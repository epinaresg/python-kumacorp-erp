from rest_framework import status
from core.tests.request_test_case import RequestAPITestCase

class AuthenticationApiTestCase(RequestAPITestCase):
    def setUp(self):
        super().setUp()

    def _execute_authentication_tests(self, *, requests):
        self._test_requires_authentication(requests=requests)
        self._test_requires_company_uuid(requests=requests)
        self._test_requires_company_uuid_from_logged_user(requests=requests)

    def _test_requires_authentication(self, *, requests):
        for method, url, data in requests:
            response = self._make_request(method=method, url=url, data=data)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, "Expected 401 Unauthorized for unauthenticated request")

    def _test_requires_company_uuid(self, *, requests):
        for method, url, data in requests:
            response = self._make_request(method=method, url=url, data=data, access_token=self.access_token)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found without company UUID header")

    def _test_requires_company_uuid_from_logged_user(self, *, requests):
        for method, url, data in requests:
            response = self._make_request(method=method, url=url, data=data, access_token=self.access_token, company_uuid=self.other_company.uuid)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found with company UUID not matching the logged user")
