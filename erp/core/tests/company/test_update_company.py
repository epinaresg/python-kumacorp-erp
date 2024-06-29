from rest_framework import status
from rest_framework.reverse import reverse
from authentication.models import CustomUser
from core.models import Company
from core.tests.base_test_case import BaseAPITestCase


class UpdateCompanyTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("company-detail", kwargs={"uuid": self.company.uuid})
        self.company_data = {
            "name": "Updated Test company",
        }
        self.required_fields = ["name"]

    def test_update_company_requires_authentication(self):
        response = self.client.put(self.url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Expected 401 Unauthorized for unauthenticated company update",
        )

    def test_update_company_fails_without_field(self):
        for field in self.required_fields:
            data = self.company_data.copy()
            data.pop(field)

            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
            response = self.client.put(self.url, data, format="json")
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
                f"Expected 400 Bad Request for missing field: {field}",
            )
            self.assertIn(
                field,
                response.data,
                f"Expected '{field}' in response data for bad request",
            )

    def test_update_company_fails_with_blank_field(self):
        for field in self.required_fields:
            data = self.company_data.copy()
            data[field] = ""

            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
            response = self.client.put(self.url, data, format="json")
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
                f"Expected 400 Bad Request for blank field: {field}",
            )
            self.assertIn(
                field,
                response.data,
                f"Expected '{field}' in response data for bad request",
            )

    def test_update_company_succeeds_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.put(self.url, self.company_data, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Expected 200 OK for successful company update",
        )

        expected_fields = ["uuid", "name", "settings"]
        for field in expected_fields:
            self.assertIn(field, response.data, f"Expected '{field}' in response data")

        company = Company.objects.get(uuid=response.data["uuid"])
        self.assertIsNotNone(company, "Company should exist in database")
        self.assertEqual(
            response.data["name"],
            self.company_data["name"],
            "Expected updated name in response",
        )
        self.assertNotEqual(
            response.data["name"],
            self.company.name,
            "Expected name to be updated in database",
        )
        self.assertEqual(
            str(company.uuid),
            str(self.company.uuid),
            "Expected updated company UUID to match original company UUID",
        )
