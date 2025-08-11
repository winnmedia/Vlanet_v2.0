# -*- coding: utf-8 -*-
"""
   
-  
- ID/PW 
-  /
"""
import logging
import random
import string
import uuid
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from . import models
from .validators import InputValidator

logger = logging.getLogger(__name__)


class AccountManagementService:
    """   """

    @staticmethod
    def generate_verification_code(length=6):
        """  """
        return ''.join(random.choices(string.digits, k=length))

    @staticmethod
    def generate_temp_password(length=12):
        """  """
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choices(chars, k=length))

    @staticmethod
    def send_email(subject, body, to_email, html_message=None):
        """   """
        try:
            email = EmailMultiAlternatives(
                subject=subject,
                body=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[to_email]
            )
            if html_message:
                email.attach_alternative(html_message, "text/html")
            
            result = email.send()
            logger.info(f"  : {to_email}")
            return result > 0
        except Exception as e:
            logger.error(f"   ({to_email}): {str(e)}")
            return False


class EmailVerificationService(AccountManagementService):
    """  """

    @classmethod
    def send_verification_email(cls, user_email, token_type='email_verification'):
        """  """
        try:
            #    
            models.EmailVerificationToken.objects.filter(
                email=user_email,
                token_type=token_type,
                is_verified=False
            ).delete()

            #   
            verification_code = cls.generate_verification_code()
            token = models.EmailVerificationToken.objects.create(
                email=user_email,
                token_type=token_type,
                verification_code=verification_code,
                expires_at=timezone.now() + timedelta(minutes=10)
            )

            #  
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>VideoPlanet  </title>
            </head>
            <body style="font-family: Arial, sans-serif; padding: 20px; margin: 0; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background: #ffffff; padding: 40px; border-radius: 10px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #1631F8; margin: 0; font-size: 32px;">VideoPlanet</h1>
                        <p style="color: #666; margin-top: 10px; font-size: 18px;"> </p>
                    </div>
                    
                    <div style="background: #f9f9f9; padding: 30px; border-radius: 8px; text-align: center;">
                        <p style="font-size: 16px; color: #333; margin-bottom: 20px;">
                               :
                        </p>
                        
                        <div style="background: #1631F8; color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <span style="font-size: 36px; font-weight: bold; letter-spacing: 8px;">{verification_code}</span>
                        </div>
                        
                        <p style="font-size: 14px; color: #666; margin-top: 20px;">
                               10 .
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """

            success = cls.send_email(
                subject="VideoPlanet  ",
                body=strip_tags(html_message),
                to_email=user_email,
                html_message=html_message
            )

            return (token, "  .") if success else (None, "  .")

        except Exception as e:
            logger.error(f"   : {str(e)}")
            return None, "     ."

    @classmethod
    def verify_email_code(cls, email, verification_code, token_type='email_verification'):
        """   """
        try:
            token = models.EmailVerificationToken.objects.filter(
                email=email,
                token_type=token_type,
                verification_code=verification_code,
                is_verified=False
            ).first()

            if not token:
                return False, "  ."

            if token.is_expired():
                return False, "  ."

            if token.is_max_attempts_reached():
                return False, "   ."

            #  
            token.is_verified = True
            token.verified_at = timezone.now()
            token.save()

            return True, "  ."

        except Exception as e:
            logger.error(f"   : {str(e)}")
            return False, "    ."


class AccountRecoveryService(AccountManagementService):
    """ID/PW  """

    @classmethod
    def find_username_by_email(cls, email):
        """  """
        try:
            #   
            is_valid, error_msg = InputValidator.validate_email(email)
            if not is_valid:
                return False, error_msg

            #   (  )
            user = models.User.objects.filter(
                email=email,
                is_deleted=False,
                login_method='email'
            ).first()

            if not user:
                return False, "      ."

            # ID   
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>VideoPlanet ID </title>
            </head>
            <body style="font-family: Arial, sans-serif; padding: 20px; margin: 0; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background: #ffffff; padding: 40px; border-radius: 10px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #1631F8; margin: 0; font-size: 32px;">VideoPlanet</h1>
                        <p style="color: #666; margin-top: 10px; font-size: 18px;">ID </p>
                    </div>
                    
                    <div style="background: #f9f9f9; padding: 30px; border-radius: 8px;">
                        <p style="font-size: 16px; color: #333; margin-bottom: 20px;">
                              :
                        </p>
                        
                        <div style="background: #1631F8; color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <p style="margin: 0; font-size: 16px;">()</p>
                            <p style="margin: 10px 0 0 0; font-size: 24px; font-weight: bold;">{user.username}</p>
                        </div>
                        
                        <p style="font-size: 14px; color: #666; margin-top: 20px;">
                            : {user.date_joined.strftime('%Y %m %d')}
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """

            success = cls.send_email(
                subject="VideoPlanet ID  ",
                body=strip_tags(html_message),
                to_email=email,
                html_message=html_message
            )

            return success, "   ." if success else "  ."

        except Exception as e:
            logger.error(f"ID  : {str(e)}")
            return False, "ID    ."

    @classmethod
    def send_password_reset_email(cls, email):
        """   """
        try:
            #   
            is_valid, error_msg = InputValidator.validate_email(email)
            if not is_valid:
                return False, error_msg

            #   (  )
            user = models.User.objects.filter(
                email=email,
                is_deleted=False,
                login_method='email'
            ).first()

            if not user:
                return False, "      ."

            #   
            token, message = EmailVerificationService.send_verification_email(
                email, 'password_reset'
            )

            if not token:
                return False, message

            return True, "    ."

        except Exception as e:
            logger.error(f"    : {str(e)}")
            return False, "    ."

    @classmethod
    def reset_password_with_code(cls, email, verification_code, new_password):
        """   """
        try:
            #   
            is_verified, message = EmailVerificationService.verify_email_code(
                email, verification_code, 'password_reset'
            )

            if not is_verified:
                return False, message

            #  
            user = models.User.objects.filter(
                email=email,
                is_deleted=False,
                login_method='email'
            ).first()

            if not user:
                return False, "   ."

            #   
            is_valid, error_msg = InputValidator.validate_password(new_password)
            if not is_valid:
                return False, error_msg

            #  
            user.set_password(new_password)
            user.save()

            logger.info(f"  : {user.email}")
            return True, "  ."

        except Exception as e:
            logger.error(f"  : {str(e)}")
            return False, "    ."


