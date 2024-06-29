import math
import random
import uuid
from rest_framework import status
from rest_framework.reverse import reverse
from core.models import Brand
from core.tests.base_test_case import BaseAPITestCase

class GetBrandTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.brands_qty = random.randint(1, 150)
        for _ in range(self.brands_qty):
            self.create_brand(company=self.company)

        self.other_brand = self.create_brand(company=self.other_company)
        self.url_list = reverse('brand-list')

        brand = Brand.objects.filter(company=self.company).order_by('?').first()
        self.url_detail = reverse('brand-detail', kwargs={'uuid': brand.uuid})

        self.expected_fields = ['uuid', 'name', 'description']


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
        brand = Brand.objects.get(uuid=data['uuid'])
        for field in self.expected_fields:
            self.assertIn(field, data, f"Field {field} in result sample")
            expected_value = str(getattr(brand, field)) if field == 'uuid' else getattr(brand, field)
            self.assertEqual(data[field], expected_value, f"Expected {field} to match in result sample")

    def test_get_detail_brand_fails_with_invalid_uuid(self):
        invalid_uuid = uuid.uuid4()
        url = reverse('brand-detail', kwargs={'uuid': invalid_uuid})
        response = self._make_get_request(url=url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found with invalid UUID")

    def test_get_detail_brand_fails_with_valid_uuid_from_another_company(self):
        url = reverse('brand-detail', kwargs={'uuid': self.other_brand.uuid})
        response = self._make_get_request(url=url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found with UUID belonging to another company")

    def test_get_detail_brand_succeeds(self):
        response = self._make_get_request(url=self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Expected 200 OK on successful get detail")
        self._test_response_structure_item(data=response.data)

    def test_get_list_brand_succeeds(self):
        response = self._make_get_request(url=self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Expected 200 OK on successful get list")
        self._test_response_structure_pagination(data=response.data, count=self.brands_qty, num_pages=math.ceil(self.brands_qty / 10), result_len=min(10, self.brands_qty))

    def test_get_list_brand_query_params_succeds(self):
        page_size = random.randint(1, 20);
        num_pages = math.ceil(self.brands_qty / page_size)
        page = random.randint(1, num_pages)
        result_len = min(page_size, self.brands_qty - ((page - 1) * page_size) )

        query_params = {'page_size': page_size, 'page': page}

        response = self._make_get_request(url=self.url_list, data=query_params)
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Expected 200 OK on successful get list")
        self._test_response_structure_pagination(data=response.data, count=self.brands_qty, num_pages=num_pages, result_len=result_len)
