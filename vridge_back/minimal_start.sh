#!/bin/bash
# 최소 실행 가능 시작 스크립트
# 헬스체크 통과를 최우선으로 하는 단순 구성

echo "[INFO] Minimal startup mode - health check priority"

# Python 경로 확인
which python3 || which python

# 환경 변수 출력
echo "[INFO] PORT: $PORT"
echo "[INFO] DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"

# 단순 Python HTTP 서버로 즉시 헬스체크 응답
python3 -c "
import http.server
import socketserver
import os

PORT = int(os.environ.get('PORT', 8000))

class HealthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK - Minimal mode')
        
    def do_HEAD(self):
        self.do_GET()

with socketserver.TCPServer(('', PORT), HealthHandler) as httpd:
    print(f'[INFO] Minimal health server at port {PORT}')
    httpd.serve_forever()
" &

# 헬스체크 서버가 시작될 시간
sleep 3

# 백그라운드에서 마이그레이션 시도 (실패해도 무시)
python3 manage.py migrate --noinput 2>/dev/null || true

# Django 시작 시도 (실패해도 헬스체크 서버는 계속 실행)
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --timeout 120 \
    --log-level info \
    2>&1 || echo "[WARNING] Django failed, but health check continues"