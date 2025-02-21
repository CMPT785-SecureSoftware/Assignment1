# app.py
from flask import Flask
from config import Config
from routes import bp as routes_bp
from error_handlers import register_error_handlers
from database import init_db
from flask_talisman import Talisman

app = Flask(__name__)
app.config.from_object(Config)

# ======================
# HTTP Security Headers
# ======================

@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'"
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Cache-Control'] = 'no-store'
    return response

# Initialize the database
init_db()

# Register the blueprint for routes
app.register_blueprint(routes_bp)

# Register custom error handlers
register_error_handlers(app)

# ======================
# Main Execution
# ======================
if __name__ == '__main__':
    # Running with Flask-Talisman for HTTPS in production.
    Talisman(app, force_https=True)
    # Running with an ad-hoc SSL context for HTTPS in development.
    app.run(debug=True, ssl_context='adhoc')