"""
초고속 헬스체크 엔드포인트
Railway 헬스체크 타임아웃 문제 해결용
"""
from django.http import HttpResponse

def ultra_fast_health(request):
    """
    초고속 헬스체크 - 최소한의 검증만 수행
    Railway 헬스체크가 빠르게 통과할 수 있도록 설계
    """
    return HttpResponse("OK", status=200, content_type="text/plain")

def root_health(request):
    """
    루트 경로 헬스체크
    """
    return HttpResponse("VideoPlanet Backend Running", status=200, content_type="text/plain")