from rest_framework.views import exception_handler
from rest_framework.response import Response


class ServiceError(Exception):
    """General service layer exception"""

    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

    @classmethod
    def permission_denied(cls, message="Permission denied"):
        """Create a permission denied error (403)"""
        return cls(message, status_code=403)

    @classmethod
    def not_found(cls, message="Resource not found"):
        """Create a not found error (404)"""
        return cls(message, status_code=404)

    @classmethod
    def bad_request(cls, message="Bad request"):
        """Create a bad request error (400)"""
        return cls(message, status_code=400)

    @classmethod
    def conflict(cls, message="Conflict"):
        """Create a conflict error (409)"""
        return cls(message, status_code=409)


def custom_exception_handler(exc, context):
    """Custom exception handler to handle ServiceError"""
    # Let DRF handle its own exceptions first
    response = exception_handler(exc, context)

    # If DRF handled it, return that response
    if response is not None:
        return response

    # Handle our custom ServiceError
    if isinstance(exc, ServiceError):
        return Response({"error": exc.message}, status=exc.status_code)

    # For any other unhandled exceptions, let Django handle them
    # This allows proper error messages in debug mode and proper logging
    return None
