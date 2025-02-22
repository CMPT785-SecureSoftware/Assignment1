# config.py
import uuid
from datetime import timedelta


# ======================
# Configuration
# ======================

class Config:
    # we're using a unique, unpredictable SECRET_KEY
    SECRET_KEY = uuid.uuid4().hex
    # Setting session timeout to 30 minutes to ensure automatic expiration after inactivity
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    # Ensuring session cookies are sent only over secure HTTPS connections
    SESSION_COOKIE_SECURE = True
    # Enhancing session security by restricting cookie access & cross-site transmission to prevent XSS and CSRF attacks
    SESSION_COOKIE_HTTPONLY = True  
    SESSION_COOKIE_SAMESITE = 'Lax'
    