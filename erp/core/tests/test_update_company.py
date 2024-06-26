from rest_framework.test import APITestCase
from rest_framework import status
from authentication.models import CustomUser
from core.models import Company
from rest_framework.reverse import reverse

class UpdateCompanyTestCase(APITestCase):
    def setUp(self):
        self.user_data = {
            'email': 'testuser@gmail.com',
            'password': 'testpassword'
        }
        self.url_get_token = reverse('token-obtain')
        self.user = CustomUser.objects.create_user(**self.user_data)
        response = self.client.post(self.url_get_token, self.user_data, format='json')
        self.access_token = response.data['access']

        self.company = Company.objects.create(user=self.user, name='Original Test company')

        self.url = reverse('company-detail', kwargs={'uuid': self.company.uuid})
        self.company_data = {
            'name': 'Test company',
        }
        self.required_fields = ['name']

    def test_update_company_requires_authentication(self):
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_company_fails_without_field(self):
        for field in self.required_fields:
            data = self.company_data.copy()
            data.pop(field)

            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
            response = self.client.put(self.url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)

    def test_update_company_fails_with_blank_field(self):
        for field in self.required_fields:
            data = self.company_data.copy()
            data[field] = ''

            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
            response = self.client.put(self.url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)

    def test_update_company_succeeds_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.put(self.url, self.company_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_fields = ['uuid', 'name', 'settings']
        for field in expected_fields:
            self.assertIn(field, response.data)

        self.assertTrue(
            response.data['name'] == self.company_data['name'] and
            response.data['name'] != self.company.name and
            self.company_data['name'] != self.company.name
        )
        self.assertTrue(
            str(response.data['uuid']) == str(self.company.uuid)
        )
