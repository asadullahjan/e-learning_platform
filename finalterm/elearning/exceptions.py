from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ErrorDetail


class ServiceError(Exception):
    """General service layer exception"""

    def __init__(self, message, status_code=400, code=None):
        self.message = message
        self.status_code = status_code
        self.code = code or "service_error"
        super().__init__(self.message)

    @classmethod
    def permission_denied(cls, message="Permission denied"):
        """Create a permission denied error (403)"""
        return cls(message, status_code=403, code="permission_denied")

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
    """Custom exception handler to handle ServiceError and common exceptions"""
    # Let DRF handle its own exceptions first
    response = exception_handler(exc, context)

    if response is not None:
        return response

    # Handle our custom ServiceError
    if isinstance(exc, ServiceError):
        detail = ErrorDetail(exc.message, code=exc.code)
        return Response({"detail": detail}, status=exc.status_code)

    # Handle common Python exceptions that should be user-friendly
    if isinstance(exc, ValueError):
        return Response(
            {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
        )

    if isinstance(exc, KeyError):
        return Response(
            {"detail": f"Missing required field: {str(exc)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(exc, TypeError):
        return Response(
            {"detail": f"Invalid data type provided: {str(exc)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # For any other unhandled exceptions, let Django handle them
    # This allows proper error messages in debug mode and proper logging
    return None
