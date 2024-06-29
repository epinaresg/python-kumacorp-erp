from core.tests.brand.init_test_case import InitTestCase

class AuthenticationBrandTestCase(InitTestCase):
    def setUp(self):
        super().setUp()

    def test_crud(self):
        self._execute_crud_tests()
