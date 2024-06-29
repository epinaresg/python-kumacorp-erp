from rest_framework import status
from rest_framework.reverse import reverse
from core.tests.base_test_case import BaseAPITestCase

class BaseUnitOfMeasureTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.unit_of_measure = self.create_unit_of_measure(company=self.company)
        self.requests = [
            ('post', reverse('unitofmeasure-list'), self.get_unit_of_measure_data()),
            ('put', reverse('unitofmeasure-detail', kwargs={'uuid': self.unit_of_measure.uuid}), self.get_unit_of_measure_data()),
            ('delete', reverse('unitofmeasure-detail', kwargs={'uuid': self.unit_of_measure.uuid}), None),
            ('get', reverse('unitofmeasure-detail', kwargs={'uuid': self.unit_of_measure.uuid}), None),
            ('get', reverse('unitofmeasure-list'), None),
        ]

    def test_base_unit_of_measure_requires_authentication(self):
        for method, url, data in self.requests:
            response = self.make_request(method=method, url=url, data=data)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, "Expected 401 Unauthorized for unauthenticated request")

    def test_base_unit_of_measure_requires_company_uuid(self):
        for method, url, data in self.requests:
            response = self.make_request(method=method, url=url, data=data, access_token=self.access_token)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found without company UUID header")

    def test_base_unit_of_measure_requires_company_uuid_from_logged_user(self):
        for method, url, data in self.requests:
            response = self.make_request(method=method, url=url, data=data, access_token=self.access_token, company_uuid=self.other_company.uuid)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found with company UUID not matching the logged user")
