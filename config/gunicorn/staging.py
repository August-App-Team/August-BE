"""Gunicorn *production* config file"""

import multiprocessing

# Django WSGI application path in pattern MODULE_NAME:VARIABLE_NAME
wsgi_app = "config.wsgi:application"
# The number of worker processes for handling requests
workers = multiprocessing.cpu_count() * 2 + 1
# The socket to bind
bind = "0.0.0.0:8001"
# Write access and error info to /var/log
accesslog = "/var/log/gunicorn/staging/access.log"
errorlog = "/var/log/gunicorn/staging/error.log"
# Redirect stdout/stderr to log file
capture_output = True
# PID file so you can easily fetch process ID
pidfile = "/var/run/gunicorn/staging/prod.pid"
# Daemonize the Gunicorn process (detach & enter background)
daemon = True