class AccountDeletionService(AccountManagementService):
    """ / """

    @classmethod
    def soft_delete_account(cls, user, reason=" "):
        """  """
        try:
            #    
            if user.is_deleted:
                return False, "  ."

            #   
            user.soft_delete(reason)

            #    
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>VideoPlanet  </title>
            </head>
            <body style="font-family: Arial, sans-serif; padding: 20px; margin: 0; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background: #ffffff; padding: 40px; border-radius: 10px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #1631F8; margin: 0; font-size: 32px;">VideoPlanet</h1>
                        <p style="color: #666; margin-top: 10px; font-size: 18px;">  </p>
                    </div>
                    
                    <div style="background: #f9f9f9; padding: 30px; border-radius: 8px;">
                        <p style="font-size: 16px; color: #333; margin-bottom: 20px;">
                            , {user.nickname or user.username}.
                        </p>
                        <p style="font-size: 16px; color: #333; margin-bottom: 20px;">
                               .
                        </p>
                        
                        <div style="border: 2px solid #ff6b6b; padding: 20px; border-radius: 8px; margin: 20px 0; background: #ffe0e0;">
                            <p style="margin: 0; font-size: 14px; color: #d63031;">
                                <strong>:</strong>  30   .
                            </p>
                            <p style="margin: 10px 0 0 0; font-size: 14px; color: #d63031;">
                                 : {user.recovery_deadline.strftime('%Y %m %d')}
                            </p>
                        </div>
                        
                        <p style="font-size: 14px; color: #666; margin-top: 20px;">
                                .
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """

            cls.send_email(
                subject="VideoPlanet   ",
                body=strip_tags(html_message),
                to_email=user.email,
                html_message=html_message
            )

            logger.info(f"   : {user.email}")
            return True, " . 30   ."

        except Exception as e:
            logger.error(f"  : {str(e)}")
            return False, "    ."

    @classmethod
    def restore_account(cls, email):
        """ """
        try:
            #   
            user = models.User.objects.filter(
                email=email,
                is_deleted=True
            ).first()

            if not user:
                return False, "    ."

            if not user.can_be_recovered():
                return False, "      ."

            #  
            user.restore_account()

            #    
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>VideoPlanet  </title>
            </head>
            <body style="font-family: Arial, sans-serif; padding: 20px; margin: 0; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background: #ffffff; padding: 40px; border-radius: 10px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #1631F8; margin: 0; font-size: 32px;">VideoPlanet</h1>
                        <p style="color: #666; margin-top: 10px; font-size: 18px;">  </p>
                    </div>
                    
                    <div style="background: #f9f9f9; padding: 30px; border-radius: 8px;">
                        <p style="font-size: 16px; color: #333; margin-bottom: 20px;">
                            , {user.nickname or user.username}.
                        </p>
                        <p style="font-size: 16px; color: #333; margin-bottom: 20px;">
                              .
                        </p>
                        
                        <div style="background: #00b894; color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <p style="margin: 0; font-size: 18px; font-weight: bold; text-align: center;">
                                    !
                            </p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """

            cls.send_email(
                subject="VideoPlanet   ",
                body=strip_tags(html_message),
                to_email=user.email,
                html_message=html_message
            )

            logger.info(f"  : {user.email}")
            return True, "  ."

        except Exception as e:
            logger.error(f"  : {str(e)}")
            return False, "    ."