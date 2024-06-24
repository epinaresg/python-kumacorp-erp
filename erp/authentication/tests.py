from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.reverse import reverse

class RegistrationTestCase(APITestCase):

    def test_user_registration(self):
        url = reverse('user-registration')
        data = {
            'email': 'testuser@gmail.com',
            'password': 'testpassword'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email='testuser@gmail.com')
        self.assertEqual(user.username, 'testuser')

        self.assertTrue(user.check_password('testpassword'))


class AuthenticationTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_token_generation(self):
        url = reverse('token-obtain')  # Asegúrate de que este nombre de ruta corresponda a tu endpoint de generación de tokens
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_token_refresh(self):
        url = reverse('token-refresh')  # Asegúrate de que este nombre de ruta corresponda a tu endpoint de refresco de tokens
        refresh_token = 'token_recibido_previamente'  # Obtenido del token de generación

        data = {
            'refresh': refresh_token
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('access', response.data)
