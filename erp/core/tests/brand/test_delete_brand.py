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

    def test_delete_brand_fails_with_invalid_uuid(self):
        invalid_uuid = uuid.uuid4()
        url = reverse('brand-detail', kwargs={'uuid': invalid_uuid})

        response = self._make_delete_request(url=url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found with invalid UUID")

    def test_delete_brand_fails_with_valid_uuid_from_another_company(self):
        url = reverse('brand-detail', kwargs={'uuid': self.other_brand.uuid})

        response = self._make_delete_request(url=url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found with UUID belonging to another company")

    def test_delete_brand_succeeds(self):
        response = self._make_delete_request(url=self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, "Expected 204 No Content on successful delete")

        with self.assertRaises(Brand.DoesNotExist):
            Brand.objects.get(uuid=self.brand.uuid)
