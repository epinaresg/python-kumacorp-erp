import math
import random
from abc import ABC, abstractmethod
from rest_framework import status
from core.tests.request_api_test_case import RequestAPITestCase

class CRUDApiTestCase(RequestAPITestCase, ABC):
    def setUp(self):
        super().setUp()

    @abstractmethod
    def _get_instance_data(self):
        pass

    @abstractmethod
    def _create_instance(self, *, company):
        pass

    @abstractmethod
    def _generate_create_url(self):
        pass

    @abstractmethod
    def _generate_update_url(self, *, instance=None):
        pass

    @abstractmethod
    def _generate_delete_url(self, *, instance=None):
        pass

    @abstractmethod
    def _generate_detail_url(self, *, instance=None):
        pass

    @abstractmethod
    def _generate_list_url(self):
        pass

    @abstractmethod
    def _get_model_class(self):
        pass

    @abstractmethod
    def _get_required_fields(self):
        pass

    @abstractmethod
    def _get_expected_fields(self):
        pass

    def _execute_crud_tests(self):
        self._test_create_fails_without_field()
        self.logger.info('=== _test_create_fails_without_field - passed')
        self._test_create_fails_with_blank_field()
        self.logger.info('=== _test_create_fails_with_blank_field - passed')
        self._test_create_succeeds_with_valid_data()
        self.logger.info('=== _test_create_succeeds_with_valid_data - passed')


        self._test_update_fails_without_field()
        self.logger.info('=== _test_update_fails_without_field - passed')
        self._test_update_fails_with_blank_field()
        self.logger.info('=== _test_update_fails_with_blank_field - passed')
        self._test_update_fails_with_invalid_uuid()
        self.logger.info('=== _test_update_fails_with_invalid_uuid - passed')
        self._test_update_fails_with_valid_uuid_from_another_company()
        self.logger.info('=== _test_update_fails_with_valid_uuid_from_another_company - passed')
        self._test_update_succeeds_with_valid_data()
        self.logger.info('=== _test_update_succeeds_with_valid_data - passed')


        self._test_delete_fails_with_invalid_uuid()
        self.logger.info('=== _test_delete_fails_with_invalid_uuid - passed')
        self._test_delete_fails_with_valid_uuid_from_another_company()
        self.logger.info('=== _test_delete_fails_with_valid_uuid_from_another_company - passed')
        self._test_delete_succeeds()
        self.logger.info('=== _test_delete_succeeds - passed')


        self._test_get_detail_fails_with_invalid_uuid()
        self.logger.info('=== _test_get_detail_fails_with_invalid_uuid - passed')
        self._test_get_detail_fails_with_valid_uuid_from_another_company()
        self.logger.info('=== _test_get_detail_fails_with_valid_uuid_from_another_company - passed')
        self._test_get_detail_succeeds()
        self.logger.info('=== _test_get_detail_succeeds - passed')

    def _test_field_validation(self, *, method, field, value):
        data = self._get_instance_data().copy()
        if value is None:
            data.pop(field)
        else:
            data[field] = value

        if (method == 'post'):
            response = self._make_post_request(url=self._generate_create_url(), data=data)
        elif (method == 'put'):
            response = self._make_put_request(url=self._generate_update_url(), data=data)
        else:
            raise ValueError(f"Unsupported method: {method}")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, f"Expected 400 Bad Request for {"missing" if value is None else "blank"} {field}")
        self.assertIn(field, response.data, f"Field {field} in response data")

    def _test_response_structure_pagination(self, *, data, count, num_pages, result_len):
        expected_fields = ['count', 'num_pages', 'next', 'previous', 'results']
        for field in expected_fields:
            self.assertIn(field, data, f"Field {field} in response data")

        self.assertEqual(data['count'], count, "Expected count value to match")
        self.assertEqual(data['num_pages'], num_pages, "Expected num_pages value to match")
        self.assertEqual(len(data['results']), result_len, "Expected valid results length")

        for sample in data['results']:
            self._test_response_structure_item(data=sample)

    def _test_response_structure_item(self, *, data):
        instance = self._get_model_class().objects.get(uuid=data['uuid'])
        for field in self._get_expected_fields():
            self.assertIn(field, data, f"Field {field} in result sample")
            expected_value = str(getattr(instance, field)) if field == 'uuid' else getattr(instance, field)
            self.assertEqual(data[field], expected_value, f"Expected {field} to match in result sample")

    ###### BEGIN - CREATE TEST ######

    def _test_create_fails_without_field(self):
        for field in self._get_required_fields():
            self._test_field_validation(method='post', field=field, value=None)

    def _test_create_fails_with_blank_field(self):
        for field in self._get_required_fields():
            self._test_field_validation(method='post', field=field, value='')

    def _test_create_succeeds_with_valid_data(self):
        data = self._get_instance_data()
        response = self._make_post_request(url=self._generate_create_url(), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Expected 201 Created for successful creation")

        created_instance = self.model_class.objects.get(uuid=response.data['uuid'])
        self.assertIsNotNone(created_instance, "Should exist in database")

        for field in self._get_expected_fields():
            self.assertIn(field, response.data, f"Field {field} in response data")

            expected_value = getattr(created_instance, field)
            response_value = response.data[field]

            if field == 'uuid':
                self.assertEqual(str(expected_value), response_value, f"Expected {field} value to match response data")
            else:
                self.assertEqual(expected_value, data[field], f"Expected {field} value to match input data")
                self.assertEqual(expected_value, response_value, f"Expected {field} value to match response data")
                self.assertEqual(response_value, data[field], f"Expected response data {field} to match input data")

    ###### END - CREATE TEST ######

    ###### BEGIN - UPDATE TEST ######

    def _test_update_fails_without_field(self):
        for field in self._get_required_fields():
            self._test_field_validation(method='put', field=field, value=None)

    def _test_update_fails_with_blank_field(self):
        for field in self._get_required_fields():
            self._test_field_validation(method='put', field=field, value='')

    def _test_update_fails_with_invalid_uuid(self):
        data = self._get_instance_data()
        response = self._make_put_request(url=self.invalid_uuid_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found for invalid UUID")

    def _test_update_fails_with_valid_uuid_from_another_company(self):
        instance = self._create_instance(company=self.other_company)
        data = self._get_instance_data()
        response = self._make_put_request(url=self._generate_update_url(instance=instance), data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found for UUID from another company")

    def _test_update_succeeds_with_valid_data(self):
        data = self._get_instance_data()
        response = self._make_put_request(url=self._generate_update_url(), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Expected 200 OK for successful update")

        updated_instance = self.model_class.objects.get(uuid=response.data['uuid'])
        self.assertIsNotNone(updated_instance, "Should exist in database")

        for field in self._get_expected_fields():
            self.assertIn(field, response.data, f"Field {field} in response data")

            expected_value = getattr(updated_instance, field)
            response_value = response.data[field]

            if field == 'uuid':
                self.assertEqual(str(expected_value), response_value, f"Expected {field} value to match response data")
            else:
                self.assertEqual(expected_value, data[field], f"Expected {field} value to match input data")
                self.assertEqual(expected_value, response_value, f"Expected {field} value to match response data")
                self.assertEqual(response_value, data[field], f"Expected response data {field} to match input data")

    ###### END - UPDATE TEST ######

    ###### BEGIN - DELETE TEST ######

    def _test_delete_fails_with_invalid_uuid(self):
        response = self._make_delete_request(url=self.invalid_uuid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found with invalid UUID")

    def _test_delete_fails_with_valid_uuid_from_another_company(self):
        instance = self._create_instance(company=self.other_company)
        response = self._make_delete_request(url=self._generate_delete_url(instance=instance))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found with UUID belonging to another company")

    def _test_delete_succeeds(self):
        instance = self._create_instance(company=self.company)
        response = self._make_delete_request(url=self._generate_delete_url(instance=instance))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, "Expected 204 No Content on successful delete")

        with self.assertRaises(self.model_class.DoesNotExist):
            self.model_class.objects.get(uuid=instance.uuid)

    ###### END - DELETE TEST ######

    ###### BEGIN - DETAIL TEST ######

    def _test_get_detail_fails_with_invalid_uuid(self):
        response = self._make_get_request(url=self.invalid_uuid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found with invalid UUID")

    def _test_get_detail_fails_with_valid_uuid_from_another_company(self):
        instance = self._create_instance(company=self.other_company)
        response = self._make_get_request(url=self._generate_detail_url(instance=instance))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found with UUID belonging to another company")

    def _test_get_detail_succeeds(self):
        response = self._make_get_request(url=self._generate_detail_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Expected 200 OK on successful get detail")
        self._test_response_structure_item(data=response.data)

    ###### END - DETAIL TEST ######

    ###### BEGIN - LIST TEST ######

    def _test_get_list_brand_succeeds(self):
        count = self._test_create_batch()
        num_pages = math.ceil(count / self.default_page_size)
        result_len = min(self.default_page_size, count)

        response = self._make_get_request(url=self._generate_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Expected 200 OK on successful get list")
        self._test_response_structure_pagination(data=response.data, count=count, num_pages=num_pages, result_len=result_len)

    def _test_get_list_brand_query_params_succeds(self):
        count = self._test_create_batch()
        page_size = random.randint(1, 20)
        num_pages = math.ceil(count / page_size)
        page = random.randint(1, num_pages)
        result_len = min(page_size, count - ((page - 1) * page_size) )

        query_params = {'page_size': page_size, 'page': page}

        response = self._make_get_request(url=self._generate_list_url(), data=query_params)
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Expected 200 OK on successful get list")
        self._test_response_structure_pagination(data=response.data, count=count, num_pages=num_pages, result_len=result_len)

    ###### END - LIST TEST ######
