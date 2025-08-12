#!/usr/bin/env python3
"""
Dual Server Architecture - Health Check + Django
================================================
Runs health check on main port, Django on secondary port.
Railway-optimized with complete isolation between services.
"""

import os
import sys
import subprocess
import threading
import time
import signal

def run_health_beacon(port):
    """Run the health beacon server"""
    print(f"[HEALTH] Starting health beacon on port {port}")
    subprocess.run([
        "gunicorn", 
        "health_beacon:application",
        "--bind", f"0.0.0.0:{port}",
        "--workers", "1",
        "--threads", "1",
        "--timeout", "30",
        "--log-level", "info"
    ])

def run_django_server():
    """Run the Django application server"""
    print("[DJANGO] Starting Django server in 5 seconds...")
    time.sleep(5)  # Give health check time to start
    
    # Change to Django directory
    os.chdir("vridge_back")
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
    
    print("[DJANGO] Running Django on internal port 8001")
    subprocess.run([
        "gunicorn",
        "config.wsgi:application",
        "--bind", "0.0.0.0:8001",
        "--workers", "2",
        "--threads", "4",
        "--timeout", "120",
        "--log-level", "info"
    ])

def main():
    """Main orchestrator"""
    port = os.environ.get('PORT', '8000')
    
    print(f"[MAIN] Dual Server Architecture Starting")
    print(f"[MAIN] Health check will run on port {port}")
    print(f"[MAIN] Django will run on port 8001")
    
    # Start health beacon in main thread (Railway expects this)
    health_thread = threading.Thread(target=run_health_beacon, args=(port,))
    health_thread.daemon = False
    health_thread.start()
    
    # Start Django in background thread
    django_thread = threading.Thread(target=run_django_server)
    django_thread.daemon = True
    django_thread.start()
    
    # Handle signals gracefully
    def signal_handler(sig, frame):
        print("\n[MAIN] Shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Keep main thread alive
    health_thread.join()

if __name__ == "__main__":
    main()