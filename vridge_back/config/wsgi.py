"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Determine settings module based on environment
if os.environ.get('RAILWAY_ENVIRONMENT'):
    # Railway production environment
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.railway")
else:
    # Local development environment
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings_dev")

application = get_wsgi_application()
