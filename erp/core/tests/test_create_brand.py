from rest_framework import status
from rest_framework.reverse import reverse
from authentication.models import CustomUser
from core.models import Brand
from core.tests.base_test_case import BaseAPITestCase

class CreateBrandTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('brand-list')
        self.brand_data = {
            'name': 'Test brand',
        }
        self.required_fields = ['name']

    def test_create_brand_requires_authentication(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, "Expected 401 Unauthorized for unauthenticated request")

    def test_create_brand_requires_company_uuid(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(self.url, self.brand_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found without company UUID header")

    def test_create_brand_requires_company_uuid_from_logged_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}', HTTP_X_COMPANY_UUID=self.other_company.uuid)
        response = self.client.post(self.url, self.brand_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found with company UUID not matching the logged user")

    def test_create_brand_fails_without_field(self):
        for field in self.required_fields:
            data = self.brand_data.copy()
            data.pop(field)

            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}', HTTP_X_COMPANY_UUID=self.company.uuid)
            response = self.client.post(self.url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, f"Expected 400 Bad Request for missing {field}")
            self.assertIn(field, response.data, f"Field {field} missing in response data")

    def test_create_brand_fails_with_blank_field(self):
        for field in self.required_fields:
            data = self.brand_data.copy()
            data[field] = ''

            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}', HTTP_X_COMPANY_UUID=self.company.uuid)
            response = self.client.post(self.url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, f"Expected 400 Bad Request for blank {field}")
            self.assertIn(field, response.data, f"Field {field} missing in response data")

    def test_create_brand_succeeds_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}', HTTP_X_COMPANY_UUID=self.company.uuid)
        response = self.client.post(self.url, self.brand_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Expected 201 Created for successful brand creation")

        expected_fields = ['uuid', 'name']
        for field in expected_fields:
            self.assertIn(field, response.data, f"Field {field} missing in response data")

        brand = Brand.objects.get(uuid=response.data['uuid'])
        self.assertIsNotNone(brand, "Brand should exist in database")
        self.assertEqual(brand.name, self.brand_data['name'], "Expected created brand name to match input data")
        self.assertEqual(response.data['name'], self.brand_data['name'], "Expected response data name to match input data")
