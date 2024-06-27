import uuid
from rest_framework import status
from rest_framework.reverse import reverse
from authentication.models import CustomUser
from core.models import Brand, Company
from core.tests.base_test_case import BaseAPITestCase

class UpdateBrandTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.brand = Brand.objects.create(company=self.company, name='Original Test brand')
        self.other_brand = Brand.objects.create(company=self.other_company, name='Original Other Test brand')
        self.url = reverse('brand-detail', kwargs={'uuid': self.brand.uuid})

    def test_delete_brand_requires_authentication(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, "Expected 401 Unauthorized for unauthenticated request")

    def test_delete_brand_requires_company_uuid(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found without company UUID header")

    def test_delete_brand_requires_company_uuid_from_logged_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}', HTTP_X_COMPANY_UUID=self.other_company.uuid)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found with company UUID not matching the logged user")

    def test_delete_brand_fails_with_invalid_uuid(self):
        invalid_uuid = uuid.uuid4()
        url = reverse('brand-detail', kwargs={'uuid': invalid_uuid})

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}', HTTP_X_COMPANY_UUID=self.company.uuid)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found with invalid brand UUID")

    def test_delete_brand_fails_with_valid_uuid_from_another_company(self):
        url = reverse('brand-detail', kwargs={'uuid': self.other_brand.uuid})

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}', HTTP_X_COMPANY_UUID=self.company.uuid)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found with brand UUID belonging to another company")

    def test_delete_brand_succeeds(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}', HTTP_X_COMPANY_UUID=self.company.uuid)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, "Expected 204 No Content on successful delete")

        with self.assertRaises(Brand.DoesNotExist):
            Brand.objects.get(uuid=self.brand.uuid)
