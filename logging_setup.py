# logging_setup.py
import os
import logging
from logging.handlers import TimedRotatingFileHandler

# ======================
# Setup Logging
# ======================

# Ensuring directories for storing log files exist, create if not exist
os.makedirs('audit-logs', exist_ok=True)
os.makedirs('application-logs', exist_ok=True)

#Function to setup the audit logger (for tracking user events e.g. logins, registrations, etc.)
def setup_audit_logger():

    # Retrieve or creating the 'audit' logger instance
    audit_logger = logging.getLogger('audit')
    
    # Capture logs at INFO and above severity logs 
    audit_logger.setLevel(logging.INFO)
    
    # Created to manage log file rotation daily at midnight; keep up to 30 backup files
    audit_handler = TimedRotatingFileHandler(
        'audit-logs/audit-log.txt', when='midnight', interval=1, backupCount=30
    )
    
    # formatting for rotated log files (appends date)
    audit_handler.suffix = "%Y-%m-%d.txt"
    
    # defining for log messages format (msg & timestamp)
    audit_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    
    # Attach handler to the logger to enable logging
    audit_logger.addHandler(audit_handler)
    # Return the configured audit logger for use in the application
    return audit_logger

# Function to set up the application logger (for program-related events e.g. errors, HTTP errors,etc.)
def setup_app_logger():
    # Retrieve or creating the 'application' logger instance
    app_logger = logging.getLogger('application')
    
    # Capture logs at INFO and above severity logs 
    app_logger.setLevel(logging.INFO)
    
    # Rotate logs daily at midnight; keep up to 30 backup files
    app_handler = TimedRotatingFileHandler(
        'application-logs/application-log.txt', when='midnight', interval=1, backupCount=30
    )
    
    # formatting for rotated log files (appends date)
    app_handler.suffix = "%Y-%m-%d.txt"
    
    # defining for log messages format (msg & timestamp)
    app_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    
    # Attach handler to the logger to enable logging
    app_logger.addHandler(app_handler)
    # Return the configured application logger for use in the application
    return app_logger