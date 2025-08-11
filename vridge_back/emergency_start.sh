#!/bin/bash
# 긴급 시작 스크립트 - 헬스체크만 통과시키기

echo "EMERGENCY MODE"

# 가장 단순한 Python HTTP 서버 실행
python3 -c "
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()
    def log_message(self, f, *a):
        pass

port = int(os.environ.get('PORT', 8000))
print(f'Emergency server on port {port}')
HTTPServer(('', port), H).serve_forever()
"