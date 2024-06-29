import logging

from faker import Faker
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from authentication.models import CustomUser
from core.models import Company


class BaseAPITestCase(APITestCase):
    def setUp(self):
        super().setUpClass()
        self.fake = Faker("es_ES")
        self.logger = logging.getLogger("django.test")

        self.user = self._create_user(
            email="testuser@gmail.com", password="testuser@gmail.com"
        )
        self.other_user = self._create_user(
            email="testuser1@gmail.com", password="testuser1@gmail.com"
        )

        self.company = self._create_company(self.user)
        self.other_company = self._create_company(self.other_user)

        self.access_token = self._get_access_token(
            email="testuser@gmail.com", password="testuser@gmail.com"
        )

    def _create_user(self, email, password):
        return CustomUser.objects.create_user(email, password)

    def _create_company(self, user):
        return Company.objects.create(user=user, name=self.fake.company())

    def _get_access_token(self, email, password):
        response = self.client.post(
            reverse("token-obtain"), {"email": email, "password": password}
        )
        return response.data["access"]
