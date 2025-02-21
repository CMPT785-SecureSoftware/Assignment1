# config.py
import uuid
from datetime import timedelta

class Config:
    SECRET_KEY = uuid.uuid4().hex
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'