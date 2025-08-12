"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.models import Group
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.generic import TemplateView
import logging

logger = logging.getLogger(__name__)

from .views import health_check, root_view
from .simple_health import simple_health_check
from .fast_health import ultra_fast_health, root_health
from .railway_health import railway_health_check, simple_root_health
from api_health import csrf_token_view
from users import views as user_views
from users.views_signup_safe import SafeSignUp, SafeSignIn
from users.views_test import TestSignUp, TestCreate
from rest_framework_simplejwt.views import TokenRefreshView

# CORS   
try:
    from .cors_debug import CORSDebugView
    cors_debug_view = CORSDebugView.as_view()
except ImportError:
    def cors_debug_view(request):
        return JsonResponse({"error": "CORS debug view not available"}, status=500)

# Fallback      
from .auth_fallback import get_auth_views

auth_views = get_auth_views()
login_view = auth_views['login']
signup_view = auth_views['signup'] 
refresh_view = auth_views['refresh']
verify_view = auth_views['verify']

#    
HAS_IMPROVED_AUTH = (login_view.__name__ == 'ImprovedSignIn')
# from .debug_views import debug_info, test_error  #  

# token_blacklist import 
try:
    from rest_framework_simplejwt import token_blacklist
    HAS_TOKEN_BLACKLIST = True
except ImportError:
    HAS_TOKEN_BLACKLIST = False
    token_blacklist = None

#   
def simple_health(request):
    return JsonResponse({"status": "ok"})

# API version is now handled by system.views.version_info
# Removed duplicate api_version function to avoid confusion

# CORS  
def cors_test_view(request):
    return JsonResponse({
        "status": "ok",
        "message": "CORS test successful",
        "method": request.method,
        "headers": {
            "Origin": request.headers.get("Origin"),
            "Host": request.headers.get("Host")
        }
    })

#   
try:
    from .urls_debug import URLDebugView, AuthTestView, auth_endpoint_status
    HAS_DEBUG_VIEWS = True
except ImportError:
    HAS_DEBUG_VIEWS = False

# Railway   
try:
    from .debug_views import debug_status, debug_echo, test_signup_debug
    HAS_RAILWAY_DEBUG = True
except ImportError:
    HAS_RAILWAY_DEBUG = False

#     ()
from django.views import View
class PublicProjectListView(View):
    def get(self, request):
        return JsonResponse({"projects": []})

# SPA 
class SPAView(TemplateView):
    template_name = "index.html"
    
    def get_template_names(self):
        #      
        return ["index.html"]
    
    def get(self, request, *args, **kwargs):
        #     
        try:
            return super().get(request, *args, **kwargs)
        except:
            return JsonResponse({"message": "React app should be served here"})

#    
try:
    from users.views_auth_improved import ImprovedSignUp, ImprovedSignIn, TestUserCreate
    HAS_IMPROVED_AUTH_V2 = True
except ImportError:
    HAS_IMPROVED_AUTH_V2 = False

#    - Fallback  
auth_patterns = [
    # API   (/api/auth/) -    
    path('api/auth/login/', login_view.as_view(), name='auth_login'),
    path('api/auth/signup/', signup_view.as_view(), name='auth_signup'),
    path('api/auth/refresh/', refresh_view.as_view(), name='auth_refresh'),
    path('api/auth/check-email/', user_views.CheckEmail.as_view(), name='auth_check_email'),
    path('api/auth/check-nickname/', user_views.CheckNickname.as_view(), name='auth_check_nickname'),
    path('api/auth/me/', user_views.UserMe.as_view(), name='auth_me'),
    #  
    path('api/auth/test-signup/', TestSignUp.as_view(), name='test_signup'),
    path('api/auth/test-create/', TestCreate.as_view(), name='test_create'),
]

# verify     
if verify_view:
    auth_patterns.append(path('api/auth/verify/', verify_view.as_view(), name='auth_verify'))

#    V2     
if HAS_IMPROVED_AUTH_V2:
    try:
        from users.views_auth_improved import TestUserCreate
        auth_patterns.append(path('api/auth/test-users/', TestUserCreate.as_view(), name='test_users'))
    except ImportError:
        pass

