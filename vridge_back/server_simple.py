#!/usr/bin/env python3
"""Ultra-minimal server for Railway"""
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')
    
    def do_POST(self):
        self.do_GET()
    
    def log_message(self, format, *args):
        pass  # No logs

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting on port {port}")
    HTTPServer(('0.0.0.0', port), Handler).serve_forever()