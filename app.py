# app.py
from flask import Flask
from config import Config
from routes import bp as routes_bp
from database import init_db
from logging_setup import get_logger

app = Flask(__name__)
app.config.from_object(Config)

# Set the secret key and session lifetime (from config.py)
# (Already loaded via app.config)

# Initialize Database
init_db()

# Register blueprint for routes
app.register_blueprint(routes_bp)

if __name__ == '__main__':
    app.run()
    # app.run(ssl_context='adhoc')  # Secure HTTPS connection