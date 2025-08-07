"""
Gunicorn configuration file for Match Cut app.
Usage: gunicorn -c gunicorn_config.py app:app
"""
import multiprocessing
import os

# Worker Options
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gthread'
threads = 2
worker_connections = 1000
timeout = 300  # 5 minutes for video processing
keepalive = 2

# Server Mechanics
daemon = False
raw_env = []

# Logging
errorlog = '-'
loglevel = 'info'
accesslog = '-'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Server Socket
bind = '127.0.0.1:5000'  # Change to '0.0.0.0:5000' for network access

# Environment Configuration
preload_app = True

def on_starting(server):
    """Log when Gunicorn server is starting"""
    print("Starting Gunicorn server for Match Cut application")

def on_exit(server):
    """Clean up any temporary files when shutting down"""
    print("Shutting down Gunicorn server for Match Cut application")
    # Add cleanup logic here if needed
