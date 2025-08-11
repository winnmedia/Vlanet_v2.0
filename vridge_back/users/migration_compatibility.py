"""
  
Railway          
"""
from django.db import connection, models
import logging

logger = logging.getLogger(__name__)

def check_column_exists(table_name, column_name):
    """    (SQLite/PostgreSQL )"""
    try:
        with connection.cursor() as cursor:
            # SQLite PostgreSQL 
            if connection.vendor == 'sqlite':
                # SQLite 
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [col[1] for col in cursor.fetchall()]
                return column_name in columns
            else:
                # PostgreSQL 
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = %s AND column_name = %s
                """, [table_name, column_name])
                return cursor.fetchone() is not None
    except Exception as e:
        logger.warning(f"Error checking column {table_name}.{column_name}: {e}")
        #       ( )
        return True

def get_user_fields_safely():
    """User        """
    safe_fields = [
        'id', 'username', 'email', 'first_name', 'last_name', 
        'is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login',
        'password', 'nickname', 'login_method', 'email_secret'
    ]
    
    #     
    if check_column_exists('users_user', 'email_verified'):
        safe_fields.extend(['email_verified', 'email_verified_at'])
    
    return safe_fields

def create_user_queryset_safely():
    """    User  """
    from .models import User
    
    try:
        #   
        return User.objects.all()
    except Exception as e:
        logger.warning(f"Full queryset failed, using safe fields: {e}")
        
        #   
        safe_fields = get_user_fields_safely()
        return User.objects.only(*safe_fields)

def get_user_safely(email):
    """   (email  username)"""
    from .models import User
    
    try:
        # email   
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            pass
        
        # username  
        try:
            return User.objects.get(username=email)
        except User.DoesNotExist:
            pass
            
        #    DoesNotExist 
        raise User.DoesNotExist(f"User with email/username '{email}' not found")
        
    except Exception as e:
        logger.warning(f"Safe user lookup failed for {email}: {e}")
        raise
