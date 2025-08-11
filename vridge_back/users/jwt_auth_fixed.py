"""
 JWT   - 2025  
        
"""

import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.exceptions import AuthenticationFailed

logger = logging.getLogger(__name__)
User = get_user_model()


class EnhancedJWTAuthentication(JWTAuthentication):
    """
     JWT  
    - username/email   
    -   
    -    
    """
    
    def authenticate(self, request):
        """  """
        header = self.get_header(request)
        if header is None:
            return None
            
        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None
        
        #  
        validated_token = self.get_validated_token(raw_token)
        
        #  
        user = self.get_user(validated_token)
        
        return user, validated_token
    
    def get_validated_token(self, raw_token):
        """   """
        messages = []
        
        try:
            # AccessToken  
            token = AccessToken(raw_token)
            
            #   
            token_type = token.get('token_type', None)
            if token_type and token_type != 'access':
                raise TokenError(f"Invalid token type: {token_type}")
            
            #  ID 
            user_id = token.get('user_id', None)
            if not user_id:
                raise TokenError("Token missing user_id")
            
            logger.debug(f"Token validated for user_id: {user_id}")
            return token
            
        except TokenError as e:
            messages.append({
                'token_class': 'AccessToken',
                'token_type': 'access',
                'message': str(e)
            })
            
            # RefreshToken  ()
            try:
                token = RefreshToken(raw_token)
                logger.warning("Access token used as refresh token - security risk!")
                raise InvalidToken({
                    'detail': 'Wrong token type. Use access token for authentication.',
                    'messages': messages
                })
            except TokenError:
                pass
        
        #   
        raise InvalidToken({
            'detail': '   .',
            'code': 'token_not_valid',
            'messages': messages
        })
    
    def get_user(self, validated_token):
        """   """
        try:
            user_id = validated_token.get('user_id')
            if not user_id:
                raise AuthenticationFailed('Token contains no user_id')
            
            #  
            user = User.objects.filter(id=user_id).first()
            
            if not user:
                logger.error(f"User not found for id: {user_id}")
                raise AuthenticationFailed('User not found')
            
            if not user.is_active:
                logger.warning(f"Inactive user tried to authenticate: {user_id}")
                raise AuthenticationFailed('User is inactive')
            
            #    ()
            if hasattr(user, 'email_verified') and not user.email_verified:
                #    
                from django.utils import timezone
                if user.date_joined.year < 2025:
                    user.email_verified = True
                    user.email_verified_at = timezone.now()
                    user.save(update_fields=['email_verified', 'email_verified_at'])
                    logger.info(f"Auto-verified legacy user: {user.username}")
            
            return user
            
        except User.DoesNotExist:
            logger.error(f"User does not exist: {user_id}")
            raise AuthenticationFailed('User not found')
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            raise AuthenticationFailed('Authentication failed')


def create_tokens_for_user(user):
    """
      JWT  
    
    Args:
        user: User 
        
    Returns:
        tuple: (access_token, refresh_token) 
    """
    try:
        refresh = RefreshToken.for_user(user)
        
        #   
        refresh['username'] = user.username
        refresh['email'] = user.email
        
        #    
        refresh.access_token['token_type'] = 'access'
        refresh['token_type'] = 'refresh'
        
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        logger.info(f"Tokens created for user {user.id}")
        
        return access_token, refresh_token
        
    except Exception as e:
        logger.error(f"Token creation failed for user {user.id}: {e}")
        raise


def debug_token(token_string):
    """
      
    
    Args:
        token_string: JWT  
        
    Returns:
        dict:  
    """
    try:
        # AccessToken  
        token = AccessToken(token_string)
        return {
            'valid': True,
            'type': 'access',
            'user_id': token.get('user_id'),
            'username': token.get('username'),
            'email': token.get('email'),
            'exp': token.get('exp'),
            'iat': token.get('iat'),
            'token_type': token.get('token_type', 'unknown')
        }
    except TokenError:
        try:
            # RefreshToken  
            token = RefreshToken(token_string)
            return {
                'valid': True,
                'type': 'refresh',
                'user_id': token.get('user_id'),
                'username': token.get('username'),
                'email': token.get('email'),
                'exp': token.get('exp'),
                'iat': token.get('iat'),
                'token_type': token.get('token_type', 'unknown')
            }
        except TokenError as e:
            return {
                'valid': False,
                'error': str(e)
            }


class JWTAuthenticationMiddleware:
    """
    JWT   ()
    Request user   
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_auth = EnhancedJWTAuthentication()
    
    def __call__(self, request):
        #  
        try:
            auth_result = self.jwt_auth.authenticate(request)
            if auth_result:
                request.user = auth_result[0]
                request.auth = auth_result[1]
        except Exception as e:
            logger.debug(f"JWT middleware auth failed: {e}")
            #    (AnonymousUser)
        
        response = self.get_response(request)
        return response