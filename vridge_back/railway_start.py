#!/usr/bin/env python3
"""
Railway   
   Django  
"""
import os
import sys
import subprocess
import time
import signal
from threading import Thread

def log(message, level="INFO"):
    """ """
    print(f"[{level}] {message}")
    sys.stdout.flush()

def run_health_server():
    """  """
    log("Starting health check server...")
    try:
        subprocess.run([sys.executable, "health_server.py"], check=False)
    except Exception as e:
        log(f"Health server error: {e}", "ERROR")

def run_migrations():
    """  ( )"""
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
    """Django  """
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
    """ """
    log(f"Received signal {signum}, shutting down...")
    sys.exit(0)

def main():
    """  """
    #   
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    #   
    log(f"PORT: {os.environ.get('PORT', 'not set')}")
    log(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE', 'not set')}")
    log(f"DATABASE_URL: {'set' if os.environ.get('DATABASE_URL') else 'not set'}")
    
    #     
    health_thread = Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    #     
    time.sleep(2)
    
    #   (  )
    run_migrations()
    
    # Django   ( )
    run_django()

if __name__ == "__main__":
    main()