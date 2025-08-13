"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.models import Group
from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# HEALTH CHECK VIEW - Simple and Standard
# ============================================================================
def health_check(request):
    """
    Standard health check endpoint for Railway.
    Returns 200 OK with JSON response.
    """
    return JsonResponse({
        "status": "healthy",
        "service": "videoplanet-backend"
    }, status=200)

# ============================================================================
# CSRF TOKEN VIEW
# ============================================================================
def csrf_token_view(request):
    """CSRF token endpoint"""
    from django.middleware.csrf import get_token
    return JsonResponse({"csrfToken": get_token(request)})

# ============================================================================
# CORS TEST VIEW
# ============================================================================
def cors_test_view(request):
    """CORS test endpoint"""
    return JsonResponse({
        "status": "ok",
        "message": "CORS test successful",
        "method": request.method,
        "headers": {
            "Origin": request.headers.get("Origin"),
            "Host": request.headers.get("Host")
        }
    })

# ============================================================================
# PUBLIC PROJECT VIEW (Placeholder)
# ============================================================================
from django.views import View
class PublicProjectListView(View):
    def get(self, request):
        return JsonResponse({"projects": []})

# ============================================================================
# SPA VIEW
# ============================================================================
class SPAView(TemplateView):
    template_name = "index.html"
    
    def get_template_names(self):
        return ["index.html"]
    
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except:
            return JsonResponse({"message": "React app should be served here"})

# ============================================================================
# AUTHENTICATION IMPORTS
# ============================================================================
from users import views as user_views
from users.views_signup_safe import SafeSignUp, SafeSignIn
from users.views_test import TestSignUp, TestCreate
from rest_framework_simplejwt.views import TokenRefreshView

# Import auth fallback views
from .auth_fallback import get_auth_views

auth_views = get_auth_views()
login_view = auth_views['login']
signup_view = auth_views['signup']
refresh_view = auth_views['refresh']
verify_view = auth_views.get('verify')

# Check for token blacklist
try:
    from rest_framework_simplejwt import token_blacklist
    HAS_TOKEN_BLACKLIST = True
except ImportError:
    HAS_TOKEN_BLACKLIST = False
    token_blacklist = None

# ============================================================================
# URL PATTERNS
# ============================================================================

# Authentication patterns
auth_patterns = [
    # API Authentication endpoints
    path('api/auth/login/', login_view.as_view(), name='auth_login'),
    path('api/auth/signup/', signup_view.as_view(), name='auth_signup'),
    path('api/auth/refresh/', refresh_view.as_view(), name='auth_refresh'),
    path('api/auth/check-email/', user_views.CheckEmail.as_view(), name='auth_check_email'),
    path('api/auth/check-nickname/', user_views.CheckNickname.as_view(), name='auth_check_nickname'),
    path('api/auth/me/', user_views.UserMe.as_view(), name='auth_me'),
    
    # Test endpoints
    path('api/auth/test-signup/', TestSignUp.as_view(), name='test_signup'),
    path('api/auth/test-create/', TestCreate.as_view(), name='test_create'),
]

# Add verify endpoint if available
if verify_view:
    auth_patterns.append(path('api/auth/verify/', verify_view.as_view(), name='auth_verify'))

# Main URL patterns
urlpatterns = [
    # Health check - MUST be first for Railway
    path('health/', health_check, name='health'),
    path('', health_check, name='root_health'),  # Root health check
    
    # Admin
    path('admin/', admin.site.urls),
    path('admin-dashboard/', include('admin_dashboard.urls')),
    
    # System API
    path('api/', include('system.urls')),
    
    # Enhanced Authentication (must come before basic auth patterns)
    path('api/auth/', include('users.urls_enhanced')),  # Enhanced signup endpoints
    
    # Authentication (legacy)
    *auth_patterns,
    
    # API endpoints
    path('api/users/', include('users.urls')),
    path('api/projects/', include(('projects.urls', 'projects'), namespace='api_projects')),
    path('api/feedbacks/', include(('feedbacks.urls', 'feedbacks'), namespace='api_feedbacks')),
    path('api/onlines/', include('onlines.urls')),
    path('api/video-planning/', include('video_planning.urls')),
    path('api/video-analysis/', include('video_analysis.urls')),
    path('api/ai-video/', include('ai_video.urls')),
    path('api/documents/', include('documents.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/calendar/', include('calendars.urls')),
    path('api/invitations/', include('invitations.urls')),
    
    # Legacy endpoints (for backward compatibility)
    path('users/', include('users.urls')),
    path('projects/', include(('projects.urls', 'projects'), namespace='legacy_projects')),
    path('feedbacks/', include(('feedbacks.urls', 'feedbacks'), namespace='legacy_feedbacks')),
    path('onlines/', include('onlines.urls')),
    
    # Utility endpoints
    path('cors-test/', cors_test_view, name='cors_test'),
    path('public/projects/', PublicProjectListView.as_view(), name='public_projects'),
    path('users/csrf-token/', csrf_token_view, name='csrf_token'),
]

# Static and media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # Production media serving
    try:
        from .media_settings import serve_media
        urlpatterns += [
            re_path(r'^media/(?P<path>.*)$', serve_media, name='serve_media'),
        ]
    except ImportError:
        pass

# SPA catch-all route - MUST be last
urlpatterns += [
    re_path(r'^(?!api|admin|media|static|health|users|projects|feedbacks|onlines|cors-test|public).*$', 
            SPAView.as_view(), name='spa'),
]

# ============================================================================
# ADMIN CUSTOMIZATION
# ============================================================================

# Unregister token blacklist models if present
if HAS_TOKEN_BLACKLIST and token_blacklist:
    try:
        admin.site.unregister(token_blacklist.models.BlacklistedToken)
        admin.site.unregister(token_blacklist.models.OutstandingToken)
    except admin.sites.NotRegistered:
        pass

# Unregister Group model
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass

# Admin site customization
admin.site.site_title = "Vlanet 관리자"
admin.site.site_header = "Vlanet 관리자 패널"
admin.site.index_title = "관리"

# ============================================================================
# ERROR HANDLERS
# ============================================================================
handler400 = 'config.error_handlers.custom_400_handler'
handler403 = 'config.error_handlers.custom_403_handler'
handler404 = 'config.error_handlers.custom_404_handler'
handler500 = 'config.error_handlers.custom_500_handler'