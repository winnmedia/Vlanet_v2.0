# Railway   
from .railway_cors_fix import *

#   
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Railway   
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', os.environ.get('GOOGLE_ID'))
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', os.environ.get('GOOGLE_APP_PASSWORD'))

#   
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'VideoPlanet <vridgeofficial@gmail.com>')
SERVER_EMAIL = DEFAULT_FROM_EMAIL

#    
import logging
logger = logging.getLogger(__name__)

if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    logger.info(f"Email configured with user: {EMAIL_HOST_USER}")
else:
    logger.error("Email configuration missing: Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD")

#    
EMAIL_TIMEOUT = 10

# Gmail     
EMAIL_USE_SSL = False  # TLS   False
EMAIL_SSL_KEYFILE = None
EMAIL_SSL_CERTFILE = None