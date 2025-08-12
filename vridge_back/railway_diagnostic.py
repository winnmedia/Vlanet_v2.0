#!/usr/bin/env python3
"""
Railway Health Check Diagnostic Server
극도로 상세한 진단 정보를 제공하는 헬스체크 서버
경로 문제 진단에 집중
"""

import os
import sys
import json
import socket
import traceback
import subprocess
from datetime import datetime
from pathlib import Path

# 로깅 레벨 설정
DEBUG = True

def log(message, level='INFO'):
    """상세한 로깅"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"[{timestamp}] [{level}] {message}", flush=True)

def get_environment_info():
    """환경 정보 수집"""
    info = {
        'python_version': sys.version,
        'python_executable': sys.executable,
        'python_path': sys.path,
        'working_directory': os.getcwd(),
        'process_id': os.getpid(),
        'hostname': socket.gethostname(),
        'port': os.environ.get('PORT', 'NOT_SET'),
        'railway_environment': os.environ.get('RAILWAY_ENVIRONMENT', 'NOT_SET'),
        'railway_service_id': os.environ.get('RAILWAY_SERVICE_ID', 'NOT_SET'),
        'railway_project_id': os.environ.get('RAILWAY_PROJECT_ID', 'NOT_SET'),
        'django_settings': os.environ.get('DJANGO_SETTINGS_MODULE', 'NOT_SET'),
    }
    
    # 모든 환경 변수 (민감한 정보는 마스킹)
    env_vars = {}
    for key, value in os.environ.items():
        if any(sensitive in key.upper() for sensitive in ['SECRET', 'KEY', 'PASSWORD', 'TOKEN']):
            env_vars[key] = value[:10] + '...' if value else 'EMPTY'
        else:
            env_vars[key] = value
    info['environment_variables'] = env_vars
    
    return info

def check_file_system():
    """파일 시스템 구조 확인"""
    log("Checking file system structure...")
    
    fs_info = {
        'current_directory': os.getcwd(),
        'directory_contents': [],
        'parent_directory': str(Path.cwd().parent),
        'parent_contents': [],
        'app_structure': {}
    }
    
    # 현재 디렉토리 내용
    try:
        for item in os.listdir('.'):
            item_path = Path(item)
            fs_info['directory_contents'].append({
                'name': item,
                'type': 'dir' if item_path.is_dir() else 'file',
                'size': item_path.stat().st_size if item_path.is_file() else None
            })
    except Exception as e:
        fs_info['directory_error'] = str(e)
    
    # 부모 디렉토리 내용
    try:
        parent = Path.cwd().parent
        for item in os.listdir(parent):
            fs_info['parent_contents'].append(item)
    except Exception as e:
        fs_info['parent_error'] = str(e)
    
    # 중요 파일/디렉토리 존재 확인
    important_paths = [
        'manage.py',
        'vridge_back',
        'vridge_back/settings.py',
        'vridge_back/wsgi.py',
        'requirements.txt',
        'railway_health.py',
        'Procfile',
        'railway.json',
        'nixpacks.toml'
    ]
    
    for path in important_paths:
        fs_info['app_structure'][path] = {
            'exists': os.path.exists(path),
            'is_file': os.path.isfile(path) if os.path.exists(path) else None,
            'is_dir': os.path.isdir(path) if os.path.exists(path) else None,
            'absolute_path': os.path.abspath(path) if os.path.exists(path) else None
        }
    
    return fs_info

def test_imports():
    """Import 테스트"""
    log("Testing Python imports...")
    
    import_results = {}
    
    # 필수 모듈 테스트
    modules_to_test = [
        'django',
        'gunicorn',
        'psycopg2',
        'whitenoise',
        'corsheaders',
        'rest_framework',
        'vridge_back',
        'vridge_back.settings',
        'vridge_back.wsgi'
    ]
    
    for module in modules_to_test:
        try:
            if module.startswith('vridge_back'):
                # Django 앱 import 시도
                exec(f"import {module}")
            else:
                __import__(module)
            import_results[module] = {
                'status': 'SUCCESS',
                'error': None
            }
        except Exception as e:
            import_results[module] = {
                'status': 'FAILED',
                'error': str(e),
                'traceback': traceback.format_exc()
            }
    
    return import_results

def test_django_setup():
    """Django 설정 테스트"""
    log("Testing Django setup...")
    
    django_info = {
        'setup_attempted': False,
        'setup_success': False,
        'error': None,
        'settings_module': os.environ.get('DJANGO_SETTINGS_MODULE'),
        'manage_py_exists': os.path.exists('manage.py')
    }
    
    try:
        # Django 설정 시도
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vridge_back.settings')
        
        import django
        django.setup()
        
        django_info['setup_attempted'] = True
        django_info['setup_success'] = True
        
        # Django 설정 확인
        from django.conf import settings
        django_info['debug'] = settings.DEBUG
        django_info['allowed_hosts'] = settings.ALLOWED_HOSTS
        django_info['installed_apps'] = settings.INSTALLED_APPS[:5]  # 처음 5개만
        
    except Exception as e:
        django_info['setup_attempted'] = True
        django_info['error'] = str(e)
        django_info['traceback'] = traceback.format_exc()
    
    return django_info

def test_network_binding():
    """네트워크 바인딩 테스트"""
    log("Testing network binding...")
    
    port = int(os.environ.get('PORT', 8000))
    
    network_info = {
        'port': port,
        'bind_test': {},
        'hostname': socket.gethostname()
    }
    
    # 다양한 바인드 주소 테스트
    bind_addresses = [
        '0.0.0.0',
        '127.0.0.1',
        'localhost',
        ''  # 모든 인터페이스
    ]
    
    for addr in bind_addresses:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((addr, port))
            sock.close()
            network_info['bind_test'][addr] = 'SUCCESS'
        except Exception as e:
            network_info['bind_test'][addr] = f'FAILED: {str(e)}'
    
    return network_info

def run_command(command):
    """명령어 실행 및 결과 반환"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        return {
            'command': command,
            'returncode': result.returncode,
            'stdout': result.stdout[:1000],  # 처음 1000자만
            'stderr': result.stderr[:1000]
        }
    except Exception as e:
        return {
            'command': command,
            'error': str(e)
        }

