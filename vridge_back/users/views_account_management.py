# -*- coding: utf-8 -*-
"""
계정 관리 API 뷰
- 이메일 인증
- ID/PW 찾기  
- 계정 삭제/복구
"""
import logging
import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from . import models
from .utils import user_validator
from .account_management_service import (
    EmailVerificationService, 
    AccountRecoveryService, 
    AccountDeletionService
)
from .validators import InputValidator
from core.response_handler import StandardResponse

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class EmailVerificationRequestView(View):
    """이메일 인증 요청"""
    
    def post(self, request):
        """인증 이메일 발송"""
        try:
            data = json.loads(request.body)
            email = data.get('email')
            token_type = data.get('token_type', 'email_verification')
            
            if not email:
                return JsonResponse({"message": "이메일을 입력해주세요."}, status=400)
            
            # 이메일 유효성 검증
            is_valid, error_msg = InputValidator.validate_email(email)
            if not is_valid:
                return StandardResponse.validation_error({"email": error_msg})
            
            # 인증 이메일 발송
            token, message = EmailVerificationService.send_verification_email(email, token_type)
            
            if token:
                return JsonResponse({
                    "success": True,
                    "message": message,
                    "token_id": str(token.token)
                }, status=200)
            else:
                return JsonResponse({
                    "success": False,
                    "message": message
                }, status=500)
                
        except json.JSONDecodeError:
            return JsonResponse({"message": "잘못된 JSON 형식입니다."}, status=400)
        except Exception as e:
            logger.error(f"이메일 인증 요청 오류: {str(e)}")
            return JsonResponse({"message": "인증 요청 중 오류가 발생했습니다."}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class EmailVerificationConfirmView(View):
    """이메일 인증 확인"""
    
    def post(self, request):
        """인증 코드 검증"""
        try:
            data = json.loads(request.body)
            email = data.get('email')
            verification_code = data.get('verification_code')
            token_type = data.get('token_type', 'email_verification')
            
            if not email or not verification_code:
                return JsonResponse({"message": "이메일과 인증코드를 입력해주세요."}, status=400)
            
            # 인증 코드 검증
            is_verified, message = EmailVerificationService.verify_email_code(
                email, verification_code, token_type
            )
            
            if is_verified:
                # 회원가입 인증인 경우 사용자의 email_verified 플래그 업데이트
                if token_type == 'email_verification':
                    user = models.User.objects.filter(email=email, is_deleted=False).first()
                    if user and not user.email_verified:
                        user.email_verified = True
                        user.email_verified_at = timezone.now()
                        user.save()
                
                return JsonResponse({
                    "success": True,
                    "message": message
                }, status=200)
            else:
                return JsonResponse({
                    "success": False,
                    "message": message
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({"message": "잘못된 JSON 형식입니다."}, status=400)
        except Exception as e:
            logger.error(f"이메일 인증 확인 오류: {str(e)}")
            return JsonResponse({"message": "인증 확인 중 오류가 발생했습니다."}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class FindUsernameView(View):
    """사용자명(ID) 찾기"""
    
    def post(self, request):
        """이메일로 사용자명 찾기"""
        try:
            data = json.loads(request.body)
            email = data.get('email')
            
            if not email:
                return JsonResponse({"message": "이메일을 입력해주세요."}, status=400)
            
            # 사용자명 찾기
            success, message = AccountRecoveryService.find_username_by_email(email)
            
            if success:
                return JsonResponse({
                    "success": True,
                    "message": message
                }, status=200)
            else:
                return JsonResponse({
                    "success": False,
                    "message": message
                }, status=404 if "찾을 수 없습니다" in message else 400)
                
        except json.JSONDecodeError:
            return JsonResponse({"message": "잘못된 JSON 형식입니다."}, status=400)
        except Exception as e:
            logger.error(f"사용자명 찾기 오류: {str(e)}")
            return JsonResponse({"message": "사용자명 찾기 중 오류가 발생했습니다."}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class PasswordResetRequestView(View):
    """비밀번호 재설정 요청"""
    
    def post(self, request):
        """비밀번호 재설정 이메일 발송"""
        try:
            data = json.loads(request.body)
            email = data.get('email')
            
            if not email:
                return JsonResponse({"message": "이메일을 입력해주세요."}, status=400)
            
            # 비밀번호 재설정 이메일 발송
            success, message = AccountRecoveryService.send_password_reset_email(email)
            
            if success:
                return JsonResponse({
                    "success": True,
                    "message": message
                }, status=200)
            else:
                return JsonResponse({
                    "success": False,
                    "message": message
                }, status=404 if "찾을 수 없습니다" in message else 400)
                
        except json.JSONDecodeError:
            return JsonResponse({"message": "잘못된 JSON 형식입니다."}, status=400)
        except Exception as e:
            logger.error(f"비밀번호 재설정 요청 오류: {str(e)}")
            return JsonResponse({"message": "비밀번호 재설정 요청 중 오류가 발생했습니다."}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class PasswordResetConfirmView(View):
    """비밀번호 재설정 확인"""
    
    def post(self, request):
        """인증 코드로 비밀번호 재설정"""
        try:
            data = json.loads(request.body)
            email = data.get('email')
            verification_code = data.get('verification_code')
            new_password = data.get('new_password')
            
            if not email or not verification_code or not new_password:
                return JsonResponse({"message": "모든 필드를 입력해주세요."}, status=400)
            
            # 비밀번호 재설정
            success, message = AccountRecoveryService.reset_password_with_code(
                email, verification_code, new_password
            )
            
            if success:
                return JsonResponse({
                    "success": True,
                    "message": message
                }, status=200)
            else:
                return JsonResponse({
                    "success": False,
                    "message": message
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({"message": "잘못된 JSON 형식입니다."}, status=400)
        except Exception as e:
            logger.error(f"비밀번호 재설정 확인 오류: {str(e)}")
            return JsonResponse({"message": "비밀번호 재설정 중 오류가 발생했습니다."}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class AccountDeletionView(View):
    """계정 삭제"""
    
    @user_validator
    def post(self, request):
        """계정 소프트 삭제"""
        try:
            data = json.loads(request.body)
            reason = data.get('reason', '사용자 요청')
            confirm_password = data.get('confirm_password')
            
            user = request.user
            
            # 소셜 로그인 사용자는 비밀번호 확인 생략
            if user.login_method == 'email' and confirm_password:
                if not user.check_password(confirm_password):
                    return JsonResponse({
                        "success": False,
                        "message": "비밀번호가 올바르지 않습니다."
                    }, status=400)
            
            # 계정 삭제
            success, message = AccountDeletionService.soft_delete_account(user, reason)
            
            if success:
                return JsonResponse({
                    "success": True,
                    "message": message,
                    "recovery_deadline": user.recovery_deadline.isoformat() if user.recovery_deadline else None
                }, status=200)
            else:
                return JsonResponse({
                    "success": False,
                    "message": message
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({"message": "잘못된 JSON 형식입니다."}, status=400)
        except Exception as e:
            logger.error(f"계정 삭제 오류: {str(e)}")
            return JsonResponse({"message": "계정 삭제 중 오류가 발생했습니다."}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class AccountRecoveryView(View):
    """계정 복구"""
    
    def post(self, request):
        """삭제된 계정 복구"""
        try:
            data = json.loads(request.body)
            email = data.get('email')
            
            if not email:
                return JsonResponse({"message": "이메일을 입력해주세요."}, status=400)
            
            # 계정 복구
            success, message = AccountDeletionService.restore_account(email)
            
            if success:
                return JsonResponse({
                    "success": True,
                    "message": message
                }, status=200)
            else:
                return JsonResponse({
                    "success": False,
                    "message": message
                }, status=404 if "찾을 수 없습니다" in message else 400)
                
        except json.JSONDecodeError:
            return JsonResponse({"message": "잘못된 JSON 형식입니다."}, status=400)
        except Exception as e:
            logger.error(f"계정 복구 오류: {str(e)}")
            return JsonResponse({"message": "계정 복구 중 오류가 발생했습니다."}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class AccountStatusView(View):
    """계정 상태 조회"""
    
    def post(self, request):
        """이메일로 계정 상태 확인"""
        try:
            data = json.loads(request.body)
            email = data.get('email')
            
            if not email:
                return JsonResponse({"message": "이메일을 입력해주세요."}, status=400)
            
            # 이메일 유효성 검증
            is_valid, error_msg = InputValidator.validate_email(email)
            if not is_valid:
                return StandardResponse.validation_error({"email": error_msg})
            
            # 사용자 찾기 (삭제된 계정도 포함)
            user = models.User.objects.filter(email=email).first()
            
            if not user:
                return JsonResponse({
                    "success": False,
                    "message": "해당 이메일로 가입된 계정을 찾을 수 없습니다."
                }, status=404)
            
            # 계정 상태 정보
            status_info = {
                "email": user.email,
                "username": user.username,
                "nickname": user.nickname,
                "is_active": user.is_active,
                "is_deleted": user.is_deleted,
                "email_verified": user.email_verified,
                "login_method": user.login_method,
                "date_joined": user.date_joined.isoformat() if user.date_joined else None,
            }
            
            # 삭제된 계정의 경우 복구 정보 포함
            if user.is_deleted:
                status_info.update({
                    "deleted_at": user.deleted_at.isoformat() if user.deleted_at else None,
                    "deletion_reason": user.deletion_reason,
                    "can_recover": user.can_be_recovered(),
                    "recovery_deadline": user.recovery_deadline.isoformat() if user.recovery_deadline else None
                })
            
            return JsonResponse({
                "success": True,
                "account_status": status_info
            }, status=200)
                
        except json.JSONDecodeError:
            return JsonResponse({"message": "잘못된 JSON 형식입니다."}, status=400)
        except Exception as e:
            logger.error(f"계정 상태 조회 오류: {str(e)}")
            return JsonResponse({"message": "계정 상태 조회 중 오류가 발생했습니다."}, status=500)