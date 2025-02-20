# config.py
import uuid
from datetime import timedelta

class Config:
    # Secure random secret key
    SECRET_KEY = uuid.uuid4().hex
    # Session timeout
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)