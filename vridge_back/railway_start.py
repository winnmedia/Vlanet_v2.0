#!/usr/bin/env python3
"""
Railway 스마트 시작 스크립트
병렬로 헬스체크 서버와 Django 앱을 시작
"""
import os
import sys
import subprocess
import time
import signal
from threading import Thread

def log(message, level="INFO"):
    """로그 출력"""
    print(f"[{level}] {message}")
    sys.stdout.flush()

def run_health_server():
    """헬스체크 서버 실행"""
    log("Starting health check server...")
    try:
        subprocess.run([sys.executable, "health_server.py"], check=False)
    except Exception as e:
        log(f"Health server error: {e}", "ERROR")

def run_migrations():
    """마이그레이션 실행 (타임아웃 포함)"""
    if os.environ.get('SKIP_MIGRATIONS') == 'true':
        log("Skipping migrations (SKIP_MIGRATIONS=true)")
        return True
    
    log("Running database migrations...")
    try:
        result = subprocess.run(
            [sys.executable, "manage.py", "migrate", "--noinput"],
            timeout=30,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            log("Migrations completed successfully")
            return True
        else:
            log(f"Migration failed: {result.stderr}", "WARNING")
            return False
    except subprocess.TimeoutExpired:
        log("Migration timeout - continuing without migrations", "WARNING")
        return False
    except Exception as e:
        log(f"Migration error: {e}", "WARNING")
        return False

def run_django():
    """Django 앱 실행"""
    port = os.environ.get('PORT', '8000')
    log(f"Starting Django app on port {port}...")
    
    cmd = [
        "gunicorn",
        "config.wsgi:application",
        f"--bind=0.0.0.0:{port}",
        "--workers=2",
        "--threads=2",
        "--timeout=120",
        "--log-level=info",
        "--access-logfile=-",
        "--error-logfile=-",
        "--preload",
        "--max-requests=1000",
        "--max-requests-jitter=50"
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        log(f"Django startup failed: {e}", "ERROR")
        sys.exit(1)

def signal_handler(signum, frame):
    """시그널 처리"""
    log(f"Received signal {signum}, shutting down...")
    sys.exit(0)

def main():
    """메인 실행 함수"""
    # 시그널 핸들러 설정
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # 환경 변수 확인
    log(f"PORT: {os.environ.get('PORT', 'not set')}")
    log(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE', 'not set')}")
    log(f"DATABASE_URL: {'set' if os.environ.get('DATABASE_URL') else 'not set'}")
    
    # 헬스체크 서버를 백그라운드 스레드로 시작
    health_thread = Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    # 헬스체크 서버가 시작될 시간 확보
    time.sleep(2)
    
    # 마이그레이션 실행 (실패해도 계속 진행)
    run_migrations()
    
    # Django 앱 시작 (메인 스레드)
    run_django()

if __name__ == "__main__":
    main()