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
from api_health import csrf_token_view
from users import views as user_views
from users.views_signup_safe import SafeSignUp, SafeSignIn
from users.views_test import TestSignUp, TestCreate
from rest_framework_simplejwt.views import TokenRefreshView

# CORS 디버그 뷰 임포트
try:
    from .cors_debug import CORSDebugView
    cors_debug_view = CORSDebugView.as_view()
except ImportError:
    def cors_debug_view(request):
        return JsonResponse({"error": "CORS debug view not available"}, status=500)

# Fallback 시스템을 통한 안정적인 인증 뷰 로드
from .auth_fallback import get_auth_views

auth_views = get_auth_views()
login_view = auth_views['login']
signup_view = auth_views['signup'] 
refresh_view = auth_views['refresh']
verify_view = auth_views['verify']

# 레거시 코드 호환성 유지
HAS_IMPROVED_AUTH = (login_view.__name__ == 'ImprovedSignIn')
# from .debug_views import debug_info, test_error  # 삭제된 파일

# token_blacklist import를 보호
try:
    from rest_framework_simplejwt import token_blacklist
    HAS_TOKEN_BLACKLIST = True
except ImportError:
    HAS_TOKEN_BLACKLIST = False
    token_blacklist = None

# 간단한 헬스체크 뷰
def simple_health(request):
    return JsonResponse({"status": "ok"})

# API 버전 정보
def api_version(request):
    return JsonResponse({
        "version": "1.0.0",
        "name": "VideoPlanet API",
        "status": "stable",
        "updated": "2025-08-06"
    })

# CORS 테스트 뷰
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

# 디버그 뷰 임포트
try:
    from .urls_debug import URLDebugView, AuthTestView, auth_endpoint_status
    HAS_DEBUG_VIEWS = True
except ImportError:
    HAS_DEBUG_VIEWS = False

# Railway 디버그 뷰 임포트
try:
    from .debug_views import debug_status, debug_echo, test_signup_debug
    HAS_RAILWAY_DEBUG = True
except ImportError:
    HAS_RAILWAY_DEBUG = False

# 공개 프로젝트 목록 뷰 (임시)
from django.views import View
class PublicProjectListView(View):
    def get(self, request):
        return JsonResponse({"projects": []})

# SPA 뷰
class SPAView(TemplateView):
    template_name = "index.html"
    
    def get_template_names(self):
        # 템플릿이 없을 경우 빈 응답 반환
        return ["index.html"]
    
    def get(self, request, *args, **kwargs):
        # 템플릿이 없을 경우를 대비한 처리
        try:
            return super().get(request, *args, **kwargs)
        except:
            return JsonResponse({"message": "React app should be served here"})

# 개선된 인증 뷰 임포트
try:
    from users.views_auth_improved import ImprovedSignUp, ImprovedSignIn, TestUserCreate
    HAS_IMPROVED_AUTH_V2 = True
except ImportError:
    HAS_IMPROVED_AUTH_V2 = False

# 통합 인증 엔드포인트 - Fallback 시스템 사용
auth_patterns = [
    # API 표준 경로 (/api/auth/) - 환경별 적절한 뷰 사용
    path('api/auth/login/', login_view.as_view(), name='auth_login'),
    path('api/auth/signup/', signup_view.as_view(), name='auth_signup'),
    path('api/auth/refresh/', refresh_view.as_view(), name='auth_refresh'),
    path('api/auth/check-email/', user_views.CheckEmail.as_view(), name='auth_check_email'),
    path('api/auth/check-nickname/', user_views.CheckNickname.as_view(), name='auth_check_nickname'),
    path('api/auth/me/', user_views.UserMe.as_view(), name='auth_me'),
    # 테스트 엔드포인트
    path('api/auth/test-signup/', TestSignUp.as_view(), name='test_signup'),
    path('api/auth/test-create/', TestCreate.as_view(), name='test_create'),
]

# verify 엔드포인트는 사용 가능한 경우에만 추가
if verify_view:
    auth_patterns.append(path('api/auth/verify/', verify_view.as_view(), name='auth_verify'))

# 개선된 인증 뷰 V2가 있으면 추가 테스트 엔드포인트 제공
if HAS_IMPROVED_AUTH_V2:
    try:
        from users.views_auth_improved import TestUserCreate
        auth_patterns.append(path('api/auth/test-users/', TestUserCreate.as_view(), name='test_users'))
    except ImportError:
        pass

