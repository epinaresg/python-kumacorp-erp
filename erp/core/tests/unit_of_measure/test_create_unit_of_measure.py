from rest_framework import status
from rest_framework.reverse import reverse
from authentication.models import CustomUser
from core.models import UnitOfMeasure
from core.tests.base_test_case import BaseAPITestCase

class CreateUnitOfMeasureTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('unitofmeasure-list')
        self.data = self.get_unit_of_measure_data()
        self.required_fields = ['name', 'abbreviation']

    def test_create_unit_of_measure_requires_authentication(self):
        response = self.make_request(method='post', url=self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, "Expected 401 Unauthorized for unauthenticated request")

    def test_create_unit_of_measure_requires_company_uuid(self):
        response = self.make_request(method='post', url=self.url, data=self.data, access_token=self.access_token)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found without company UUID header")

    def test_create_unit_of_measure_requires_company_uuid_from_logged_user(self):
        response = self.make_request(method='post', url=self.url, data=self.data, access_token=self.access_token, company_uuid=self.other_company.uuid)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found with company UUID not matching the logged user")

    def test_create_unit_of_measure_fails_without_field(self):
        for field in self.required_fields:
            data = self.data.copy()
            data.pop(field)

            response = self.make_request(method='post', url=self.url, data=data, access_token=self.access_token, company_uuid=self.company.uuid)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, f"Expected 400 Bad Request for missing {field}")
            self.assertIn(field, response.data, f"Field {field} missing in response data")

    def test_create_unit_of_measure_fails_with_blank_field(self):
        for field in self.required_fields:
            data = self.data.copy()
            data[field] = ''

            response = self.make_request(method='post', url=self.url, data=data, access_token=self.access_token, company_uuid=self.company.uuid)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, f"Expected 400 Bad Request for blank {field}")
            self.assertIn(field, response.data, f"Field {field} missing in response data")

    def test_create_unit_of_measure_succeeds_with_valid_data(self):
        response = self.make_request(method='post', url=self.url, data=self.data, access_token=self.access_token, company_uuid=self.company.uuid)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Expected 201 Created for successful creation")

        unit_of_measure = UnitOfMeasure.objects.get(uuid=response.data['uuid'])
        self.assertIsNotNone(unit_of_measure, "Should exist in database")

        expected_fields = ['uuid', 'name', 'abbreviation']
        for field in expected_fields:
            self.assertIn(field, response.data, f"Field {field} missing in response data")
            if (field != 'uuid'):
                self.assertEqual(getattr(unit_of_measure, field), self.data[field], f"Expected updated {field} to match input data")
                self.assertEqual(response.data[field], self.data[field], f"Expected response data {field} to match input data")
