from rest_framework.test import APITestCase
from rest_framework import status
from authentication.models import CustomUser
from core.models import Brand
from rest_framework.reverse import reverse

class CreateBrandTestCase(APITestCase):
    def setUp(self):
        self.user_data = {
            'email': 'testuser@gmail.com',
            'password': 'testpassword'
        }
        self.url_get_token = reverse('token-obtain')
        self.user = CustomUser.objects.create_user(**self.user_data)
        response = self.client.post(self.url_get_token, self.user_data, format='json')
        self.access_token = response.data['access']

        self.url = reverse('brand-list')
        self.brand_data = {
            'name': 'Test brand',
        }
        self.required_fields = ['name']

    def test_create_brand_requires_authentication(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_brand_fails_without_field(self):
        for field in self.required_fields:
            data = self.brand_data.copy()
            data.pop(field)

            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
            response = self.client.post(self.url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)

    def test_create_brand_fails_with_blank_field(self):
        for field in self.required_fields:
            data = self.brand_data.copy()
            data[field] = ''

            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
            response = self.client.post(self.url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)

    def test_create_brand_succeeds_with_valid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(self.url, self.brand_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        expected_fields = ['uuid', 'name', 'settings']
        for field in expected_fields:
            self.assertIn(field, response.data)

        brand = Brand.objects.get(uuid=response.data['uuid'])
        self.assertIsNotNone(brand)
        self.assertTrue(
            brand.name == self.brand_data['name'] and
            brand.name == response.data['name'] and
            response.data['name'] == self.brand_data['name']
        )

    def test_create_brand_fails_user_cannot_register_multiple_companies(self):
        brand = Brand.objects.create(user=self.user, **self.brand_data)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(self.url, self.brand_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
