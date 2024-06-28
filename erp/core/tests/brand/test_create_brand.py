from rest_framework import status
from rest_framework.reverse import reverse
from core.models import Brand
from core.tests.base_test_case import BaseAPITestCase

class CreateBrandTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('brand-list')
        self.data = self.get_brand_data()
        self.required_fields = ['name']

    def _test_field_validation(self, field, value):
        data = self.data.copy()
        if value is None:
            data.pop(field)
        else:
            data[field] = value

        response = self.make_request(method='post', url=self.url, data=data, access_token=self.access_token, company_uuid=self.company.uuid)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, f"Expected 400 Bad Request for missing {field}")
        self.assertIn(field, response.data, f"Field {field} missing in response data")

    def test_create_brand_fails_without_field(self):
        for field in self.required_fields:
            self._test_field_validation(field, None, status.HTTP_400_BAD_REQUEST, f"Expected 400 Bad Request for missing {field}")

    def test_create_brand_fails_with_blank_field(self):
        for field in self.required_fields:
            self._test_field_validation(field, '', status.HTTP_400_BAD_REQUEST, f"Expected 400 Bad Request for blank {field}")

    def test_create_brand_succeeds_with_valid_data(self):
        response = self.make_request(method='post', url=self.url, data=self.data, access_token=self.access_token, company_uuid=self.company.uuid)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Expected 201 Created for successful creation")

        brand = Brand.objects.get(uuid=response.data['uuid'])
        self.assertIsNotNone(brand, "Should exist in database")

        expected_fields = ['uuid', 'name', 'description']
        for field in expected_fields:
            self.assertIn(field, response.data, f"Field {field} in response data")
            if (field != 'uuid'):
                self.assertEqual(getattr(brand, field), self.data[field], f"Expected updated {field} to match input data")
                self.assertEqual(response.data[field], self.data[field], f"Expected response data {field} to match input data")
                self.assertEqual(getattr(brand, field), response.data[field], f"Expected updated {field} to match response data")
            else:
                self.assertEqual(str(getattr(brand, field)), str(response.data[field]), f"Expected updated {field} to match response data")
