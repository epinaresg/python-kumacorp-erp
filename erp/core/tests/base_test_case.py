from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from authentication.models import CustomUser
from core.models import Company

class BaseAPITestCase(APITestCase):
    def setUp(self):
        self.user = self.create_user(email='testuser@gmail.com', password='testpassword')
        self.company = self.create_company(user=self.user, name='Test company')

        self.other_user = self.create_user(email='testuser1@gmail.com', password='testpassword1')
        self.other_company = self.create_company(user=self.other_user, name='OtherTest company')

        self.url_get_token = reverse('token-obtain')
        response = self.client.post(self.url_get_token, {'email': self.user.email, 'password': 'testpassword'}, format='json')
        self.access_token = response.data['access']

    def create_user(self, email, password):
        return CustomUser.objects.create_user(email=email, password=password)

    def create_company(self, user, name):
        return Company.objects.create(user=user, name=name)
