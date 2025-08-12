"""
Railway 프로덕션 환경 로그인 500 에러 해결
Victoria - DBRE (Database Reliability Engineer)

Railway 환경에서 발생하는 데이터베이스 연결 및 로그인 관련 500 에러를 해결하는 뷰
"""

import logging
import time
import traceback
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import AnonymousUser
from django.db import transaction, connection
from django.db.utils import OperationalError, DatabaseError
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User
import json

# Railway 전용 로거 설정
logger = logging.getLogger('railway_login')

def check_database_connection():
    """데이터베이스 연결 상태 확인"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            return True
    except (OperationalError, DatabaseError) as e:
        logger.error(f"데이터베이스 연결 실패: {e}")
        return False

def safe_database_operation(operation, max_retries=3):
    """데이터베이스 작업을 안전하게 실행"""
    for attempt in range(max_retries):
        try:
            return operation()
        except (OperationalError, DatabaseError) as e:
            logger.warning(f"데이터베이스 작업 실패 (시도 {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(0.5 * (attempt + 1))  # 지수 백오프
    return None

@api_view(['POST'])
@permission_classes([AllowAny])
def railway_login_view(request):
    """Railway 환경에 최적화된 로그인 뷰"""
    
    logger.info(f"로그인 요청 시작 - IP: {request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))}")
    
    try:
        # 1. 요청 데이터 검증
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({
                    'error': '잘못된 JSON 형식입니다',
                    'code': 'INVALID_JSON'
                }, status=400)
        else:
            data = request.POST
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # 필드 검증
        if not email:
            return JsonResponse({
                'error': '이메일을 입력해주세요',
                'code': 'EMAIL_REQUIRED'
            }, status=400)
        
        if not password:
            return JsonResponse({
                'error': '비밀번호를 입력해주세요',
                'code': 'PASSWORD_REQUIRED'
            }, status=400)
        
        # 2. 데이터베이스 연결 확인
        if not check_database_connection():
            logger.error("데이터베이스 연결 실패")
            return JsonResponse({
                'error': '서버 연결에 문제가 있습니다. 잠시 후 다시 시도해주세요.',
                'code': 'DATABASE_CONNECTION_ERROR'
            }, status=503)
        
        # 3. 사용자 조회 (안전한 데이터베이스 작업)
        def get_user_operation():
            try:
                user = User.objects.get(email=email)
                logger.info(f"사용자 조회 성공 - ID: {user.id}, Email: {user.email}")
                return user
            except User.DoesNotExist:
                logger.warning(f"사용자 조회 실패 - 존재하지 않는 이메일: {email}")
                return None
        
        user = safe_database_operation(get_user_operation)
        
        if user is None:
            return JsonResponse({
                'error': '이메일 또는 비밀번호가 올바르지 않습니다',
                'code': 'INVALID_CREDENTIALS'
            }, status=401)
        
        # 4. 사용자 상태 확인
        if not user.is_active:
            logger.warning(f"비활성 사용자 로그인 시도 - ID: {user.id}")
            return JsonResponse({
                'error': '비활성화된 계정입니다. 관리자에게 문의하세요.',
                'code': 'ACCOUNT_INACTIVE'
            }, status=401)
        
        # 소프트 삭제된 사용자 확인
        if getattr(user, 'is_deleted', False):
            logger.warning(f"삭제된 사용자 로그인 시도 - ID: {user.id}")
            return JsonResponse({
                'error': '삭제된 계정입니다.',
                'code': 'ACCOUNT_DELETED'
            }, status=401)
        
        # 5. 비밀번호 확인 (Django의 authenticate 사용)
        def authenticate_operation():
            authenticated_user = authenticate(request, username=email, password=password)
            return authenticated_user
        
        authenticated_user = safe_database_operation(authenticate_operation)
        
        if not authenticated_user:
            logger.warning(f"인증 실패 - Email: {email}")
            return JsonResponse({
                'error': '이메일 또는 비밀번호가 올바르지 않습니다',
                'code': 'INVALID_CREDENTIALS'
            }, status=401)
        
        # 6. JWT 토큰 생성
        try:
            refresh = RefreshToken.for_user(authenticated_user)
            access_token = refresh.access_token
            
            logger.info(f"JWT 토큰 생성 성공 - 사용자 ID: {authenticated_user.id}")
            
        except Exception as e:
            logger.error(f"JWT 토큰 생성 실패: {e}")
            return JsonResponse({
                'error': '토큰 생성 중 오류가 발생했습니다',
                'code': 'TOKEN_GENERATION_ERROR'
            }, status=500)
        
        # 7. 로그인 세션 처리
        try:
            login(request, authenticated_user)
            logger.info(f"세션 로그인 성공 - 사용자 ID: {authenticated_user.id}")
        except Exception as e:
            logger.warning(f"세션 로그인 실패 (JWT는 성공): {e}")
            # JWT가 있으므로 계속 진행
        
        # 8. 로그인 시간 업데이트 (선택적)
        def update_last_login():
            try:
                authenticated_user.last_login = datetime.now()
                authenticated_user.save(update_fields=['last_login'])
                return True
            except Exception as e:
                logger.warning(f"last_login 업데이트 실패: {e}")
                return False
        
        safe_database_operation(update_last_login)
        
        # 9. 성공 응답
        response_data = {
            'message': '로그인 성공',
            'user': {
                'id': authenticated_user.id,
                'email': authenticated_user.email,
                'username': authenticated_user.username,
                'first_name': authenticated_user.first_name or '',
                'last_name': authenticated_user.last_name or '',
                'is_active': authenticated_user.is_active,
                'last_login': authenticated_user.last_login.isoformat() if authenticated_user.last_login else None
            },
            'tokens': {
                'access': str(access_token),
                'refresh': str(refresh)
            }
        }
        
        logger.info(f"로그인 완료 - 사용자 ID: {authenticated_user.id}")
        
        return JsonResponse(response_data, status=200)
        
    except Exception as e:
        # 예상치 못한 오류 처리
        logger.error(f"로그인 처리 중 예상치 못한 오류: {e}")
        logger.error(traceback.format_exc())
        
        return JsonResponse({
            'error': '서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요.',
            'code': 'INTERNAL_SERVER_ERROR',
            'timestamp': datetime.now().isoformat()
        }, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def railway_health_check(request):
    """Railway용 헬스체크 엔드포인트"""
    
    health_data = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'vridge-backend',
        'environment': 'railway'
    }
    
    try:
        # 데이터베이스 연결 테스트
        db_healthy = check_database_connection()
        health_data['database'] = 'healthy' if db_healthy else 'unhealthy'
        
        if db_healthy:
            # 사용자 테이블 확인
            try:
                user_count = User.objects.count()
                health_data['users_count'] = user_count
                health_data['database_details'] = 'users_table_accessible'
            except Exception as e:
                health_data['database'] = 'unhealthy'
                health_data['database_error'] = str(e)
        
        # 전체 상태 결정
        if health_data['database'] != 'healthy':
            health_data['status'] = 'unhealthy'
            return JsonResponse(health_data, status=503)
        
        return JsonResponse(health_data, status=200)
        
    except Exception as e:
        logger.error(f"헬스체크 실패: {e}")
        return JsonResponse({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }, status=503)

@api_view(['GET'])
@permission_classes([AllowAny])
def railway_status_check(request):
    """Railway 배포 상태 확인"""
    
    try:
        # 환경 변수 확인
        import os
        env_vars = {
            'DATABASE_URL': bool(os.environ.get('DATABASE_URL')),
            'DJANGO_SETTINGS_MODULE': os.environ.get('DJANGO_SETTINGS_MODULE'),
            'DEBUG': os.environ.get('DEBUG', 'False'),
            'SECRET_KEY': bool(os.environ.get('SECRET_KEY')),
        }
        
        # Django 설정 확인
        from django.conf import settings
        
        status_data = {
            'timestamp': datetime.now().isoformat(),
            'django_version': settings.DJANGO_VERSION if hasattr(settings, 'DJANGO_VERSION') else 'unknown',
            'debug_mode': settings.DEBUG,
            'allowed_hosts': settings.ALLOWED_HOSTS,
            'database_engine': settings.DATABASES['default']['ENGINE'],
            'environment_vars': env_vars,
            'apps_installed': len(settings.INSTALLED_APPS),
        }
        
        return JsonResponse(status_data, status=200)
        
    except Exception as e:
        logger.error(f"상태 확인 실패: {e}")
        return JsonResponse({
            'error': '상태 확인 중 오류 발생',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def railway_test_login(request):
    """Railway 테스트용 간단한 로그인"""
    
    try:
        # 기본 테스트 사용자로 로그인 시도
        test_email = 'demo@test.com'
        test_password = '123456'  # 또는 demo123456
        
        logger.info(f"테스트 로그인 시도 - {test_email}")
        
        # 사용자 확인
        try:
            user = User.objects.get(email=test_email)
            logger.info(f"테스트 사용자 발견 - ID: {user.id}")
        except User.DoesNotExist:
            return JsonResponse({
                'error': '테스트 사용자가 존재하지 않습니다',
                'email': test_email
            }, status=404)
        
        # 인증 시도
        authenticated_user = authenticate(username=test_email, password=test_password)
        
        if authenticated_user:
            # JWT 토큰 생성
            refresh = RefreshToken.for_user(authenticated_user)
            access_token = refresh.access_token
            
            return JsonResponse({
                'message': '테스트 로그인 성공',
                'user_id': authenticated_user.id,
                'email': authenticated_user.email,
                'tokens': {
                    'access': str(access_token),
                    'refresh': str(refresh)
                }
            }, status=200)
        else:
            return JsonResponse({
                'error': '테스트 사용자 인증 실패',
                'email': test_email
            }, status=401)
            
    except Exception as e:
        logger.error(f"테스트 로그인 오류: {e}")
        return JsonResponse({
            'error': '테스트 로그인 중 오류 발생',
            'details': str(e)
        }, status=500)