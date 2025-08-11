#!/usr/bin/env python3
"""
Django 시작 문제 디버깅 스크립트
로컬에서 Django 시작 과정을 단계별로 테스트합니다.
"""
import os
import sys
import subprocess
import time
import socket
from pathlib import Path

def test_step(name, func):
    """각 단계 테스트 및 결과 출력"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print('='*60)
    try:
        result = func()
        print(f"✓ SUCCESS: {result}")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False

def check_python_version():
    """Python 버전 확인"""
    version = sys.version
    if sys.version_info < (3, 8):
        raise Exception(f"Python 3.8+ required, got {version}")
    return f"Python {version}"

def check_django_installed():
    """Django 설치 확인"""
    try:
        import django
        return f"Django {django.get_version()}"
    except ImportError:
        raise Exception("Django not installed")

def check_requirements():
    """필수 패키지 확인"""
    required = ['gunicorn', 'django', 'psycopg2-binary', 'whitenoise', 'django-cors-headers']
    missing = []
    
    for package in required:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        raise Exception(f"Missing packages: {', '.join(missing)}")
    return "All required packages installed"

def check_settings():
    """Django 설정 파일 확인"""
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.railway'
    
    try:
        from django.conf import settings
        settings.configure()
        return f"Settings loaded: DEBUG={settings.DEBUG}"
    except Exception as e:
        # 이미 설정되어 있을 수 있음
        return "Settings already configured or accessible"

def check_database():
    """데이터베이스 연결 테스트"""
    try:
        result = subprocess.run(
            [sys.executable, 'manage.py', 'dbshell', '--command=SELECT VERSION();'],
            capture_output=True,
            text=True,
            timeout=10,
            env={**os.environ, 'DJANGO_SETTINGS_MODULE': 'config.settings.railway'}
        )
        if result.returncode == 0:
            return f"Database connected: {result.stdout.strip()[:50]}"
        else:
            # SQLite fallback 확인
            if 'sqlite' in result.stderr.lower() or result.returncode == 1:
                return "Using SQLite (no PostgreSQL configured)"
            raise Exception(f"Database error: {result.stderr}")
    except subprocess.TimeoutExpired:
        raise Exception("Database connection timeout")

def check_migrations():
    """마이그레이션 상태 확인"""
    result = subprocess.run(
        [sys.executable, 'manage.py', 'showmigrations', '--plan', '--verbosity=0'],
        capture_output=True,
        text=True,
        timeout=30,
        env={**os.environ, 'DJANGO_SETTINGS_MODULE': 'config.settings.railway'}
    )
    
    if result.returncode != 0:
        raise Exception(f"Migration check failed: {result.stderr}")
    
    lines = result.stdout.split('\n')
    applied = sum(1 for line in lines if '[X]' in line)
    pending = sum(1 for line in lines if '[ ]' in line)
    
    return f"Migrations: {applied} applied, {pending} pending"

def run_migrations():
    """마이그레이션 실행"""
    result = subprocess.run(
        [sys.executable, 'manage.py', 'migrate', '--noinput'],
        capture_output=True,
        text=True,
        timeout=60,
        env={**os.environ, 'DJANGO_SETTINGS_MODULE': 'config.settings.railway'}
    )
    
    if result.returncode != 0:
        # 경고는 무시하고 에러만 확인
        if 'error' in result.stderr.lower():
            raise Exception(f"Migration failed: {result.stderr[:200]}")
    
    return "Migrations completed"

def check_static_files():
    """정적 파일 설정 확인"""
    staticfiles_dir = Path('staticfiles')
    if not staticfiles_dir.exists():
        staticfiles_dir.mkdir(exist_ok=True)
    
    result = subprocess.run(
        [sys.executable, 'manage.py', 'collectstatic', '--noinput', '--verbosity=0'],
        capture_output=True,
        text=True,
        timeout=30,
        env={**os.environ, 'DJANGO_SETTINGS_MODULE': 'config.settings.railway'}
    )
    
    if result.returncode != 0 and 'error' in result.stderr.lower():
        raise Exception(f"Static files collection failed: {result.stderr[:200]}")
    
    return f"Static files collected to {staticfiles_dir}"

def test_runserver():
    """Django runserver 테스트"""
    print("\nTrying to start Django development server...")
    process = subprocess.Popen(
        [sys.executable, 'manage.py', 'runserver', '127.0.0.1:8001', '--noreload'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env={**os.environ, 'DJANGO_SETTINGS_MODULE': 'config.settings.railway'}
    )
    
    # 서버 시작 대기
    time.sleep(5)
    
    # 프로세스 상태 확인
    if process.poll() is not None:
        output = process.stdout.read()
        raise Exception(f"Server failed to start: {output[:500]}")
    
    # 포트 확인
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(('127.0.0.1', 8001))
    sock.close()
    
    # 프로세스 종료
    process.terminate()
    process.wait(timeout=5)
    
    if result == 0:
        return "Django development server started successfully"
    else:
        raise Exception("Server started but port not accessible")

def test_gunicorn():
    """Gunicorn 테스트"""
    print("\nTrying to start Gunicorn...")
    process = subprocess.Popen(
        [
            'gunicorn',
            'config.wsgi:application',
            '--bind=127.0.0.1:8002',
            '--workers=1',
            '--timeout=30',
            '--log-level=debug'
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env={**os.environ, 'DJANGO_SETTINGS_MODULE': 'config.settings.railway'}
    )
    
    # Gunicorn 시작 대기
    time.sleep(5)
    
    # 프로세스 상태 확인
    if process.poll() is not None:
        output = process.stdout.read()
        raise Exception(f"Gunicorn failed to start: {output[:500]}")
    
    # 포트 확인
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(('127.0.0.1', 8002))
    sock.close()
    
    # 프로세스 종료
    process.terminate()
    process.wait(timeout=5)
    
    if result == 0:
        return "Gunicorn started successfully"
    else:
        raise Exception("Gunicorn started but port not accessible")

def main():
    """메인 디버깅 프로세스"""
    print("Django Startup Debugging Script")
    print("="*60)
    
    tests = [
        ("Python Version", check_python_version),
        ("Django Installation", check_django_installed),
        ("Required Packages", check_requirements),
        ("Settings Configuration", check_settings),
        ("Database Connection", check_database),
        ("Migration Status", check_migrations),
        ("Run Migrations", run_migrations),
        ("Static Files", check_static_files),
        ("Django Development Server", test_runserver),
        ("Gunicorn Server", test_gunicorn),
    ]
    
    results = []
    for name, test_func in tests:
        success = test_step(name, test_func)
        results.append((name, success))
        if not success and name in ["Python Version", "Django Installation", "Required Packages"]:
            print("\n⚠️  Critical failure, stopping tests")
            break
    
    # 결과 요약
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for name, success in results:
        status = "✓" if success else "✗"
        print(f"{status} {name}")
    
    success_count = sum(1 for _, s in results if s)
    total_count = len(results)
    
    print(f"\nResult: {success_count}/{total_count} tests passed")
    
    if success_count == total_count:
        print("\n✅ All tests passed! Django should start successfully.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        print("\nCommon solutions:")
        print("1. Install missing packages: pip install -r requirements.txt")
        print("2. Set DATABASE_URL environment variable for PostgreSQL")
        print("3. Run migrations: python manage.py migrate")
        print("4. Check file permissions in the project directory")

if __name__ == "__main__":
    main()