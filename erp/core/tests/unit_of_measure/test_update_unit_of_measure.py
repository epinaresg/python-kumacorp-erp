import uuid
from rest_framework import status
from rest_framework.reverse import reverse
from core.models import UnitOfMeasure
from core.tests.base_test_case import BaseAPITestCase

class UpdateUnitOfMeasureTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.unit_of_measure = self.create_unit_of_measure(company=self.company)
        self.other_unit_of_measure = self.create_unit_of_measure(company=self.other_company)
        self.url = reverse('unitofmeasure-detail', kwargs={'uuid': self.unit_of_measure.uuid})
        self.data = self.get_unit_of_measure_data()
        self.required_fields = ['name', 'abbreviation']
        self.expected_fields = ['uuid', 'name', 'abbreviation']

    def _test_field_validation(self, *, field, value):
        data = self.data.copy()
        if value is None:
            data.pop(field)
        else:
            data[field] = value

        response = self._make_put_request(url=self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, f"Expected 400 Bad Request for {"missing" if value is None else "blank"} {field}")
        self.assertIn(field, response.data, f"Field {field} in response data")

    def test_update_unit_of_measure_fails_without_field(self):
        for field in self.required_fields:
            self._test_field_validation(field=field, value=None)

    def test_update_unit_of_measure_fails_with_blank_field(self):
        for field in self.required_fields:
            self._test_field_validation(field=field, value='')

    def test_update_unit_of_measure_fails_with_invalid_uuid(self):
        invalid_uuid = uuid.uuid4()
        url = reverse('unitofmeasure-detail', kwargs={'uuid': invalid_uuid})

        response = self._make_put_request(url=url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found for invalid UUID")

    def test_update_unit_of_measure_fails_with_valid_uuid_from_another_company(self):
        url = reverse('unitofmeasure-detail', kwargs={'uuid': self.other_unit_of_measure.uuid})

        response = self._make_put_request(url=url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found for UUID from another company")

    def test_update_unit_of_measure_succeeds_with_valid_data(self):
        response = self._make_put_request(url=self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Expected 200 OK for successful update")

        updated_unit_of_measure = UnitOfMeasure.objects.get(uuid=response.data['uuid'])
        self.assertIsNotNone(updated_unit_of_measure, "Should exist in database")

        for field in self.expected_fields:
            self.assertIn(field, response.data, f"Field {field} in response data")

            expected_value = getattr(updated_unit_of_measure, field)
            response_value = response.data[field]

            if field == 'uuid':
                self.assertEqual(str(expected_value), response_value, f"Expected {field} value to match response data")
            else:
                self.assertEqual(expected_value, self.data[field], f"Expected {field} value to match input data")
                self.assertEqual(expected_value, response_value, f"Expected {field} value to match response data")
                self.assertEqual(response_value, self.data[field], f"Expected response data {field} to match input data")
