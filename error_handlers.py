from flask import jsonify
from logging_setup import setup_app_logger  # Import logging setup function

# Initialize the logger for the application
app_logger = setup_app_logger()

# Function to register error handlers for the app
def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(error):
        # Log and return a JSON response for 404 Not Found errors
        app_logger.warning(f"404 error: {error}")
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        # Log and return a JSON response for 500 Internal Server Errors
        app_logger.error(f"Internal server error: {error}")
        return jsonify({'error': 'Internal server error'}), 500
