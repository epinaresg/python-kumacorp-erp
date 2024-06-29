from faker import Faker
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from authentication.models import CustomUser
from core.models import Company

class BaseAPITestCase(APITestCase):
    def setUp(self):
        super().setUp()

        self.fake = Faker('es_ES')

        self.user = self._create_user(email='testuser@gmail.com', password='testuser@gmail.com')
        self.other_user = self._create_user(email='testuser1@gmail.com', password='testuser1@gmail.com')

        self.company = self._create_company(user=self.user)
        self.other_company = self._create_company(user=self.other_user)

        self.access_token = self.client.post(
            path=reverse('token-obtain'),
            data={'email': 'testuser@gmail.com', 'password': 'testuser@gmail.com'}
        ).data['access']

    def _create_user(self, *, email, password):
        return CustomUser.objects.create_user(email=email, password=password)

    def _create_company(self, *, user):
        return Company.objects.create(user=user, name=self.fake.company())
