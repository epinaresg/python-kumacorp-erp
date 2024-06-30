from rest_framework import status
from core.tests.base_api_test_case import BaseAPITestCase
from abc import ABC, abstractmethod


class AuthenticationApiTestCase(BaseAPITestCase, ABC):
    def setUp(self):
        super().setUp()

    @abstractmethod
    def _get_requests(self):
        pass

    def _execute_authentication_tests(self):
        self._test_requires_authentication()

        self._test_requires_company_uuid()

        self._test_requires_company_uuid_from_logged_user()

    def _test_requires_authentication(self):
        for method, url, data in self._get_requests():
            response = self._make_request(method=method, url=url, data=data)
            self.assertEqual(
                response.status_code,
                status.HTTP_401_UNAUTHORIZED,
                "Expected 401 Unauthorized for unauthenticated request",
            )

    def _test_requires_company_uuid(self):
        for method, url, data in self._get_requests():
            response = self._make_request(
                method=method, url=url, data=data, access_token=self.access_token
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_404_NOT_FOUND,
                "Expected 404 Not Found without company UUID header",
            )

    def _test_requires_company_uuid_from_logged_user(self):
        for method, url, data in self._get_requests():
            response = self._make_request(
                method=method,
                url=url,
                data=data,
                access_token=self.access_token,
                company_uuid=self.other_company.uuid,
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_404_NOT_FOUND,
                "Expected 404 Not Found with company UUID not matching the logged user",
            )
