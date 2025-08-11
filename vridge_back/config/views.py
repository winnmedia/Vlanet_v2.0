from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .version import VERSION, COMMIT_HASH, FULL_VERSION


@csrf_exempt
@require_http_methods(["GET", "POST", "OPTIONS"])
def health_check(request):
    """  - Railway  """
    # Railway    
    return JsonResponse({
        "status": "ok",
        "service": "videoplanet-backend"
    }, status=200)


@csrf_exempt
def root_view(request):
    """  """
    return JsonResponse({
        "message": "VRidge Backend API",
        "version": "1.0.0",
        "endpoints": {
            "users": "/users/",
            "projects": "/projects/",
            "feedbacks": "/feedbacks/",
            "onlines": "/onlines/",
            "admin": "/admin/",
            "health": "/health/"
        }
    })