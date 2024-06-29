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
        self.expected_fields = ['uuid', 'name', 'description']

    def test_create_brand_fails_without_field(self):
        for field in self.required_fields:
            self._test_field_validation(field=field, value=None)

    def test_create_brand_fails_with_blank_field(self):
        for field in self.required_fields:
            self._test_field_validation(field=field, value='')

    def test_create_brand_succeeds_with_valid_data(self):
        response = self._make_post_request(url=self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Expected 201 Created for successful creation")

        created_brand = Brand.objects.get(uuid=response.data['uuid'])
        self.assertIsNotNone(created_brand, "Should exist in database")

        for field in self.expected_fields:
            self.assertIn(field, response.data, f"Field {field} in response data")

            expected_value = getattr(created_brand, field)
            response_value = response.data[field]

            if field == 'uuid':
                self.assertEqual(str(expected_value), response_value, f"Expected {field} value to match response data")
            else:
                self.assertEqual(expected_value, self.data[field], f"Expected {field} value to match input data")
                self.assertEqual(expected_value, response_value, f"Expected {field} value to match response data")
                self.assertEqual(response_value, self.data[field], f"Expected response data {field} to match input data")
