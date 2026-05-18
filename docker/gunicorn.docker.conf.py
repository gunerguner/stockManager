import multiprocessing
import os

bind = "0.0.0.0:8000"

worker_class = "sync"
_default_workers = min(max(2, multiprocessing.cpu_count()), 4)
workers = int(os.getenv("GUNICORN_WORKERS", str(_default_workers)))

daemon = False
pidfile = None

accesslog = "-"
errorlog = "-"
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")

graceful_timeout = 30
timeout = int(os.getenv("GUNICORN_TIMEOUT", "120"))
preload_app = True
