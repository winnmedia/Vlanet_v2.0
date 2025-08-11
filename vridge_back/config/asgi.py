"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

# Railway  railway  
if os.environ.get('RAILWAY_ENVIRONMENT'):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.railway")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.railway")

import django  #    django  

django.setup()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import OriginValidator, AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from feedbacks import routing

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "websocket": OriginValidator(
            AuthMiddlewareStack(
                # URLRouter  ,    HTTP path 
                URLRouter(routing.websocket_urlpatterns)
            ),
            [
                ".localhost",
                "http://localhost:3000",
                ".vlanet.net",
                "https://vlanet.net:443",
            ],
        ),
        "http": django_asgi_app,
    }
)
