from rest_framework.test import APITestCase
from rest_framework import status
from authentication.models import CustomUser
from rest_framework.reverse import reverse

class RegistrationTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('user-registration')
        self.user_data = {
            'email': 'testuser@gmail.com',
            'password': 'testpassword'
        }
        self.required_fields = ['email', 'password']

    def test_registration_fails_without_field(self):
        for field in self.required_fields:
            data = self.user_data.copy()
            data.pop(field)

            response = self.client.post(self.url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data['errors'])

    def test_registration_fails_with_blank_field(self):
        for field in self.required_fields:
            data = self.user_data.copy()
            data[field] = ''

            response = self.client.post(self.url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data['errors'])

    def test_registration_fails_with_invalid_email_format(self):
        data = self.user_data.copy()
        data['email'] = 'invalid-email'

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data['errors'])

    def test_registration_fails_with_duplicate_email(self):
        CustomUser.objects.create_user(email=self.user_data['email'], password=self.user_data['password'])
        response = self.client.post(self.url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data['errors'])

    def test_registration_succeeds_with_user_data(self):
        response = self.client.post(self.url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = CustomUser.objects.get(email=self.user_data['email'])
        self.assertTrue(user.check_password(self.user_data['password']))
