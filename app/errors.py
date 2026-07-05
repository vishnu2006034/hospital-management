"""HTTP error handlers.

Registers custom error pages for common HTTP status codes.
"""

from flask import jsonify, Flask
from flask.typing import ResponseReturnValue

from app.extensions import db


def register_error_handlers(app: Flask) -> None:
    """Register error handlers with the Flask application."""

    @app.errorhandler(404)
    def not_found(error) -> ResponseReturnValue:
        """Handle 404 Not Found errors."""
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found.',
        }), 404

    @app.errorhandler(500)
    def internal_error(error) -> ResponseReturnValue:
        """Handle 500 Internal Server errors."""
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred.',
        }), 500

    @app.errorhandler(403)
    def forbidden(error) -> ResponseReturnValue:
        """Handle 403 Forbidden errors."""
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource.',
        }), 403
