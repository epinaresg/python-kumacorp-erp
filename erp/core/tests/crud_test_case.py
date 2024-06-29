import logging

from rest_framework import status
from core.tests.request_test_case import RequestAPITestCase

class CRUDApiTestCase(RequestAPITestCase):
    def setUp(self):
        super().setUp()
        self.logger = logging.getLogger('django.test')

    def _execute_crud_tests(self):
        self._test_create_fails_without_field()
        self._test_create_fails_with_blank_field()
        self._test_create_succeeds_with_valid_data()

        self._test_update_fails_without_field()
        self._test_update_fails_with_blank_field()
        self._test_update_fails_with_invalid_uuid()
        self._test_update_fails_with_valid_uuid_from_another_company()
        self._test_update_succeeds_with_valid_data()

    def _test_field_validation(self, *, method, field, value):
        data = self.get_instance_data_fn().copy()
        if value is None:
            data.pop(field)
        else:
            data[field] = value

        if (method == 'post'):
            response = self._make_post_request(url=self.create_url, data=data)
        elif (method == 'put'):
            response = self._make_put_request(url=self.update_url, data=data)
        else:
            raise ValueError(f"Unsupported method: {method}")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, f"Expected 400 Bad Request for {"missing" if value is None else "blank"} {field}")
        self.assertIn(field, response.data, f"Field {field} in response data")

    ###### BEGIN - CREATE TEST ######

    def _test_create_fails_without_field(self):
        for field in self.required_fields:
            self._test_field_validation(method='post', field=field, value=None)
        self.logger.info('_test_create_fails_without_field passed')

    def _test_create_fails_with_blank_field(self):
        for field in self.required_fields:
            self._test_field_validation(method='post', field=field, value='')
        self.logger.info('_test_create_fails_with_blank_field passed')

    def _test_create_succeeds_with_valid_data(self):
        data = self.get_instance_data_fn()
        response = self._make_post_request(url=self.create_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Expected 201 Created for successful creation")

        created_instance = self.model_class.objects.get(uuid=response.data['uuid'])
        self.assertIsNotNone(created_instance, "Should exist in database")

        for field in self.expected_fields:
            self.assertIn(field, response.data, f"Field {field} in response data")

            expected_value = getattr(created_instance, field)
            response_value = response.data[field]

            if field == 'uuid':
                self.assertEqual(str(expected_value), response_value, f"Expected {field} value to match response data")
            else:
                self.assertEqual(expected_value, data[field], f"Expected {field} value to match input data")
                self.assertEqual(expected_value, response_value, f"Expected {field} value to match response data")
                self.assertEqual(response_value, data[field], f"Expected response data {field} to match input data")
        self.logger.info('_test_create_succeeds_with_valid_data passed')

    ###### END - CREATE TEST ######

    ###### BEGIN - UPDATE TEST ######

    def _test_update_fails_without_field(self):
        for field in self.required_fields:
            self._test_field_validation(method='put', field=field, value=None)
        self.logger.info('_test_update_fails_without_field passed')

    def _test_update_fails_with_blank_field(self):
        for field in self.required_fields:
            self._test_field_validation(method='put', field=field, value='')
        self.logger.info('_test_update_fails_with_blank_field passed')

    def _test_update_fails_with_invalid_uuid(self):
        data = self.get_instance_data_fn()
        response = self._make_put_request(url=self.invalid_uuid_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found for invalid UUID")
        self.logger.info('_test_update_fails_with_invalid_uuid passed')

    def _test_update_fails_with_valid_uuid_from_another_company(self):
        data = self.get_instance_data_fn()
        response = self._make_put_request(url=self.other_company_update_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found for UUID from another company")
        self.logger.info('_test_update_fails_with_valid_uuid_from_another_company passed')

    def _test_update_succeeds_with_valid_data(self):
        data = self.get_instance_data_fn()
        response = self._make_put_request(url=self.update_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Expected 200 OK for successful update")

        updated_instance = self.model_class.objects.get(uuid=response.data['uuid'])
        self.assertIsNotNone(updated_instance, "Should exist in database")

        for field in self.expected_fields:
            self.assertIn(field, response.data, f"Field {field} in response data")

            expected_value = getattr(updated_instance, field)
            response_value = response.data[field]

            if field == 'uuid':
                self.assertEqual(str(expected_value), response_value, f"Expected {field} value to match response data")
            else:
                self.assertEqual(expected_value, data[field], f"Expected {field} value to match input data")
                self.assertEqual(expected_value, response_value, f"Expected {field} value to match response data")
                self.assertEqual(response_value, data[field], f"Expected response data {field} to match input data")
        self.logger.info('_test_update_succeeds_with_valid_data passed')

    ###### END - UPDATE TEST ######
