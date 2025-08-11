import hashlib
import secrets
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class PasswordResetSecurity:
    """   """
    
    @staticmethod
    def generate_auth_code():
        """  6   """
        return str(secrets.randbelow(900000) + 100000)
    
    @staticmethod
    def hash_auth_code(auth_code):
        """  """
        return hashlib.sha256(f"{auth_code}{settings.SECRET_KEY}".encode()).hexdigest()
    
    @staticmethod
    def verify_auth_code(provided_code, stored_hash):
        """  """
        provided_hash = PasswordResetSecurity.hash_auth_code(provided_code)
        return secrets.compare_digest(provided_hash, stored_hash)
    
    @staticmethod
    def check_rate_limit(identifier, action_type="auth_request", limit=3, window=300):
        """Rate limiting  (: 5 3)"""
        cache_key = f"rate_limit:{action_type}:{identifier}"
        
        #    
        attempts = cache.get(cache_key, 0)
        
        if attempts >= limit:
            return False, f"{window//60}  {limit}   ."
        
        #   
        cache.set(cache_key, attempts + 1, window)
        return True, None
    
    @staticmethod
    def store_auth_code(email, auth_code, expiry_minutes=10):
        """    (: 10 )"""
        cache_key = f"password_reset:{email}"
        hashed_code = PasswordResetSecurity.hash_auth_code(auth_code)
        
        data = {
            'code': hashed_code,
            'created_at': datetime.now().isoformat(),
            'attempts': 0
        }
        
        cache.set(cache_key, data, expiry_minutes * 60)
        logger.info(f"Auth code stored for {email}, expires in {expiry_minutes} minutes")
    
    @staticmethod
    def verify_and_get_auth_code(email, provided_code, max_attempts=5):
        """      """
        cache_key = f"password_reset:{email}"
        data = cache.get(cache_key)
        
        if not data:
            return False, "    ."
        
        #   
        if data['attempts'] >= max_attempts:
            cache.delete(cache_key)
            return False, "   .    ."
        
        #   
        data['attempts'] += 1
        cache.set(cache_key, data, 600)  # 10 
        
        #  
        if PasswordResetSecurity.verify_auth_code(provided_code, data['code']):
            #    
            cache.delete(cache_key)
            return True, None
        
        return False, f"   . ({data['attempts']}/{max_attempts} )"
    
    @staticmethod
    def generate_reset_token(user_id):
        """    """
        token = secrets.token_urlsafe(32)
        cache_key = f"reset_token:{token}"
        
        cache.set(cache_key, {
            'user_id': user_id,
            'created_at': datetime.now().isoformat()
        }, 600)  # 10 
        
        return token
    
    @staticmethod
    def verify_reset_token(token):
        """  """
        cache_key = f"reset_token:{token}"
        data = cache.get(cache_key)
        
        if not data:
            return None, "   ."
        
        #    
        cache.delete(cache_key)
        return data['user_id'], None