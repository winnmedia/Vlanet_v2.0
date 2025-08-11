"""
Twelve Labs API  
      
"""
import os
from django.core.exceptions import ImproperlyConfigured

def get_env_variable(var_name, default=None):
    """  """
    try:
        return os.environ[var_name]
    except KeyError:
        if default is not None:
            return default
        error_msg = f"  {var_name}  ."
        raise ImproperlyConfigured(error_msg)

# Twelve Labs API 
TWELVE_LABS_API_KEY = get_env_variable('TWELVE_LABS_API_KEY', '')
TWELVE_LABS_INDEX_ID = get_env_variable('TWELVE_LABS_INDEX_ID', '')

# AI    
USE_AI_ANALYSIS = bool(TWELVE_LABS_API_KEY and TWELVE_LABS_INDEX_ID)

#     
DEVELOPMENT_MODE = not USE_AI_ANALYSIS

#     
DAILY_ANALYSIS_LIMIT = int(get_env_variable('DAILY_ANALYSIS_LIMIT', '100'))
MONTHLY_ANALYSIS_LIMIT = int(get_env_variable('MONTHLY_ANALYSIS_LIMIT', '1000'))

#    ( )
USER_DAILY_LIMIT = int(get_env_variable('USER_DAILY_LIMIT', '5'))
USER_MONTHLY_LIMIT = int(get_env_variable('USER_MONTHLY_LIMIT', '50'))

#   
PREMIUM_USER_DAILY_LIMIT = int(get_env_variable('PREMIUM_USER_DAILY_LIMIT', '20'))
PREMIUM_USER_MONTHLY_LIMIT = int(get_env_variable('PREMIUM_USER_MONTHLY_LIMIT', '200'))

#     
MAX_VIDEO_SIZE_MB = int(get_env_variable('MAX_VIDEO_SIZE_MB', '500'))  # 500MB
MAX_VIDEO_DURATION_MINUTES = int(get_env_variable('MAX_VIDEO_DURATION_MINUTES', '30'))  # 30

#   
FREE_USER_MAX_SIZE_MB = int(get_env_variable('FREE_USER_MAX_SIZE_MB', '100'))  # 100MB
FREE_USER_MAX_DURATION_MINUTES = int(get_env_variable('FREE_USER_MAX_DURATION_MINUTES', '10'))  # 10

#  
TWELVE_LABS_LOGGING = {
    'level': get_env_variable('TWELVE_LABS_LOG_LEVEL', 'INFO'),
    'log_api_calls': get_env_variable('LOG_TWELVE_LABS_API', 'False').lower() == 'true',
    'log_analysis_results': get_env_variable('LOG_ANALYSIS_RESULTS', 'True').lower() == 'true'
}