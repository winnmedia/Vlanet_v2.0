"""
   
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
import logging
import os

from .models import User, EmailVerificationToken

# email_queue_manager  
try:
    from .email_queue import email_queue_manager
    #    
    if not email_queue_manager.is_running:
        email_queue_manager.start()
except Exception as e:
    logger.warning(f"Email queue manager not available: {str(e)}")
    email_queue_manager = None

logger = logging.getLogger(__name__)

class EmailVerificationService:
    """  """
    
    @staticmethod
    def send_verification_email(user):
        """   """
        try:
            #     
            EmailVerificationToken.objects.filter(
                user=user, 
                email=user.email,
                is_verified=False
            ).delete()
            
            #     (24 )
            verification_token = EmailVerificationToken.objects.create(
                user=user,
                email=user.email,
                expires_at=timezone.now() + timedelta(hours=24)
            )
            
            #   
            verification_url = f"{settings.FRONTEND_URL}/verify-email/{verification_token.token}"
            
            #  
            subject = "[VideoPlanet]    "
            
            #   (HTML) -   (  HTML)
            try:
                html_message = render_to_string('emails/email_verification_premium.html', {
                    'user_name': user.nickname or user.username,
                    'user_email': user.email,
                    'verification_url': verification_url,
                    'expires_hours': 24,
                    'site_name': 'VideoPlanet',
                    'site_url': settings.FRONTEND_URL,
                })
            except Exception:
                #    HTML 
                html_message = f"""
                <html>
                <body>
                    <h2> {user.nickname or user.username}!</h2>
                    <p>VideoPlanet  .</p>
                    <p>       :</p>
                    <p><a href="{verification_url}" style="background-color: #1631F8; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;"> </a></p>
                    <p>     :</p>
                    <p>{verification_url}</p>
                    <p>   24  .</p>
                    <br>
                    <p>.<br>VideoPlanet </p>
                </body>
                </html>
                """
            
            #   ()
            text_message = f"""
 {user.nickname or user.username}!

VideoPlanet  .

       :
{verification_url}

   24  .

.
VideoPlanet 
            """
            
            #   
            if email_queue_manager:
                #     
                email_id = email_queue_manager.add_email(
                    subject=subject,
                    body=text_message,
                    recipient_list=[user.email],
                    html_message=html_message,
                    priority=1,  #  
                    email_type='verification'
                )
                
                if email_id:
                    logger.info(f"   : {user.email} (ID: {email_id})")
                    return verification_token
                else:
                    logger.error(f"    : {user.email}")
            else:
                #     
                from django.core.mail import send_mail
                try:
                    result = send_mail(
                        subject=subject,
                        message=text_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                    if result:
                        logger.info(f"    : {user.email}")
                        return verification_token
                except Exception as send_error:
                    logger.error(f"   : {str(send_error)}")
            
            #      (  )
            return verification_token
                
        except Exception as e:
            logger.error(f"    : {str(e)}")
            return None
    
    @staticmethod
    def verify_email(token):
        """  """
        try:
            verification_token = EmailVerificationToken.objects.get(
                token=token,
                is_verified=False
            )
            
            #   
            if verification_token.is_expired():
                logger.warning(f"   : {verification_token.email}")
                return False, "  .     ."
            
            #     
            user = verification_token.user
            user.email_verified = True
            user.email_verified_at = timezone.now()
            user.save()
            
            #    
            verification_token.is_verified = True
            verification_token.verified_at = timezone.now()
            verification_token.save()
            
            logger.info(f"  : {user.email}")
            return True, "  .      ."
            
        except EmailVerificationToken.DoesNotExist:
            logger.warning(f"    : {token}")
            return False, "   ."
        except Exception as e:
            logger.error(f"    : {str(e)}")
            return False, "    .   ."
    
    @staticmethod
    def resend_verification_email(user):
        """  """
        if user.email_verified:
            return False, "    ."
        
        #      
        verification_token = EmailVerificationService.send_verification_email(user)
        
        if verification_token:
            return True, "  .   ."
        else:
            return False, "    .   ."
    
    @staticmethod
    def send_welcome_email(user):
        """      """
        try:
            subject = "[VideoPlanet]  ! "
            
            html_message = render_to_string('emails/welcome_premium.html', {
                'user_name': user.nickname or user.username,
                'user_email': user.email,
                'site_name': 'VideoPlanet',
                'site_url': settings.FRONTEND_URL,
            })
            
            text_message = f"""
 {user.nickname or user.username}!

VideoPlanet  .

      :
-     
-    
-   
-   

      !

.
VideoPlanet 
            """
            
            success = send_mail(
                subject=subject,
                message=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            if success:
                email_backend = 'SendGrid' if os.environ.get('SENDGRID_API_KEY') else 'Gmail'
                logger.info(f"{email_backend}    : {user.email}")
                return True
            else:
                logger.error(f"   : {user.email}")
                return False
                
        except Exception as e:
            logger.error(f"    : {str(e)}")
            return False