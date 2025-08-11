"""
SendGrid  
"""
import os
import logging
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

class SendGridEmailService:
    """SendGrid    """
    
    @staticmethod
    def send_verification_email(user, verification_token):
        """   """
        try:
            #   
            verification_url = f"{settings.FRONTEND_URL}/verify-email/{verification_token.token}"
            
            # HTML  
            html_content = render_to_string('emails/email_verification_premium.html', {
                'user': user,
                'verification_url': verification_url,
                'valid_hours': 24,
                'current_year': 2025,
            })
            
            #   
            text_content = strip_tags(html_content)
            
            # SendGrid  
            result = send_mail(
                subject='[VideoPlanet]   ',
                message=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_content,
                fail_silently=False,
            )
            
            if result:
                logger.info(f"SendGrid    : {user.email}")
                return True
            else:
                logger.error(f"SendGrid    : {user.email}")
                return False
                
        except Exception as e:
            logger.error(f"SendGrid   : {str(e)}")
            return False
    
    @staticmethod
    def send_welcome_email(user):
        """     """
        try:
            # HTML  
            html_content = render_to_string('emails/welcome_email.html', {
                'user': user,
                'login_url': f"{settings.FRONTEND_URL}/login",
                'features': [
                    '  ',
                    '  ',
                    'AI   ',
                    '  '
                ],
                'current_year': 2025,
            })
            
            #   
            text_content = strip_tags(html_content)
            
            # SendGrid  
            result = send_mail(
                subject='[VideoPlanet] ! ',
                message=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_content,
                fail_silently=False,
            )
            
            if result:
                logger.info(f"SendGrid    : {user.email}")
                return True
            else:
                logger.error(f"SendGrid    : {user.email}")
                return False
                
        except Exception as e:
            logger.error(f"SendGrid    : {str(e)}")
            return False
    
    @staticmethod
    def send_password_reset_email(user, reset_code):
        """   """
        try:
            # HTML  
            html_content = render_to_string('emails/password_reset.html', {
                'user': user,
                'reset_code': reset_code,
                'valid_minutes': 30,
                'current_year': 2025,
            })
            
            #   
            text_content = f"""
VideoPlanet   

 {user.nickname or user.username},

   :

: {reset_code}

  30 .

.
VideoPlanet 
            """
            
            # SendGrid  
            result = send_mail(
                subject='[VideoPlanet]   ',
                message=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_content,
                fail_silently=False,
            )
            
            if result:
                logger.info(f"SendGrid     : {user.email}")
                return True
            else:
                logger.error(f"SendGrid     : {user.email}")
                return False
                
        except Exception as e:
            logger.error(f"SendGrid     : {str(e)}")
            return False
    
    @staticmethod
    def test_sendgrid_connection():
        """SendGrid  """
        try:
            if not os.environ.get('SENDGRID_API_KEY'):
                return False, "SendGrid API   ."
            
            #   
            result = send_mail(
                subject='[VideoPlanet] SendGrid  ',
                message='SendGrid  .',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['test@example.com'],
                fail_silently=False,
            )
            
            if result:
                return True, "SendGrid  "
            else:
                return False, "SendGrid   "
                
        except Exception as e:
            return False, f"SendGrid  : {str(e)}"