# 메인 URL 패턴
urlpatterns = auth_patterns + [
    # 루트 경로 헬스체크 (Railway 기본 헬스체크용) - 최우선 처리
    path("", ultra_fast_health, name="root_health"),
    
    # System API (헬스체크, 마이그레이션 상태 등)
    path("api/", include("system.urls")),  # 시스템 API 추가
    
    # API 헬스체크 (기존 유지) - 초고속 헬스체크로 변경
    path("api/health/", ultra_fast_health, name="api_health"),  # 초고속 헬스체크
    path("api/health-full/", health_check, name="api_health_full"),  # 상세 헬스체크
    path("api/version/", api_version, name="api_version"),  # API 버전 정보
    path("health/", simple_health_check, name="health"),  # 레거시 헬스체크
    path("cors-test/", cors_test_view, name="cors_test"),  # CORS 테스트
    path("public/projects/", PublicProjectListView.as_view(), name="public_projects"),  # 공개 프로젝트 목록
    
    # 디버그 엔드포인트 (Railway 환경 디버깅용)
    path("api/debug/urls/", URLDebugView.as_view() if HAS_DEBUG_VIEWS else simple_health, name="debug_urls"),
    path("api/debug/auth-status/", auth_endpoint_status if HAS_DEBUG_VIEWS else simple_health, name="debug_auth_status"),
    path("api/debug/auth-test/", AuthTestView.as_view() if HAS_DEBUG_VIEWS else simple_health, name="debug_auth_test"),
    path("api/debug/cors/", cors_debug_view, name="debug_cors"),  # CORS 디버그 엔드포인트
    path("admin/", admin.site.urls),
    path("admin-dashboard/", include("admin_dashboard.urls")),  # 관리자 대시보드
    
    # 디버깅 엔드포인트 (Railway 환경에서만 활성화)
    # path("api/debug-info/", debug_info, name="debug_info"),  # 삭제된 뷰
    # path("api/test-error/", test_error, name="test_error"),  # 삭제된 뷰
    
    # API 경로 (권장) - /api/ 프리픽스를 사용하는 표준 경로
    path("api/users/", include("users.urls")),
    path("api/projects/", include(("projects.urls", "projects"), namespace="api_projects")),
    path("api/feedbacks/", include(("feedbacks.urls", "feedbacks"), namespace="api_feedbacks")),
    path("api/onlines/", include("onlines.urls")),
    path("api/video-planning/", include("video_planning.urls")),
    path("api/video-analysis/", include("video_analysis.urls")),
    path("api/ai-video/", include("ai_video.urls")),  # AI 영상 생성 API
    path("api/documents/", include("documents.urls")),  # 문서 관리 API
    path("api/analytics/", include("analytics.urls")),  # 분석 API
    
    # 레거시 경로 (하위 호환성) - /api/ 프리픽스가 없는 구 경로
    # 새로운 개발에서는 위의 /api/ 경로를 사용할 것을 권장
    path("users/", include("users.urls")),
    path("projects/", include(("projects.urls", "projects"), namespace="legacy_projects")),
    path("feedbacks/", include(("feedbacks.urls", "feedbacks"), namespace="legacy_feedbacks")),
    path("onlines/", include("onlines.urls")),
    
    # CSRF 토큰 (특별 경로)
    path("users/csrf-token/", csrf_token_view, name="csrf_token"),
]

# Railway 디버그 엔드포인트 추가
if HAS_RAILWAY_DEBUG:
    urlpatterns += [
        path('api/debug/status/', debug_status, name='debug_status'),
        path('api/debug/echo/', debug_echo, name='debug_echo'),
        path('api/debug/test-signup/', test_signup_debug, name='test_signup_debug'),
    ]

# Always serve media files
if settings.DEBUG:
    # 개발 환경에서는 Django의 static 서빙 사용
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # 프로덕션에서는 커스텀 미디어 서빙 뷰 사용
    from .media_settings import serve_media
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve_media, name='serve_media'),
    ]

# SPA catch-all route - API 경로가 아닌 모든 요청을 React로 전달
# 이것은 반드시 맨 마지막에 와야 함
urlpatterns += [
    # 루트 경로를 포함한 모든 나머지 경로를 React SPA로 전달
    re_path(r'^(?!api|admin|media|static|health|users|projects|feedbacks|onlines|cors-test|public).*$', SPAView.as_view(), name='spa'),
]

# token_blacklist가 있을 때만 unregister
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

admin.site.site_title = "Vlanet 관리자"
admin.site.site_header = "Vlanet 관리 시스템"
admin.site.index_title = "대시보드"

# 커스텀 에러 핸들러 설정
handler400 = 'config.error_handlers.custom_400_handler'
handler403 = 'config.error_handlers.custom_403_handler'
handler404 = 'config.error_handlers.custom_404_handler'
handler500 = 'config.error_handlers.custom_500_handler'
