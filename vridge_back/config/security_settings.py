"""
     
"""
import os


def get_secure_settings(debug=False):
    """    """
    if debug:
        #   
        return {
            'CSRF_COOKIE_SECURE': False,
            'SESSION_COOKIE_SECURE': False,
            'SECURE_SSL_REDIRECT': False,
            'SECURE_HSTS_SECONDS': 0,
            'SECURE_HSTS_INCLUDE_SUBDOMAINS': False,
            'SECURE_HSTS_PRELOAD': False,
        }
    else:
        #   
        return {
            'CSRF_COOKIE_SECURE': True,
            'SESSION_COOKIE_SECURE': True,
            'SECURE_SSL_REDIRECT': True,
            'SECURE_HSTS_SECONDS': 31536000,  # 1
            'SECURE_HSTS_INCLUDE_SUBDOMAINS': True,
            'SECURE_HSTS_PRELOAD': True,
            'SECURE_PROXY_SSL_HEADER': ('HTTP_X_FORWARDED_PROTO', 'https'),
        }


def validate_secret_key(secret_key):
    """SECRET_KEY  """
    if not secret_key:
        raise ValueError("SECRET_KEY must be set in production")
    
    if len(secret_key) < 50:
        raise ValueError("SECRET_KEY must be at least 50 characters long")
    
    if secret_key.startswith('django-insecure'):
        raise ValueError("Production SECRET_KEY cannot start with 'django-insecure'")
    
    return True


def get_allowed_hosts():
    """ ALLOWED_HOSTS 설정 - 환경별 보안 고려 """
    import sys
    
    # 환경변수에서 ALLOWED_HOSTS 가져오기
    allowed_hosts_env = os.environ.get('ALLOWED_HOSTS', '')
    if allowed_hosts_env:
        hosts = [host.strip() for host in allowed_hosts_env.split(',')]
        # 테스트 환경일 때만 testserver 자동 추가
        if 'test' in sys.argv or 'pytest' in sys.modules:
            if 'testserver' not in hosts:
                hosts.append('testserver')
        return hosts
    
    # 기본값 설정 (환경별)
    base_hosts = [
        'localhost',
        '127.0.0.1',
        'videoplanet.up.railway.app',
        'api.vlanet.net',
        'vlanet.net',
        'www.vlanet.net',
    ]
    
    # 테스트 환경에서만 testserver 추가
    # 이는 Django 테스트 프레임워크가 기본적으로 사용하는 호스트명
    if 'test' in sys.argv or 'pytest' in sys.modules or os.environ.get('TESTING', 'False').lower() == 'true':
        base_hosts.append('testserver')
    
    # 개발 환경에서 추가 허용 호스트
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    if debug:
        base_hosts.extend([
            '0.0.0.0',
            '*'  # 개발 환경에서만 모든 호스트 허용 (주의: 프로덕션에서는 절대 사용 금지)
        ])
    
    return base_hosts