def test_commands():
    """시스템 명령어 테스트"""
    log("Running system commands...")
    
    commands = [
        'pwd',
        'ls -la | head -20',
        'which python',
        'which python3',
        'python --version',
        'pip list | grep -E "django|gunicorn|psycopg2"',
        'echo $PATH',
        'echo $PYTHONPATH',
        'ps aux | grep python | head -5'
    ]
    
    results = []
    for cmd in commands:
        results.append(run_command(cmd))
    
    return results

def application(environ, start_response):
    """WSGI 애플리케이션 - 진단 정보를 JSON으로 반환"""
    
    log("="*60)
    log("HEALTH CHECK REQUEST RECEIVED")
    log(f"Time: {datetime.now().isoformat()}")
    log(f"Path: {environ.get('PATH_INFO', '/')}")
    log(f"Method: {environ.get('REQUEST_METHOD', 'UNKNOWN')}")
    log("="*60)
    
    # 진단 정보 수집
    diagnostic_data = {
        'timestamp': datetime.now().isoformat(),
        'request_path': environ.get('PATH_INFO', '/'),
        'request_method': environ.get('REQUEST_METHOD', 'UNKNOWN'),
        'wsgi_environ_keys': list(environ.keys()),
        'diagnostics': {}
    }
    
    try:
        # 1. 환경 정보
        log("Collecting environment info...")
        diagnostic_data['diagnostics']['environment'] = get_environment_info()
        
        # 2. 파일 시스템
        log("Checking file system...")
        diagnostic_data['diagnostics']['file_system'] = check_file_system()
        
        # 3. Import 테스트
        log("Testing imports...")
        diagnostic_data['diagnostics']['imports'] = test_imports()
        
        # 4. Django 설정
        log("Testing Django setup...")
        diagnostic_data['diagnostics']['django'] = test_django_setup()
        
        # 5. 네트워크
        log("Testing network...")
        diagnostic_data['diagnostics']['network'] = test_network_binding()
        
        # 6. 시스템 명령어
        log("Running system commands...")
        diagnostic_data['diagnostics']['commands'] = test_commands()
        
        # 성공 응답
        diagnostic_data['status'] = 'DIAGNOSTIC_COMPLETE'
        diagnostic_data['health'] = 'OK'
        
    except Exception as e:
        log(f"ERROR during diagnostics: {e}", level='ERROR')
        diagnostic_data['error'] = str(e)
        diagnostic_data['traceback'] = traceback.format_exc()
        diagnostic_data['status'] = 'DIAGNOSTIC_ERROR'
    
    # JSON 응답 생성
    response_body = json.dumps(diagnostic_data, indent=2, default=str)
    response_bytes = response_body.encode('utf-8')
    
    # 콘솔에도 출력
    log("="*60)
    log("DIAGNOSTIC SUMMARY")
    log("="*60)
    print(response_body, flush=True)
    log("="*60)
    
    # HTTP 응답
    status = '200 OK'
    headers = [
        ('Content-Type', 'application/json'),
        ('Content-Length', str(len(response_bytes))),
        ('Cache-Control', 'no-cache'),
        ('X-Diagnostic-Version', '2.0'),
        ('X-Timestamp', datetime.now().isoformat())
    ]
    
    start_response(status, headers)
    return [response_bytes]

def main():
    """독립 실행 모드"""
    log("Starting diagnostic server in standalone mode...")
    
    from wsgiref.simple_server import make_server
    
    port = int(os.environ.get('PORT', 8000))
    
    with make_server('0.0.0.0', port, application) as httpd:
        log(f"Diagnostic server running on port {port}")
        log(f"Visit http://localhost:{port}/ for diagnostics")
        httpd.serve_forever()

if __name__ == '__main__':
    main()