from flask import jsonify
from werkzeug.exceptions import HTTPException

class APIError(Exception):
    """Base API error class"""
    status_code = 400
    
    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
    
    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = 'error'
        rv['code'] = self.status_code
        return rv

class NotFoundError(APIError):
    """Raised when a resource is not found"""
    status_code = 404

class ValidationError(APIError):
    """Raised when validation fails"""
    status_code = 400

class UnauthorizedError(APIError):
    """Raised when authentication is required but not provided"""
    status_code = 401

class ForbiddenError(APIError):
    """Raised when the user doesn't have permission to access the resource"""
    status_code = 403

class ConflictError(APIError):
    """Raised when there's a conflict with the current state of the resource"""
    status_code = 409

def register_error_handlers(app):
    """Register error handlers for the application"""
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        """Handle API errors"""
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors"""
        return jsonify({
            'status': 'error',
            'code': 404,
            'message': 'The requested resource was not found.'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        # Log the error here
        app.logger.error(f'Internal Server Error: {str(error)}')
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': 'An internal server error occurred.'
        }), 500
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Handle other HTTP exceptions"""
        return jsonify({
            'status': 'error',
            'code': error.code,
            'message': error.description
        }), error.code
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        """Handle all other exceptions"""
        app.logger.error(f'Unhandled exception: {str(error)}')
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': 'An unexpected error occurred.'
        }), 500
