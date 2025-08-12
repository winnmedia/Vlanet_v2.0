"""
Gunicorn   -      
"""
import os
import multiprocessing

#  
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
backlog = 2048

#  
workers = int(os.environ.get('WEB_CONCURRENCY', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 2

#  
daemon = False
raw_env = [
    'DJANGO_SETTINGS_MODULE=config.settings.railway',
]
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# 
errorlog = '-'
loglevel = 'info'
accesslog = '-'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

#  
proc_name = 'vridge-backend'

#  
def on_starting(server):
    """  """
    server.log.info("Starting Vridge Backend Server")
    server.log.info(f"Listening at: {bind}")
    server.log.info(f"Using {workers} workers")

def on_reload(server):
    """ """
    server.log.info("Reloading Vridge Backend Server")

def worker_int(worker):
    """  """
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """ fork """
    server.log.info(f"Forking worker {worker.pid}")

def pre_exec(server):
    """    """
    server.log.info("Forked child, re-executing.")

def when_ready(server):
    """   """
    server.log.info("Server is ready. Spawning workers")
    #        
    import requests
    try:
        port = os.environ.get('PORT', '8000')
        response = requests.get(f'http://localhost:{port}/api/health/', timeout=5)
        server.log.info(f"Health check ready: {response.status_code}")
    except:
        server.log.info("Health check warming up...")

def worker_abort(worker):
    """  """
    worker.log.info("Worker received SIGABRT signal")