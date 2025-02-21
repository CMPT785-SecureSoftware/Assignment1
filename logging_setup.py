# logging_setup.py
import os
import logging
from logging.handlers import TimedRotatingFileHandler

# Create directories for log files if they do not exist
os.makedirs('audit-logs', exist_ok=True)
os.makedirs('application-logs', exist_ok=True)

def setup_audit_logger():
    audit_logger = logging.getLogger('audit')
    audit_logger.setLevel(logging.INFO)
    audit_handler = TimedRotatingFileHandler(
        'audit-logs/audit-log.txt', when='midnight', interval=1, backupCount=30
    )
    audit_handler.suffix = "%Y-%m-%d.txt"
    audit_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    audit_logger.addHandler(audit_handler)
    return audit_logger

def setup_app_logger():
    app_logger = logging.getLogger('application')
    app_logger.setLevel(logging.INFO)
    app_handler = TimedRotatingFileHandler(
        'application-logs/application-log.txt', when='midnight', interval=1, backupCount=30
    )
    app_handler.suffix = "%Y-%m-%d.txt"
    app_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    app_logger.addHandler(app_handler)
    return app_logger