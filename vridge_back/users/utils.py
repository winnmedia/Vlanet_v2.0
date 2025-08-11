import os
import threading
from django.conf import settings
from django.http import JsonResponse
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
try:
    from .jwt_compatibility import CompatibleJWTAuthentication as JWTAuthentication
except ImportError:
    from rest_framework_simplejwt.authentication import JWTAuthentication
from . import models
from projects import models as project_model

from django.core.mail import EmailMessage, send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

#    import
try:
    from .email_queue import email_queue_manager
    USE_EMAIL_QUEUE = True
except ImportError:
    USE_EMAIL_QUEUE = False


def user_validator(function):
    def wrapper(self, request, *args, **kwargs):
        try:
            # Debug logging
            print(f"[Auth Debug] Request method: {request.method}")
            print(f"[Auth Debug] Auth header: {request.META.get('HTTP_AUTHORIZATION', 'No auth header')}")
            print(f"[Auth Debug] Content-Type: {request.content_type}")
            print(f"[Auth Debug] User before auth: {request.user}")
            
            # TEMPORARY DEBUG MODE - REMOVE AFTER FIXING
            if os.environ.get('JWT_DEBUG_MODE') == 'true':
                print("[Auth Debug] JWT_DEBUG_MODE enabled - bypassing authentication")
                #   
                try:
                    test_user = models.User.objects.first()
                    if test_user:
                        request.user = test_user
                        print(f"[Auth Debug] Using test user: {test_user.username}")
                        return function(self, request, *args, **kwargs)
                except Exception as e:
                    print(f"[Auth Debug] Failed to get test user: {e}")
            
            # Use Django REST Framework's JWT authentication
            jwt_auth = JWTAuthentication()
            
            try:
                # This will validate the token and return (user, token)
                auth_result = jwt_auth.authenticate(request)
                print(f"[Auth Debug] JWT auth result: {auth_result}")
                if auth_result is not None:
                    user, token = auth_result
                    if user:
                        request.user = user
                        print(f"[Auth Debug] Authenticated user: {request.user}")
                        return function(self, request, *args, **kwargs)
                
                # Fallback to cookie if header auth fails
                vridge_session = request.COOKIES.get("vridge_session", None)
                if vridge_session:
                    # Create a fake request with the token in header
                    class FakeRequest:
                        def __init__(self, token):
                            self.META = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
                    
                    fake_request = FakeRequest(vridge_session)
                    auth_result = jwt_auth.authenticate(fake_request)
                    if auth_result is not None:
                        user, token = auth_result
                        if user:
                            request.user = user
                            print("request.user", request.user)
                            return function(self, request, *args, **kwargs)
                
                response = JsonResponse({"message": "NEED_ACCESS_TOKEN"}, status=401)
                response['WWW-Authenticate'] = 'Bearer'
                return response
                    
            except (InvalidToken, TokenError) as e:
                print(f"Token validation error: {e}")
                response = JsonResponse({"message": "INVALID_TOKEN"}, status=401)
                response['WWW-Authenticate'] = 'Bearer'
                return response
                
        except Exception as e:
            import traceback
            print(f"Authentication error: {e}")
            print(f"Error type: {type(e).__name__}")
            print(f"Error traceback: {traceback.format_exc()}")
            response = JsonResponse({"message": "AUTHENTICATION_ERROR", "detail": str(e)}, status=401)
            response['WWW-Authenticate'] = 'Bearer'
            return response

    return wrapper


