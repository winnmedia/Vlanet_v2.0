# -*- coding: utf-8 -*-
"""
  API 
-  
- ID/PW   
-  /
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
    """  """
    
    def post(self, request):
        """  """
        try:
            data = json.loads(request.body)
            email = data.get('email')
            token_type = data.get('token_type', 'email_verification')
            
            if not email:
                return JsonResponse({"message": " ."}, status=400)
            
            #   
            is_valid, error_msg = InputValidator.validate_email(email)
            if not is_valid:
                return StandardResponse.validation_error({"email": error_msg})
            
            #   
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
            return JsonResponse({"message": " JSON ."}, status=400)
        except Exception as e:
            logger.error(f"   : {str(e)}")
            return JsonResponse({"message": "    ."}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class EmailVerificationConfirmView(View):
    """  """
    
    def post(self, request):
        """  """
        try:
            data = json.loads(request.body)
            email = data.get('email')
            verification_code = data.get('verification_code')
            token_type = data.get('token_type', 'email_verification')
            
            if not email or not verification_code:
                return JsonResponse({"message": "  ."}, status=400)
            
            #   
            is_verified, message = EmailVerificationService.verify_email_code(
                email, verification_code, token_type
            )
            
            if is_verified:
                #     email_verified  
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
            return JsonResponse({"message": " JSON ."}, status=400)
        except Exception as e:
            logger.error(f"   : {str(e)}")
            return JsonResponse({"message": "    ."}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class FindUsernameView(View):
    """(ID) """
    
    def post(self, request):
        """  """
        try:
            data = json.loads(request.body)
            email = data.get('email')
            
            if not email:
                return JsonResponse({"message": " ."}, status=400)
            
            #  
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
                }, status=404 if "  " in message else 400)
                
        except json.JSONDecodeError:
            return JsonResponse({"message": " JSON ."}, status=400)
        except Exception as e:
            logger.error(f"  : {str(e)}")
            return JsonResponse({"message": "    ."}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class PasswordResetRequestView(View):
    """  """
    
    def post(self, request):
        """   """
        try:
            data = json.loads(request.body)
            email = data.get('email')
            
            if not email:
                return JsonResponse({"message": " ."}, status=400)
            
            #    
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
                }, status=404 if "  " in message else 400)
                
        except json.JSONDecodeError:
            return JsonResponse({"message": " JSON ."}, status=400)
        except Exception as e:
            logger.error(f"   : {str(e)}")
            return JsonResponse({"message": "     ."}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class PasswordResetConfirmView(View):
    """  """
    
    def post(self, request):
        """   """
        try:
            data = json.loads(request.body)
            email = data.get('email')
            verification_code = data.get('verification_code')
            new_password = data.get('new_password')
            
            if not email or not verification_code or not new_password:
                return JsonResponse({"message": "  ."}, status=400)
            
            #  
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
            return JsonResponse({"message": " JSON ."}, status=400)
        except Exception as e:
            logger.error(f"   : {str(e)}")
            return JsonResponse({"message": "    ."}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class AccountDeletionView(View):
    """ """
    
    @user_validator
    def post(self, request):
        """  """
        try:
            data = json.loads(request.body)
            reason = data.get('reason', ' ')
            confirm_password = data.get('confirm_password')
            
            user = request.user
            
            #      
            if user.login_method == 'email' and confirm_password:
                if not user.check_password(confirm_password):
                    return JsonResponse({
                        "success": False,
                        "message": "  ."
                    }, status=400)
            
            #  
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
            return JsonResponse({"message": " JSON ."}, status=400)
        except Exception as e:
            logger.error(f"  : {str(e)}")
            return JsonResponse({"message": "    ."}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class AccountRecoveryView(View):
    """ """
    
    def post(self, request):
        """  """
        try:
            data = json.loads(request.body)
            email = data.get('email')
            
            if not email:
                return JsonResponse({"message": " ."}, status=400)
            
            #  
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
                }, status=404 if "  " in message else 400)
                
        except json.JSONDecodeError:
            return JsonResponse({"message": " JSON ."}, status=400)
        except Exception as e:
            logger.error(f"  : {str(e)}")
            return JsonResponse({"message": "    ."}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class AccountStatusView(View):
    """  """
    
    def post(self, request):
        """   """
        try:
            data = json.loads(request.body)
            email = data.get('email')
            
            if not email:
                return JsonResponse({"message": " ."}, status=400)
            
            #   
            is_valid, error_msg = InputValidator.validate_email(email)
            if not is_valid:
                return StandardResponse.validation_error({"email": error_msg})
            
            #   (  )
            user = models.User.objects.filter(email=email).first()
            
            if not user:
                return JsonResponse({
                    "success": False,
                    "message": "      ."
                }, status=404)
            
            #   
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
            
            #      
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
            return JsonResponse({"message": " JSON ."}, status=400)
        except Exception as e:
            logger.error(f"   : {str(e)}")
            return JsonResponse({"message": "     ."}, status=500)