#  URL 
urlpatterns = auth_patterns + [
    #    (Railway  ) -  
    path("", simple_root_health, name="root_health"),
    
    # System API (,   )
    path("api/", include("system.urls")),  #  API 
    
    # API  ( ) -   
    path("api/health/", railway_health_check, name="api_health"),  # Railway 헬스체크
    path("api/health-full/", health_check, name="api_health_full"),  #  
    # api/version/ is handled by system.urls (included above)
    path("health/", simple_health_check, name="health"),  #  
    path("cors-test/", cors_test_view, name="cors_test"),  # CORS 
    path("public/projects/", PublicProjectListView.as_view(), name="public_projects"),  #   
    
    #   (Railway  )
    path("api/debug/urls/", URLDebugView.as_view() if HAS_DEBUG_VIEWS else simple_health, name="debug_urls"),
    path("api/debug/auth-status/", auth_endpoint_status if HAS_DEBUG_VIEWS else simple_health, name="debug_auth_status"),
    path("api/debug/auth-test/", AuthTestView.as_view() if HAS_DEBUG_VIEWS else simple_health, name="debug_auth_test"),
    path("api/debug/cors/", cors_debug_view, name="debug_cors"),  # CORS  
    path("admin/", admin.site.urls),
    path("admin-dashboard/", include("admin_dashboard.urls")),  #  
    
    #   (Railway  )
    # path("api/debug-info/", debug_info, name="debug_info"),  #  
    # path("api/test-error/", test_error, name="test_error"),  #  
    
    # API  () - /api/    
    path("api/users/", include("users.urls")),
    path("api/projects/", include(("projects.urls", "projects"), namespace="api_projects")),
    path("api/feedbacks/", include(("feedbacks.urls", "feedbacks"), namespace="api_feedbacks")),
    path("api/onlines/", include("onlines.urls")),
    path("api/video-planning/", include("video_planning.urls")),
    path("api/video-analysis/", include("video_analysis.urls")),
    path("api/ai-video/", include("ai_video.urls")),  # AI   API
    path("api/documents/", include("documents.urls")),  #   API
    path("api/analytics/", include("analytics.urls")),  #  API
    path("api/calendar/", include("calendars.urls")),  #  API
    path("api/invitations/", include("invitations.urls")),  #  API
    
    #   ( ) - /api/    
    #    /api/    
    path("users/", include("users.urls")),
    path("projects/", include(("projects.urls", "projects"), namespace="legacy_projects")),
    path("feedbacks/", include(("feedbacks.urls", "feedbacks"), namespace="legacy_feedbacks")),
    path("onlines/", include("onlines.urls")),
    
    # CSRF  ( )
    path("users/csrf-token/", csrf_token_view, name="csrf_token"),
]

# Railway   
if HAS_RAILWAY_DEBUG:
    urlpatterns += [
        path('api/debug/status/', debug_status, name='debug_status'),
        path('api/debug/echo/', debug_echo, name='debug_echo'),
        path('api/debug/test-signup/', test_signup_debug, name='test_signup_debug'),
    ]

# Always serve media files
if settings.DEBUG:
    #   Django static  
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    #      
    from .media_settings import serve_media
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve_media, name='serve_media'),
    ]

# SPA catch-all route - API     React 
#      
urlpatterns += [
    #       React SPA 
    re_path(r'^(?!api|admin|media|static|health|users|projects|feedbacks|onlines|cors-test|public).*$', SPAView.as_view(), name='spa'),
]

# token_blacklist   unregister
if HAS_TOKEN_BLACKLIST and token_blacklist:
    try:
        admin.site.unregister(token_blacklist.models.BlacklistedToken)
        admin.site.unregister(token_blacklist.models.OutstandingToken)
    except admin.sites.NotRegistered:
        pass

try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass

admin.site.site_title = "Vlanet "
admin.site.site_header = "Vlanet  "
admin.site.index_title = ""

#    
handler400 = 'config.error_handlers.custom_400_handler'
handler403 = 'config.error_handlers.custom_403_handler'
handler404 = 'config.error_handlers.custom_404_handler'
handler500 = 'config.error_handlers.custom_500_handler'
