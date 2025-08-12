#!/usr/bin/env python3
"""
Railway Direct Health Check Server
Procfile에서 직접 실행 가능한 Python 헬스체크 서버
"""

import os
import sys
from datetime import datetime

# 환경 변수에서 포트 가져오기
PORT = int(os.environ.get('PORT', 8000))

print(f"""
=====================================
Railway Direct Health Server
Time: {datetime.now().isoformat()}
Port: {PORT}
Working Directory: {os.getcwd()}
Python: {sys.executable}
=====================================
""", flush=True)

# 초간단 HTTP 서버
import socket

def run_server():
    """최소한의 HTTP 서버"""
    
    # 소켓 생성
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # 바인드
    server_socket.bind(('0.0.0.0', PORT))
    server_socket.listen(5)
    
    print(f"[INFO] Server listening on 0.0.0.0:{PORT}", flush=True)
    
    while True:
        try:
            # 연결 대기
            client_socket, address = server_socket.accept()
            
            # 요청 읽기 (최대 4KB)
            request = client_socket.recv(4096).decode('utf-8')
            
            # 요청 경로 추출
            if request:
                first_line = request.split('\n')[0]
                method, path, _ = first_line.split(' ', 2)
                
                print(f"[REQUEST] {method} {path} from {address[0]}", flush=True)
                
                # 헬스체크 응답
                if '/health' in path or path == '/':
                    # 200 OK 응답
                    response_body = '{"status":"healthy","server":"railway-direct","timestamp":"' + datetime.now().isoformat() + '"}'
                    response = f"""HTTP/1.1 200 OK\r
Content-Type: application/json\r
Content-Length: {len(response_body)}\r
Connection: close\r
\r
{response_body}"""
                    
                    print(f"[RESPONSE] 200 OK for health check", flush=True)
                    
                else:
                    # 404 응답
                    response_body = '{"error":"Not Found"}'
                    response = f"""HTTP/1.1 404 Not Found\r
Content-Type: application/json\r
Content-Length: {len(response_body)}\r
Connection: close\r
\r
{response_body}"""
                    
                    print(f"[RESPONSE] 404 Not Found", flush=True)
                
                # 응답 전송
                client_socket.send(response.encode('utf-8'))
            
            # 연결 종료
            client_socket.close()
            
        except Exception as e:
            print(f"[ERROR] {e}", flush=True)
            if 'client_socket' in locals():
                client_socket.close()
            continue

if __name__ == '__main__':
    try:
        run_server()
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped by user", flush=True)
    except Exception as e:
        print(f"[FATAL] Server error: {e}", flush=True)
        sys.exit(1)