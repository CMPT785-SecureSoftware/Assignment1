# error_handlers.py
from flask import jsonify
from logging_setup import setup_app_logger

app_logger = setup_app_logger()

# ======================
# Error Handlers (Optional)
# ======================

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(error):
        app_logger.warning(f"404 error: {error}")
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        app_logger.error(f"Internal server error: {error}")
        return jsonify({'error': 'Internal server error'}), 500
