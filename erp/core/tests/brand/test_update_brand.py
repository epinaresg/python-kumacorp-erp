import uuid
from rest_framework import status
from rest_framework.reverse import reverse
from authentication.models import CustomUser
from core.models import Brand, Company
from core.tests.base_test_case import BaseAPITestCase

class UpdateBrandTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.brand = self.create_brand(company=self.company)
        self.other_brand = self.create_brand(company=self.other_company)
        self.url = reverse('brand-detail', kwargs={'uuid': self.brand.uuid})
        self.data = self.get_brand_data()
        self.required_fields = ['name']

    def _test_field_validation(self, field, value, expected_status, error_msg):
        data = self.data.copy()
        if value is None:
            data.pop(field)
        else:
            data[field] = value

        response = self.make_request(method='put', url=self.url, data=data, access_token=self.access_token, company_uuid=self.company.uuid)
        self.assertEqual(response.status_code, expected_status, error_msg)
        self.assertIn(field, response.data, f"Field {field} missing in response data")

    def test_update_brand_fails_without_field(self):
        for field in self.required_fields:
            self._test_field_validation(field, None, status.HTTP_400_BAD_REQUEST, f"Expected 400 Bad Request for missing {field}")

    def test_update_brand_fails_with_blank_field(self):
        for field in self.required_fields:
            self._test_field_validation(field, '', status.HTTP_400_BAD_REQUEST, f"Expected 400 Bad Request for blank {field}")

    def test_update_brand_fails_with_invalid_uuid(self):
        invalid_uuid = uuid.uuid4()
        url = reverse('brand-detail', kwargs={'uuid': invalid_uuid})

        response = self.make_request(method='put', url=url, data=self.data, access_token=self.access_token, company_uuid=self.company.uuid)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found for invalid UUID")

    def test_update_brand_fails_with_valid_uuid_from_another_company(self):
        url = reverse('brand-detail', kwargs={'uuid': self.other_brand.uuid})

        response = self.make_request(method='put', url=url, data=self.data, access_token=self.access_token, company_uuid=self.company.uuid)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found for UUID from another company")

    def test_update_brand_succeeds_with_valid_data(self):
        response = self.make_request(method='put', url=self.url, data=self.data, access_token=self.access_token, company_uuid=self.company.uuid)
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Expected 200 OK for successful update")

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
