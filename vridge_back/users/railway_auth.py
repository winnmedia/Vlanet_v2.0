"""
Railway 환경 전용 안정적인 인증 핸들러
Import 에러를 방지하고 안정적인 인증 처리를 보장
"""
import logging
import json
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate
from django.conf import settings

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class RailwayLogin(View):
    """Railway 환경용 안정적인 로그인 뷰"""
    
    def post(self, request):
        try:
            # Request body 파싱
            if not request.body:
                return JsonResponse({"message": "요청 본문이 없습니다."}, status=400)
            
            try:
                data = json.loads(request.body.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.error(f"JSON 파싱 에러: {str(e)}")
                return JsonResponse({"message": "잘못된 JSON 형식입니다."}, status=400)
            
            # 로그인 정보 추출
            email = data.get("email") or data.get("username")
            password = data.get("password")
            
            if not email or not password:
                return JsonResponse({"message": "이메일과 비밀번호를 입력해주세요."}, status=400)
            
            logger.info(f"Railway 로그인 시도 - email: {email}")
            
            # 사용자 인증
            user = authenticate(request, username=email, password=password)
            
            if not user:
                # email로 재시도
                try:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    user_obj = User.objects.filter(email=email).first()
                    if user_obj:
                        user = authenticate(request, username=user_obj.username, password=password)
                except Exception as e:
                    logger.error(f"사용자 조회 에러: {e}")
            
            if user:
                # JWT 토큰 생성
                try:
                    from rest_framework_simplejwt.tokens import RefreshToken
                    refresh = RefreshToken.for_user(user)
                    access_token = str(refresh.access_token)
                    refresh_token = str(refresh)
                    
                    response_data = {
                        "message": "success",
                        "access": access_token,
                        "refresh": refresh_token,
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "user": {
                            "id": user.id,
                            "username": user.username,
                            "email": getattr(user, 'email', ''),
                            "nickname": getattr(user, 'nickname', user.username)
                        }
                    }
                    
                    res = JsonResponse(response_data, status=200)
                    
                    # 쿠키 설정 (Railway는 HTTPS)
                    res.set_cookie(
                        "vridge_session",
                        access_token,
                        httponly=True,
                        samesite="Lax",
                        secure=True,
                        max_age=2419200,
                    )
                    return res
                    
                except Exception as e:
                    logger.error(f"JWT 토큰 생성 에러: {e}")
                    return JsonResponse({
                        "message": "로그인 성공했지만 토큰 생성에 실패했습니다.",
                        "error": str(e)
                    }, status=500)
            else:
                logger.warning(f"로그인 실패: {email}")
                return JsonResponse({"message": "이메일 또는 비밀번호가 올바르지 않습니다."}, status=401)
                
        except Exception as e:
            logger.error(f"Railway 로그인 에러: {str(e)}", exc_info=True)
            return JsonResponse({
                "message": "로그인 처리 중 오류가 발생했습니다.",
                "error": str(e) if settings.DEBUG else "Internal server error"
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class RailwaySignup(View):
    """Railway 환경용 안정적인 회원가입 뷰"""
    
    def post(self, request):
        try:
            # Request body 파싱
            if not request.body:
                return JsonResponse({"message": "요청 본문이 없습니다."}, status=400)
            
            try:
                data = json.loads(request.body.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.error(f"JSON 파싱 에러: {str(e)}")
                return JsonResponse({"message": "잘못된 JSON 형식입니다."}, status=400)
            
            email = data.get("email")
            nickname = data.get("nickname")
            password = data.get("password")
            
            # 필수 필드 검증
            if not email or not nickname or not password:
                return JsonResponse({"message": "모든 필드를 입력해주세요."}, status=400)
            
            # 이메일 형식 검증
            import re
            email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
            if not email_regex.match(email):
                return JsonResponse({"message": "올바른 이메일 형식이 아닙니다."}, status=400)
            
            # 비밀번호 길이 검증
            if len(password) < 8:
                return JsonResponse({"message": "비밀번호는 최소 8자 이상이어야 합니다."}, status=400)
            
            # 닉네임 길이 검증
            if len(nickname) < 2:
                return JsonResponse({"message": "닉네임은 최소 2자 이상이어야 합니다."}, status=400)
            
            logger.info(f"Railway 회원가입 시도 - 이메일: {email}, 닉네임: {nickname}")
            
            # User 모델 가져오기
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # 중복 체크
            if User.objects.filter(username=email).exists():
                return JsonResponse({"message": "이미 사용중인 이메일입니다."}, status=409)
            
            if hasattr(User, 'nickname'):
                if User.objects.filter(nickname=nickname).exists():
                    return JsonResponse({"message": "이미 사용중인 닉네임입니다."}, status=409)
            
            # 사용자 생성
            try:
                new_user = User(
                    username=email,
                    email=email
                )
                
                # nickname 필드가 있으면 설정
                if hasattr(User, 'nickname'):
                    new_user.nickname = nickname
                
                # login_method 필드가 있으면 설정
                if hasattr(User, 'login_method'):
                    new_user.login_method = 'email'
                
                # 비밀번호 설정
                new_user.set_password(password)
                
                # Railway 환경에서는 이메일 인증 자동 완료
                if hasattr(User, 'email_verified'):
                    new_user.email_verified = True
                    logger.info(f"Railway 환경 - 이메일 자동 인증: {email}")
                
                new_user.save()
                
                logger.info(f"Railway 회원가입 성공 - ID: {new_user.id}, 이메일: {new_user.username}")
                
                return JsonResponse({
                    "message": "회원가입이 완료되었습니다.",
                    "email_sent": False,
                    "user": new_user.username,
                    "nickname": nickname,
                    "auto_verified": True
                }, status=201)
                
            except Exception as e:
                logger.error(f"사용자 생성 에러: {e}")
                return JsonResponse({
                    "message": "회원가입 처리 중 오류가 발생했습니다.",
                    "error": str(e) if settings.DEBUG else "Internal server error"
                }, status=500)
                
        except Exception as e:
            logger.error(f"Railway 회원가입 에러: {str(e)}", exc_info=True)
            return JsonResponse({
                "message": "회원가입 처리 중 오류가 발생했습니다.",
                "error": str(e) if settings.DEBUG else "Internal server error"
            }, status=500)