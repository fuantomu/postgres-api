import unittest

class BaseAPITest(unittest.TestCase):
    get_success_code = 202
    post_success_code = 201
    bad_request_error_code = 400
    validation_error_code = 422

    def __init__(self, methodName = "runTest", client = None):
        super().__init__(methodName)
        self.client = client

