import uuid
from rest_framework import status
from rest_framework.reverse import reverse
from authentication.models import CustomUser
from core.models import Brand, Company
from core.tests.base_test_case import BaseAPITestCase

class UpdateBrandTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.brand = self.create_brand(company=self.company, name='Original Test brand')
        self.other_brand = self.create_brand(company=self.other_company, name='Original Other Test brand')

        self.url = reverse('brand-detail', kwargs={'uuid': self.brand.uuid})
        self.brand_data = {
            'name': 'Updated Test brand',
        }
        self.required_fields = ['name']

    def test_update_brand_requires_authentication(self):
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, "Expected 401 Unauthorized for unauthenticated request")

    def test_update_brand_requires_company_uuid(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.put(self.url, self.brand_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found without company UUID header")

    def test_update_brand_requires_company_uuid_from_logged_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}', HTTP_X_COMPANY_UUID=self.other_company.uuid)
        response = self.client.put(self.url, self.brand_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found with company UUID not matching the logged user")

    def test_update_brand_fails_without_field(self):
        for field in self.required_fields:
            data = self.brand_data.copy()
            data.pop(field)

            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}', HTTP_X_COMPANY_UUID=self.company.uuid)
            response = self.client.put(self.url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, f"Expected 400 Bad Request for missing {field}")
            self.assertIn(field, response.data, f"Field {field} missing in response data")

    def test_update_brand_fails_with_blank_field(self):
        for field in self.required_fields:
            data = self.brand_data.copy()
            data[field] = ''

            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}', HTTP_X_COMPANY_UUID=self.company.uuid)
            response = self.client.put(self.url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, f"Expected 400 Bad Request for blank {field}")
            self.assertIn(field, response.data, f"Field {field} missing in response data")

    def test_update_brand_fails_with_invalid_uuid(self):
        invalid_uuid = uuid.uuid4()
        url = reverse('brand-detail', kwargs={'uuid': invalid_uuid})

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}', HTTP_X_COMPANY_UUID=self.company.uuid)
        response = self.client.put(url, self.brand_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found for invalid UUID")

    def test_update_brand_fails_with_valid_uuid_from_another_company(self):
        url = reverse('brand-detail', kwargs={'uuid': self.other_brand.uuid})

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}', HTTP_X_COMPANY_UUID=self.company.uuid)
        response = self.client.put(url, self.brand_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found for UUID from another company")

    def test_update_brand_succeeds_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}', HTTP_X_COMPANY_UUID=self.company.uuid)
        response = self.client.put(self.url, self.brand_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Expected 200 OK for successful update")

        brand = Brand.objects.get(uuid=response.data['uuid'])
        self.assertIsNotNone(brand, "Brand should exist in database")

        expected_fields = ['uuid', 'name']
        for field in expected_fields:
            self.assertIn(field, response.data, f"Field {field} missing in response data")
            if (field != 'uuid'):
                self.assertEqual(getattr(brand, field), self.brand_data[field], f"Expected updated {field} to match input data")
                self.assertEqual(response.data[field], self.brand_data[field], f"Expected response data {field} to match input data")

        self.assertEqual(str(brand.uuid), str(self.brand.uuid), "Expected updated UUID to match original UUID")
