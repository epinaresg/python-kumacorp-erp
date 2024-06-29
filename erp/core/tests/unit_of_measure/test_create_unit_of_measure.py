from rest_framework import status
from rest_framework.reverse import reverse
from core.models import UnitOfMeasure
from core.tests.base_test_case import BaseAPITestCase

class CreateUnitOfMeasureTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('unitofmeasure-list')
        self.data = self.get_unit_of_measure_data()
        self.required_fields = ['name', 'abbreviation']
        self.expected_fields = ['uuid', 'name', 'abbreviation']

    def _make_post_request(self, *, url, data):
        return self.make_request(method='post', url=url, data=data, access_token=self.access_token, company_uuid=self.company.uuid)

    def _test_field_validation(self, *, field, value):
        data = self.data.copy()
        if value is None:
            data.pop(field)
        else:
            data[field] = value

        response = self._make_post_request(url=self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, f"Expected 400 Bad Request for missing or blank {field}")
        self.assertIn(field, response.data, f"Field {field} in response data")

    def test_create_unit_of_measure_fails_without_field(self):
        for field in self.required_fields:
            self._test_field_validation(field=field, value=None)

    def test_create_unit_of_measure_fails_with_blank_field(self):
        for field in self.required_fields:
            self._test_field_validation(field=field, value='')

    def test_create_unit_of_measure_succeeds_with_valid_data(self):
        response = self._make_post_request(url=self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Expected 201 Created for successful creation")

        created_unit_of_measure = UnitOfMeasure.objects.get(uuid=response.data['uuid'])
        self.assertIsNotNone(created_unit_of_measure, "Should exist in database")

        for field in self.expected_fields:
            self.assertIn(field, response.data, f"Field {field} in response data")

            expected_value = getattr(created_unit_of_measure, field)
            response_value = response.data[field]

            if field == 'uuid':
                self.assertEqual(str(expected_value), response_value, f"Expected {field} value to match response data")
            else:
                self.assertEqual(expected_value, self.data[field], f"Expected {field} value to match input data")
                self.assertEqual(expected_value, response_value, f"Expected {field} value to match response data")
                self.assertEqual(response_value, self.data[field], f"Expected response data {field} to match input data")
