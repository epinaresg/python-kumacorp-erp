from core.tests.brand.init_test_case import InitTestCase

class AuthenticationBrandTestCase(InitTestCase):
    def setUp(self):
        super().setUp()

    def test_authentication(self):
        self._execute_authentication_tests(requests=self.requests)
