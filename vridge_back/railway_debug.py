#!/usr/bin/env python
"""
Railway Environment Debugger
Railway    .
"""
import os
import sys
import json
import socket
import subprocess
from datetime import datetime

def print_section(title):
    """  """
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)

def check_environment():
    """  """
    print_section("Environment Variables")
    
    critical_vars = [
        'PORT',
        'DATABASE_URL',
        'RAILWAY_ENVIRONMENT',
        'RAILWAY_PROJECT_ID',
        'RAILWAY_SERVICE_ID',
        'DJANGO_SETTINGS_MODULE',
        'SECRET_KEY'
    ]
    
    for var in critical_vars:
        value = os.environ.get(var, 'NOT SET')
        if var in ['DATABASE_URL', 'SECRET_KEY'] and value != 'NOT SET':
            #    
            value = value[:20] + '...'
        print(f"{var}: {value}")
    
    #   
    print("\nOther Railway variables:")
    for key, value in os.environ.items():
        if key.startswith('RAILWAY_') and key not in critical_vars:
            print(f"{key}: {value}")

def check_network():
    """  """
    print_section("Network Configuration")
    
    # 
    print(f"Hostname: {socket.gethostname()}")
    
    # IP 
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        print(f"IP Address: {ip_address}")
    except:
        print("IP Address: Unable to determine")
    
    #   
    port = int(os.environ.get('PORT', 8000))
    print(f"\nTrying to bind to port {port}...")
    
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        test_socket.bind(('0.0.0.0', port))
        test_socket.close()
        print(f" Port {port} is available")
    except OSError as e:
        print(f" Port {port} binding failed: {e}")

def check_database():
    """  """
    print_section("Database Connection")
    
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print(" DATABASE_URL not set")
        return
    
    # psycopg2   
    try:
        import psycopg2
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f" PostgreSQL connected: {version}")
        
        #  
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            LIMIT 5
        """)
        tables = cursor.fetchall()
        print(f"\nSample tables: {[t[0] for t in tables]}")
        
        conn.close()
    except ImportError:
        print(" psycopg2 not installed")
    except Exception as e:
        print(f" Database connection failed: {e}")

def check_django():
    """Django  """
    print_section("Django Configuration")
    
    # Django  
    settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'NOT SET')
    print(f"Settings Module: {settings_module}")
    
    # Django 
    try:
        result = subprocess.run(
            [sys.executable, 'manage.py', 'check'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(" Django check passed")
        else:
            print(f" Django check failed:\n{result.stderr}")
    except subprocess.TimeoutExpired:
        print(" Django check timeout")
    except Exception as e:
        print(f" Django check error: {e}")
    
    #  
    try:
        result = subprocess.run(
            [sys.executable, 'manage.py', 'showmigrations', '--plan', '--verbosity', '0'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            pending = [l for l in lines if '[ ]' in l]
            print(f"\nMigration status: {len(pending)} pending migrations")
            if pending and len(pending) < 10:
                for migration in pending[:5]:
                    print(f"  - {migration}")
        else:
            print(f" Migration check failed")
    except Exception as e:
        print(f" Migration check error: {e}")

def check_dependencies():
    """Python  """
    print_section("Python Dependencies")
    
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    
    #   
    critical_packages = [
        'django',
        'gunicorn',
        'psycopg2',
        'psycopg2-binary',
        'whitenoise',
        'djangorestframework',
        'django-cors-headers'
    ]
    
    print("\nCritical packages:")
    for package in critical_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f" {package}")
        except ImportError:
            print(f" {package} - NOT INSTALLED")

def test_simple_server():
    """ HTTP  """
    print_section("Simple HTTP Server Test")
    
    port = int(os.environ.get('PORT', 8000))
    
    test_code = f'''
import socket
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('0.0.0.0', {port}))
sock.listen(5)
print(f"Test server listening on port {port}")

sock.settimeout(2)
try:
    conn, addr = sock.accept()
    request = conn.recv(1024)
    response = b"HTTP/1.1 200 OK\\r\\nContent-Type: text/plain\\r\\n\\r\\nTest OK"
    conn.send(response)
    conn.close()
    print(" Successfully handled test request")
except socket.timeout:
    print(" Server can bind and listen")
finally:
    sock.close()
'''
    
    try:
        result = subprocess.run(
            [sys.executable, '-c', test_code],
            capture_output=True,
            text=True,
            timeout=3
        )
        print(result.stdout)
        if result.stderr:
            print(f"Errors: {result.stderr}")
    except subprocess.TimeoutExpired:
        print(" Server test completed (timeout expected)")
    except Exception as e:
        print(f" Server test failed: {e}")

def generate_report():
    """  """
    print_section("Diagnostic Summary")
    
    timestamp = datetime.now().isoformat()
    
    report = {
        'timestamp': timestamp,
        'environment': os.environ.get('RAILWAY_ENVIRONMENT', 'unknown'),
        'service_id': os.environ.get('RAILWAY_SERVICE_ID', 'unknown'),
        'checks': {
            'port_configured': bool(os.environ.get('PORT')),
            'database_configured': bool(os.environ.get('DATABASE_URL')),
            'django_configured': bool(os.environ.get('DJANGO_SETTINGS_MODULE')),
            'secret_key_configured': bool(os.environ.get('SECRET_KEY'))
        }
    }
    
    print(json.dumps(report, indent=2))
    
    print("\n" + "="*60)
    print("Diagnostic complete. Check the output above for issues.")
    print("="*60)

def main():
    """  """
    print("="*60)
    print(" Railway Deployment Diagnostics")
    print(f" Timestamp: {datetime.now().isoformat()}")
    print("="*60)
    
    check_environment()
    check_network()
    check_database()
    check_dependencies()
    check_django()
    test_simple_server()
    generate_report()

if __name__ == '__main__':
    main()