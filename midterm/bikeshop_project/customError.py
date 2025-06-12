from django.utils.encoding import force_str

from rest_framework import status
from rest_framework.exceptions import APIException


class CustomValidation(APIException):
    default_status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "A server error occurred."
    default_field = "detail"

    def __init__(self, detail=None, field=None, status_code=None):
        self.status_code = status_code or self.default_status_code
        field = field or self.default_field
        detail_text = force_str(detail or self.default_detail)
        self.detail = {field: detail_text}
