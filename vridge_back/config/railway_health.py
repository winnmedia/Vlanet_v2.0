"""
Railway 전용 간단한 헬스체크 뷰
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET", "HEAD", "OPTIONS"])
def railway_health_check(request):
    """
    Railway 헬스체크 전용 뷰
    - 데이터베이스 체크 없음
    - 간단한 JSON 응답만 반환
    """
    try:
        return JsonResponse({
            "status": "healthy",
            "service": "videoplanet-backend"
        }, status=200)
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)

@csrf_exempt
def simple_root_health(request):
    """
    루트 경로 헬스체크
    """
    return JsonResponse({"status": "ok"}, status=200)