from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def simple_health_check(request):
    """  - DB     """
    return JsonResponse({
        "status": "ok",
        "service": "vridge-backend"
    })