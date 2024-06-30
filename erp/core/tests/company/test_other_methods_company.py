from rest_framework import status
from rest_framework.reverse import reverse
from core.tests.base_api_test_case import BaseAPITestCase


class OtherMethodsCompanyTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()

        self.url_list = reverse("company-list")
        self.url_detail = reverse("company-detail", kwargs={"uuid": self.company.uuid})

    def test_other_methods_list_requires_authentication(self):
        response = self.client.get(self.url_list)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Expected 401 Unauthorized for unauthenticated list request",
        )

    def test_other_methods_detail_requires_authentication(self):
        response = self.client.get(self.url_detail)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Expected 401 Unauthorized for unauthenticated detail request",
        )

    def test_other_methods_delete_requires_authentication(self):
        response = self.client.delete(self.url_detail)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Expected 401 Unauthorized for unauthenticated delete request",
        )

    def test_other_methods_list_not_allowed(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(self.url_list)
        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
            "Expected 405 Method Not Allowed for list view with authenticated user",
        )

    def test_other_methods_detail_not_allowed(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(self.url_detail)
        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
            "Expected 405 Method Not Allowed for detail view with authenticated user",
        )

    def test_other_methods_delete_not_allowed(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.delete(self.url_detail)
        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
            "Expected 405 Method Not Allowed for delete view with authenticated user",
        )
