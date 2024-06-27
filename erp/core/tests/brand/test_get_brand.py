import uuid
import random
from rest_framework import status
from rest_framework.reverse import reverse
from authentication.models import CustomUser
from core.models import Brand, Company
from core.tests.base_test_case import BaseAPITestCase

class GetBrandTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.brands_qty = random.choice([1, 50])
        for x in range(self.brands_qty):
            self.create_brand(company=self.company)

        self.brand = self.create_brand(company=self.company)
        self.brands_qty += 1

        self.other_brand = self.create_brand(company=self.other_company)
        self.url_list = reverse('brand-list')
        self.url_detail = reverse('brand-detail', kwargs={'uuid': self.brand.uuid})

    def test_get_list_brand_requires_authentication(self):
        response = self.make_request(method='get', url=self.url_list)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, "Expected 401 Unauthorized for unauthenticated request")

    def test_get_detail_brand_requires_authentication(self):
        response = self.make_request(method='get', url=self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, "Expected 401 Unauthorized for unauthenticated request")

    def test_get_list_requires_company_uuid(self):
        response = self.make_request(method='get', url=self.url_list, data=None, access_token=self.access_token)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found without company UUID header")

    def test_get_detail_brand_requires_company_uuid(self):
        response = self.make_request(method='get', url=self.url_detail, data=None, access_token=self.access_token)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found without company UUID header")

    def test_get_list_brand_requires_company_uuid_from_logged_user(self):
        response = self.make_request(method='get', url=self.url_list, data=None, access_token=self.access_token, company_uuid=self.other_company.uuid)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found with company UUID not matching the logged user")

    def test_get_detail_brand_requires_company_uuid_from_logged_user(self):
        response = self.make_request(method='get', url=self.url_detail, data=None, access_token=self.access_token, company_uuid=self.other_company.uuid)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found with company UUID not matching the logged user")


    def test_get_detail_brand_fails_with_invalid_uuid(self):
        invalid_uuid = uuid.uuid4()
        url = reverse('brand-detail', kwargs={'uuid': invalid_uuid})

        response = self.make_request(method='get', url=url, data=None, access_token=self.access_token, company_uuid=self.company.uuid)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found with invalid UUID")

    def test_get_detail_brand_fails_with_valid_uuid_from_another_company(self):
        url = reverse('brand-detail', kwargs={'uuid': self.other_brand.uuid})

        response = self.make_request(method='get', url=url, data=None, access_token=self.access_token, company_uuid=self.company.uuid)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found with UUID belonging to another company")

    def test_get_detail_brand_succeeds(self):
        response = self.make_request(method='get', url=url, data=None, access_token=self.access_token, company_uuid=self.company.uuid)
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Expected 200 Ok on successful get detail")

        with self.assertRaises(Brand.DoesNotExist):
            Brand.objects.get(uuid=self.brand.uuid)
