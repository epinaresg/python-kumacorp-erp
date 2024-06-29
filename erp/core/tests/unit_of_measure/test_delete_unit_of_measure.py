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

    def _make_delete_request(self, *, url):
        return self.make_request(method='delete', url=url, data=None, access_token=self.access_token, company_uuid=self.company.uuid)

    def test_delete_unit_of_measure_fails_with_invalid_uuid(self):
        invalid_uuid = uuid.uuid4()
        url = reverse('unitofmeasure-detail', kwargs={'uuid': invalid_uuid})

        response = self._make_delete_request(url=url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found with invalid UUID")

    def test_delete_unit_of_measure_fails_with_valid_uuid_from_another_company(self):
        url = reverse('unitofmeasure-detail', kwargs={'uuid': self.other_unit_of_measure.uuid})

        response = self._make_delete_request(url=url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found with UUID belonging to another company")

    def test_delete_unit_of_measure_succeeds(self):
        response = self._make_delete_request(url=self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, "Expected 204 No Content on successful delete")

        with self.assertRaises(UnitOfMeasure.DoesNotExist):
            UnitOfMeasure.objects.get(uuid=self.unit_of_measure.uuid)