class EmailThread(threading.Thread):
    def __init__(self, subject, body, recipient_list, html_message):
        self.subject = subject
        self.body = body
        self.recipient_list = recipient_list
        self.fail_silently = False
        self.html_message = html_message
        threading.Thread.__init__(self)

    def run(self):
        try:
            from django.conf import settings
            print(f"[Email] Attempting to send email to {self.recipient_list}")
            print(f"[Email] EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
            print(f"[Email] EMAIL_HOST: {settings.EMAIL_HOST}")
            print(f"[Email] EMAIL_PORT: {settings.EMAIL_PORT}")
            print(f"[Email] EMAIL_HOST_USER: {settings.EMAIL_HOST_USER[:3]}..." if settings.EMAIL_HOST_USER else "[Email] EMAIL_HOST_USER: Not set")
            
            email = EmailMultiAlternatives(
                subject=self.subject, 
                body=self.body, 
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=self.recipient_list
            )
            if self.html_message:
                email.attach_alternative(self.html_message, "text/html")
            result = email.send(self.fail_silently)
            email_backend = 'SendGrid' if os.environ.get('SENDGRID_API_KEY') else 'Gmail'
            print(f"[Email] Email sent successfully via {email_backend} to {self.recipient_list}. Result: {result}")
        except Exception as e:
            print(f"[Email] Failed to send email to {self.recipient_list}: {str(e)}")
            import traceback
            traceback.print_exc()


def auth_send_email(request, email, secret):
    """   """
    try:
        #   
        print(f"[Email] Sending auth email to: {email}")
        print(f"[Email] Auth number: {secret}")
        
        #       
        if settings.EMAIL_BACKEND != 'django.core.mail.backends.console.EmailBackend':
            if os.environ.get('SENDGRID_API_KEY'):
                print("[Email] Using SendGrid for email")
            elif settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:
                print("[Email] Using Gmail for email")
            else:
                print("[Email] ERROR: No email credentials configured")
                return False
        
        # HTML      HTML 
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>VideoPlanet </title>
        </head>
        <body style="font-family: Arial, sans-serif; padding: 20px; margin: 0; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background: #ffffff; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #1631F8; margin: 0; font-size: 32px;">VideoPlanet</h1>
                    <p style="color: #666; margin-top: 10px; font-size: 18px;"> </p>
                </div>
                
                <div style="background: #f9f9f9; padding: 30px; border-radius: 8px; text-align: center;">
                    <p style="font-size: 16px; color: #333; margin-bottom: 20px;">
                            :
                    </p>
                    
                    <div style="background: #1631F8; color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <span style="font-size: 36px; font-weight: bold; letter-spacing: 8px;">{secret}</span>
                    </div>
                    
                    <p style="font-size: 14px; color: #666; margin-top: 20px;">
                          3 .
                    </p>
                </div>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center;">
                    <p style="font-size: 12px; color: #999; margin: 0;">
                          VideoPlanet   .
                    </p>
                    <p style="font-size: 12px; color: #999; margin: 5px 0;">
                           ,    .
                    </p>
                    <p style="font-size: 12px; color: #999; margin: 5px 0;">
                        © 2024 VideoPlanet. All rights reserved.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        try:
            # verify_email.html   
            html_message = render_to_string("verify_email.html", {"secret": secret})
        except:
            #     HTML 
            pass
        
        to = [email]
        
        #    ( )
        if USE_EMAIL_QUEUE:
            email_queue_manager.add_email(
                "VideoPlanet ", 
                strip_tags(html_message), 
                to, 
                html_message,
                priority=1  #    
            )
        else:
            #   
            EmailThread("VideoPlanet ", strip_tags(html_message), to, html_message).start()
        
        email_backend = 'SendGrid' if os.environ.get('SENDGRID_API_KEY') else 'Gmail'
        print(f"[Email] Auth email queued for sending via {email_backend}")
        return True
        
    except Exception as e:
        print(f"[Email] Error in auth_send_email: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def invite_send_email(request, email, uid, token, name):
    """    ( )"""
    try:
        print(f"[Invite Email] Legacy invite email function called for: {email} for project: {name}")
        print(f"[Invite Email] This function is deprecated. Use ProjectInvitationEmailService instead.")
        
        #    ProjectInvitation  
        #       
        
        #   
        if settings.EMAIL_BACKEND != 'django.core.mail.backends.console.EmailBackend':
            if os.environ.get('SENDGRID_API_KEY'):
                print(f"[Invite Email] Using SendGrid for email (API Key present: {bool(os.environ.get('SENDGRID_API_KEY'))})")
            elif getattr(settings, 'EMAIL_HOST_USER', None) and getattr(settings, 'EMAIL_HOST_PASSWORD', None):
                print(f"[Invite Email] Using Gmail for email (Credentials present)")
            else:
                print("[Invite Email] ERROR: No email credentials configured")
                return False
        
        # URL  -     
        if settings.DEBUG:
            base_url = "http://localhost:3000"
        else:
            base_url = "https://vlanet.net"
        
        #   : /invitation/{token}  URL 
        url = f"{base_url}/invitation/{token}"
        
        # HTML  
        try:
            html_message = render_to_string(
                "invite_email.html",
                {
                    "uid": uid,
                    "token": token,
                    "url": url,
                    "scheme": request.scheme,
                    "domain": request.META.get("HTTP_HOST", "vlanet.net"),
                    "name": name,
                },
            )
        except Exception as e:
            print(f"[Invite Email] Template rendering failed: {str(e)}")
            #      HTML
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>VideoPlanet  </title>
            </head>
            <body style="font-family: Arial, sans-serif; padding: 20px; margin: 0; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background: #ffffff; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #1631F8; margin: 0; font-size: 32px;">VideoPlanet</h1>
                        <p style="color: #666; margin-top: 10px; font-size: 18px;"> </p>
                    </div>
                    
                    <div style="background: #f9f9f9; padding: 30px; border-radius: 8px;">
                        <h3 style="font-size: 24px; margin-bottom: 20px;">'{name}'  !</h3>
                        <p style="font-size: 16px; color: #333; margin-bottom: 20px;">
                                .
                        </p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{url}" 
                               style="display: inline-block; padding: 15px 30px; background: #1631F8; color: white; text-decoration: none; border-radius: 5px; font-size: 16px; font-weight: bold;">
                                 
                            </a>
                        </div>
                    </div>
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center;">
                        <p style="font-size: 12px; color: #999; margin: 0;">
                              VideoPlanet    .
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
        
        to = [email]
        subject = f"VideoPlanet '{name}'  "
        
        #  
        if USE_EMAIL_QUEUE:
            email_queue_manager.add_email(
                subject,
                strip_tags(html_message),
                to,
                html_message,
                priority=3  #    
            )
        else:
            #   
            EmailThread(subject, strip_tags(html_message), to, html_message).start()
        
        email_backend = 'SendGrid' if os.environ.get('SENDGRID_API_KEY') else 'Gmail'
        print(f"[Invite Email] Legacy invite email queued for sending via {email_backend}")
        return True
        
    except Exception as e:
        print(f"[Invite Email] Error in invite_send_email: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


# request.Meta
# CONTENT_LENGTH–   ().
# CONTENT_TYPE–   MIME .
# HTTP_ACCEPT–    .
# HTTP_ACCEPT_ENCODING–   .
# HTTP_ACCEPT_LANGUAGE–   .
# HTTP_HOST–   HTTP  .
# HTTP_REFERER–  ( ).
# HTTP_USER_AGENT–    .
# QUERY_STRING–   ( ) .
# REMOTE_ADDR–  IP .
# REMOTE_HOST–   .
# REMOTE_USER–    ( ).
# REQUEST_METHOD"GET"–     "POST".
# SERVER_NAME–   .
# SERVER_PORT–  ().

from django.contrib.auth.tokens import default_token_generator  #    
from django.utils.crypto import salted_hmac, constant_time_compare
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str


def project_token_generator(project):
    value = (
        f"{project.id}{project.user.id}{project.user.username}{project.user.password}"
    )
    token = salted_hmac(
        "django.winnmedia.virege.project.inviteToken",
        value,
        secret=settings.SECRET_KEY,
    ).hexdigest()[::2]
    return token


def check_project_token(project, token):
    if not (project and token):
        return False
    return constant_time_compare(project_token_generator(project), token)
