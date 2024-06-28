from rest_framework import status
from rest_framework.reverse import reverse
from core.tests.base_test_case import BaseAPITestCase

class BaseBrandTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.brand = self.create_brand(company=self.company)
        self.requests = [
            ('post', reverse('brand-list'), self.get_brand_data()),
            ('put', reverse('brand-detail', kwargs={'uuid': self.brand.uuid}), self.get_brand_data()),
            ('delete', reverse('brand-detail', kwargs={'uuid': self.brand.uuid}), None),
            ('get', reverse('brand-detail', kwargs={'uuid': self.brand.uuid}), None),
            ('get', reverse('brand-list'), None),
        ]

    def test_base_brand_requires_authentication(self):
        for method, url, data in self.requests:
            response = self.make_request(method=method, url=url, data=data)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, "Expected 401 Unauthorized for unauthenticated request")

    def test_base_brand_requires_company_uuid(self):
        for method, url, data in self.requests:
            response = self.make_request(method=method, url=url, data=data, access_token=self.access_token)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found without company UUID header")

    def test_base_brand_requires_company_uuid_from_logged_user(self):
        for method, url, data in self.requests:
            response = self.make_request(method=method, url=url, data=data, access_token=self.access_token, company_uuid=self.other_company.uuid)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found with company UUID not matching the logged user")
