"""
    
Django Channels   
"""

import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application


def get_websocket_application():
    """
      
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
    
    # Django ASGI 
    django_asgi_app = get_asgi_application()
    
    #   import (circular import )
    from feedbacks import routing as feedback_routing
    from chat import routing as chat_routing
    
    #   
    websocket_urlpatterns = []
    websocket_urlpatterns.extend(feedback_routing.websocket_urlpatterns)
    websocket_urlpatterns.extend(chat_routing.websocket_urlpatterns)
    
    #  
    application = ProtocolTypeRouter({
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(websocket_urlpatterns)
            )
        ),
    })
    
    return application


def configure_channels(settings_module):
    """
    Channels   
    settings.py  
    """
    
    # Redis URL 
    REDIS_URL = os.environ.get('REDIS_URL')
    
    if REDIS_URL:
        # Redis   
        CHANNEL_LAYERS = {
            'default': {
                'BACKEND': 'channels_redis.core.RedisChannelLayer',
                'CONFIG': {
                    "hosts": [REDIS_URL],
                    "capacity": 1500,
                    "expiry": 10,
                    "group_expiry": 86400,  # 24
                    "channel_capacity": {
                        "http.request": 1000,
                        "websocket.send": 100,
                    },
                },
            },
        }
    else:
        #  InMemory 
        CHANNEL_LAYERS = {
            'default': {
                'BACKEND': 'channels.layers.InMemoryChannelLayer',
                'CONFIG': {
                    "capacity": 100,
                    "expiry": 60,
                },
            },
        }
    
    return CHANNEL_LAYERS


#    
class WebSocketManager:
    """
       
    """
    
    def __init__(self):
        self.connections = {}
        self.reconnect_attempts = {}
    
    def add_connection(self, user_id, channel_name):
        """ """
        if user_id not in self.connections:
            self.connections[user_id] = []
        self.connections[user_id].append(channel_name)
    
    def remove_connection(self, user_id, channel_name):
        """ """
        if user_id in self.connections:
            self.connections[user_id].remove(channel_name)
            if not self.connections[user_id]:
                del self.connections[user_id]
    
    def get_user_connections(self, user_id):
        """   """
        return self.connections.get(user_id, [])
    
    def is_user_online(self, user_id):
        """   """
        return user_id in self.connections


#   
ws_manager = WebSocketManager()


#  
class WebSocketAuthMiddleware:
    """
      
    JWT   
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        from urllib.parse import parse_qs
        from channels.db import database_sync_to_async
        from rest_framework_simplejwt.tokens import AccessToken
        from django.contrib.auth.models import AnonymousUser
        
        #    
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]
        
        if token:
            try:
                #  
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                
                #  
                from users.models import User
                scope['user'] = await database_sync_to_async(
                    User.objects.get
                )(id=user_id)
            except Exception:
                scope['user'] = AnonymousUser()
        else:
            scope['user'] = AnonymousUser()
        
        return await self.app(scope, receive, send)


#  
class ReconnectingWebSocket:
    """
         ( )
    """
    
    JS_CODE = """
    class ReconnectingWebSocket {
        constructor(url, options = {}) {
            this.url = url;
            this.options = {
                maxReconnectAttempts: 5,
                reconnectInterval: 1000,
                maxReconnectInterval: 30000,
                reconnectDecay: 1.5,
                timeoutInterval: 2000,
                ...options
            };
            
            this.reconnectAttempts = 0;
            this.reconnectInterval = this.options.reconnectInterval;
            this.shouldReconnect = true;
            this.messageQueue = [];
            
            this.connect();
        }
        
        connect() {
            this.ws = new WebSocket(this.url);
            this.connectTimeout = setTimeout(() => {
                this.ws.close();
            }, this.options.timeoutInterval);
            
            this.ws.onopen = (event) => {
                clearTimeout(this.connectTimeout);
                this.reconnectAttempts = 0;
                this.reconnectInterval = this.options.reconnectInterval;
                
                //    
                while (this.messageQueue.length > 0) {
                    const message = this.messageQueue.shift();
                    this.ws.send(message);
                }
                
                if (this.onopen) this.onopen(event);
            };
            
            this.ws.onclose = (event) => {
                clearTimeout(this.connectTimeout);
                if (this.onclose) this.onclose(event);
                
                if (this.shouldReconnect && 
                    this.reconnectAttempts < this.options.maxReconnectAttempts) {
                    setTimeout(() => {
                        this.reconnectAttempts++;
                        this.connect();
                    }, this.reconnectInterval);
                    
                    //   
                    this.reconnectInterval = Math.min(
                        this.reconnectInterval * this.options.reconnectDecay,
                        this.options.maxReconnectInterval
                    );
                }
            };
            
            this.ws.onerror = (event) => {
                if (this.onerror) this.onerror(event);
            };
            
            this.ws.onmessage = (event) => {
                if (this.onmessage) this.onmessage(event);
            };
        }
        
        send(data) {
            if (this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(data);
            } else {
                this.messageQueue.push(data);
            }
        }
        
        close() {
            this.shouldReconnect = false;
            this.ws.close();
        }
    }
    """


#    
PRODUCTION_GUIDE = """
#    

## 1. Daphne   
```bash
pip install daphne
```

## 2. Daphne  (Procfile  start.sh)
```bash
daphne -b 0.0.0.0 -p $PORT config.asgi:application
```

## 3. Nginx   
```nginx
location /ws {
    proxy_pass http://localhost:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 86400;
}
```

## 4.  
- REDIS_URL: Redis  
- WEBSOCKET_ACCEPT_ALL_ORIGINS: False ()

## 5.  
- Redis Cluster  
-   Sticky Session 
-   
"""


#  
async def websocket_health_check(scope, receive, send):
    """
      
    /ws/health/  
    """
    await send({
        'type': 'websocket.accept',
    })
    
    await send({
        'type': 'websocket.send',
        'text': json.dumps({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
        })
    })
    
    await send({
        'type': 'websocket.close',
    })


#  
class WebSocketMonitor:
    """
      
    """
    
    def __init__(self):
        self.metrics = {
            'total_connections': 0,
            'active_connections': 0,
            'messages_sent': 0,
            'messages_received': 0,
            'errors': 0,
        }
    
    def on_connect(self):
        self.metrics['total_connections'] += 1
        self.metrics['active_connections'] += 1
    
    def on_disconnect(self):
        self.metrics['active_connections'] -= 1
    
    def on_message_sent(self):
        self.metrics['messages_sent'] += 1
    
    def on_message_received(self):
        self.metrics['messages_received'] += 1
    
    def on_error(self):
        self.metrics['errors'] += 1
    
    def get_metrics(self):
        return self.metrics.copy()


#   
ws_monitor = WebSocketMonitor()