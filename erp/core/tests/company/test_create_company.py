from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from authentication.models import CustomUser
from core.models import Company

class CreateCompanyTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email='testuser@gmail.com', password='testuser@gmail.com')

        url_get_token = reverse('token-obtain')
        response = self.client.post(url_get_token, {'email': 'testuser@gmail.com', 'password': 'testuser@gmail.com'}, format='json')
        self.access_token = response.data['access']

        self.url = reverse('company-list')
        self.company_data = {
            'name': 'Test company',
        }
        self.required_fields = ['name']

    def test_create_company_requires_authentication(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, "Expected 401 Unauthorized for unauthenticated company creation")

    def test_create_company_fails_without_field(self):
        for field in self.required_fields:
            data = self.company_data.copy()
            data.pop(field)

            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
            response = self.client.post(self.url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data, f"Missing '{field}' in response data for bad request")

    def test_create_company_fails_with_blank_field(self):
        for field in self.required_fields:
            data = self.company_data.copy()
            data[field] = ''

            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
            response = self.client.post(self.url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data, f"Missing '{field}' in response data for bad request")

    def test_create_company_succeeds_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(self.url, self.company_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Expected 201 Created for successful company creation")

        expected_fields = ['uuid', 'name', 'settings']
        for field in expected_fields:
            self.assertIn(field, response.data, f"Expected '{field}' in response data")

        company = Company.objects.get(uuid=response.data['uuid'])
        self.assertIsNotNone(company)
        self.assertEqual(
            company.name, self.company_data['name'], "Expected company name to match input data"
        )
        self.assertEqual(
            response.data['name'], self.company_data['name'], "Expected response name to match input data"
        )

    def test_create_company_fails_user_cannot_register_multiple_companies(self):
        company = Company.objects.create(user=self.user, **self.company_data)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(self.url, self.company_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, "Expected 400 Bad Request for duplicate company creation")
