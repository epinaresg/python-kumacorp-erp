from rest_framework.test import APITestCase
from rest_framework import status
from authentication.models import CustomUser
from rest_framework.reverse import reverse

class AuthenticationTestCase(APITestCase):
    def setUp(self):
        self.url_get_token = reverse('token-obtain')
        self.url_refresh_token = reverse('token-refresh')

        self.user_data = {
            'email': 'testuser@gmail.com',
            'password': 'testpassword'
        }
        self.required_fields = ['email', 'password']
        self.user = CustomUser.objects.create_user(**self.user_data)

    def test_authentication_fails_without_field(self):
        for field in self.required_fields:
            data = self.user_data.copy()
            data.pop(field)

            response = self.client.post(self.url_get_token, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)

    def test_authentication_fails_with_blank_field(self):
        for field in self.required_fields:
            data = self.user_data.copy()
            data[field] = ''

            response = self.client.post(self.url_get_token, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)

    def test_authentication_get_token_fail_with_invalid_email(self):
        data = self.user_data.copy()
        data['email'] = 'invalid-email'

        response = self.client.post(self.url_get_token, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authentication_get_token_fail_with_invalid_password(self):
        data = self.user_data.copy()
        data['password'] = 'invalid-password'

        response = self.client.post(self.url_get_token, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authentication_get_token_succeeds_with_user_data(self):
        data = self.user_data.copy()

        response = self.client.post(self.url_get_token, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)

    def test_authentication_refresh_token_succeeds_with_valid_refresh_token(self):
        response = self.client.post(self.url_get_token, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)

        refresh_token = response.data['refresh']

        response = self.client.post(self.url_refresh_token, {'refresh': refresh_token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_authentication_refresh_token_fails_with_invalid_refresh_token(self):
        response = self.client.post(self.url_refresh_token, {'refresh': 'invalid-refresh-token'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
