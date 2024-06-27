import uuid
from rest_framework import status
from rest_framework.reverse import reverse
from authentication.models import CustomUser
from core.models import UnitOfMeasure, Company
from core.tests.base_test_case import BaseAPITestCase

class UpdateUnitOfMeasureTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.unit_of_measure = self.create_unit_of_measure(company=self.company, name='Name Test', abbreviation='TABRV')
        self.other_unit_of_measure = self.create_unit_of_measure(company=self.other_company, name='Other Name Test', abbreviation='OTABRV')
        self.url = reverse('unitofmeasure-detail', kwargs={'uuid': self.unit_of_measure.uuid})

    def test_delete_unit_of_measure_requires_authentication(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, "Expected 401 Unauthorized for unauthenticated request")

    def test_delete_unit_of_measure_requires_company_uuid(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found without company UUID header")

    def test_delete_unit_of_measure_requires_company_uuid_from_logged_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}', HTTP_X_COMPANY_UUID=self.other_company.uuid)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found with company UUID not matching the logged user")

    def test_delete_unit_of_measure_fails_with_invalid_uuid(self):
        invalid_uuid = uuid.uuid4()
        url = reverse('unitofmeasure-detail', kwargs={'uuid': invalid_uuid})

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}', HTTP_X_COMPANY_UUID=self.company.uuid)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found with invalid unit of measure UUID")

    def test_delete_unit_of_measure_fails_with_valid_uuid_from_another_company(self):
        url = reverse('unitofmeasure-detail', kwargs={'uuid': self.other_unit_of_measure.uuid})

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}', HTTP_X_COMPANY_UUID=self.company.uuid)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, "Expected 404 Not Found with UUID belonging to another company")

    def test_delete_unit_of_measure_succeeds(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}', HTTP_X_COMPANY_UUID=self.company.uuid)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, "Expected 204 No Content on successful delete")

        with self.assertRaises(UnitOfMeasure.DoesNotExist):
            UnitOfMeasure.objects.get(uuid=self.unit_of_measure.uuid)
