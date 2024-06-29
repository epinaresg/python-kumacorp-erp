import uuid
from rest_framework import status
from rest_framework.reverse import reverse
from core.models import Brand
from core.tests.base_test_case import BaseAPITestCase

class UpdateBrandTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.brand = self.create_brand(company=self.company)
        self.other_brand = self.create_brand(company=self.other_company)
        self.url = reverse('brand-detail', kwargs={'uuid': self.brand.uuid})
        self.data = self.get_brand_data()
        self.required_fields = ['name']
        self.expected_fields = ['uuid', 'name', 'description']

    def _make_put_request(self, *, url, data):
        return self.make_request(method='put', url=url, data=data, access_token=self.access_token, company_uuid=self.company.uuid)

    def _test_field_validation(self, *, field, value):
        data = self.data.copy()
        if value is None:
            data.pop(field)
        else:
            data[field] = value

        response = self._make_put_request(url=self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, f"Expected 400 Bad Request for {"missing" if value is None else "blank"} {field}")
        self.assertIn(field, response.data, f"Field {field} in response data")

    def test_update_brand_fails_without_field(self):
        for field in self.required_fields:
            self._test_field_validation(field=field, value=None)

    def test_update_brand_fails_with_blank_field(self):
        for field in self.required_fields:
            self._test_field_validation(field=field, value='')

    def test_update_brand_fails_with_invalid_uuid(self):
        invalid_uuid = uuid.uuid4()
        url = reverse('brand-detail', kwargs={'uuid': invalid_uuid})

        response = self._make_put_request(url=url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found for invalid UUID")

    def test_update_brand_fails_with_valid_uuid_from_another_company(self):
        url = reverse('brand-detail', kwargs={'uuid': self.other_brand.uuid})

        response = self._make_put_request(url=url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found for UUID from another company")

    def test_update_brand_succeeds_with_valid_data(self):
        response = self._make_put_request(url=self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Expected 200 OK for successful update")

        updated_brand = Brand.objects.get(uuid=response.data['uuid'])
        self.assertIsNotNone(updated_brand, "Should exist in database")

        for field in self.expected_fields:
            self.assertIn(field, response.data, f"Field {field} in response data")

            expected_value = getattr(updated_brand, field)
            response_value = response.data[field]

            if field == 'uuid':
                self.assertEqual(str(expected_value), response_value, f"Expected {field} value to match response data")
            else:
                self.assertEqual(expected_value, self.data[field], f"Expected {field} value to match input data")
                self.assertEqual(expected_value, response_value, f"Expected {field} value to match response data")
                self.assertEqual(response_value, self.data[field], f"Expected response data {field} to match input data")
