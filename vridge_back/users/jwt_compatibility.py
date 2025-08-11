"""
JWT   
    JWT   
"""
from rest_framework_simplejwt.authentication import JWTAuthentication as BaseJWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .migration_compatibility import get_user_safely
import logging

logger = logging.getLogger(__name__)

class CompatibleJWTAuthentication(BaseJWTAuthentication):
    """   JWT  """
    
    def get_user(self, validated_token):
        """   """
        try:
            #   
            return super().get_user(validated_token)
        except Exception as e:
            logger.warning(f"JWT user lookup failed, trying compatibility mode: {e}")
            
            #   
            try:
                user_id = validated_token.get('user_id')
                if not user_id:
                    raise InvalidToken('Token contained no recognizable user identification')
                
                #   
                from django.contrib.auth import get_user_model
                User = get_user_model()
                
                # ID    
                try:
                    return User.objects.only(
                        'id', 'username', 'email', 'first_name', 'last_name',
                        'is_active', 'is_staff', 'is_superuser', 'date_joined',
                        'password', 'nickname', 'login_method'
                    ).get(id=user_id)
                except User.DoesNotExist:
                    raise InvalidToken('User not found')
                    
            except Exception as e:
                logger.error(f"Compatibility mode also failed: {e}")
                raise InvalidToken(f'User retrieval failed: {str(e)}')