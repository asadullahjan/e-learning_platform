import functools
from django.test import TestCase
from rest_framework.test import APITestCase


def debug_on_failure(test_method):
    """Decorator that logs response data when a test method fails"""

    @functools.wraps(test_method)
    def wrapper(self, *args, **kwargs):
        try:
            return test_method(self, *args, **kwargs)
        except Exception as e:
            # Log response if it exists
            if hasattr(self, "last_response") and self.last_response:
                filename = test_method.__code__.co_filename.replace("\\", "/")
                line_number = test_method.__code__.co_firstlineno

                print(f"\n{'='*80}")
                print(f"🚨 TEST FAILED - {test_method.__name__} 🚨")
                print(f"{'='*80}")
                print(f'File "{filename}:{line_number}"')
                print(f"Status Code: {self.last_response.status_code}")

                try:
                    if hasattr(self.last_response, "data"):
                        print(f"Response Data: \n{self.last_response.data}")
                    elif hasattr(self.last_response, "content"):
                        content = self.last_response.content.decode()
                        print(f"Response Content: \n{content}")
                except Exception as decode_error:
                    print(f"Could not extract response data: {decode_error}")

                print(f"{'='*80}\n")

            # Re-raise the original exception
            raise e

    return wrapper


class BaseTestCase(TestCase):
    """
    Base test case for regular Django tests with custom logging.
    Use @debug_on_failure decorator on test methods.
    """

    def setUp(self):
        super().setUp()
        self.last_response = None

    def log_response(self, response):
        """Helper to set last_response and return response"""
        self.last_response = response
        return response


class BaseAPITestCase(APITestCase):
    """
    Test base class for API tests.
    Use @debug_on_failure decorator on test methods
    and set self.last_response = response in your tests.
    """

    def setUp(self):
        super().setUp()
        self.last_response = None
        self.expected_status = None
        self.expected_data = None

    def assertStatusCode(self, response, expected_status_code):
        self.expected_status = expected_status_code
        self.assertEqual(response.status_code, expected_status_code)

    def log_response(self, response):
        """Helper to set last_response and return response"""
        self.last_response = response
        return response
