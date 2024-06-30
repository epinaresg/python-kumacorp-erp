import logging

from faker import Faker
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from authentication.models import CustomUser
from core.models import Company


class BaseAPITestCase(APITestCase):
    def setUp(self):
        super().setUp()
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

    def _make_request(
        self, *, method, url, data=None, access_token=None, company_uuid=None
    ):
        headers = {}
        if access_token:
            headers["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"
        if company_uuid:
            headers["HTTP_X_COMPANY_UUID"] = company_uuid

        if headers:
            self.client.credentials(**headers)

        methods = {
            "get": self.client.get,
            "post": self.client.post,
            "put": self.client.put,
            "delete": self.client.delete,
        }

        if method in methods:
            return methods[method](url, data, format="json")
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

    def _make_post_request(self, *, url, data):
        return self._make_request(
            method="post",
            url=url,
            data=data,
            access_token=self.access_token,
            company_uuid=self.company.uuid,
        )

    def _make_delete_request(self, *, url):
        return self._make_request(
            method="delete",
            url=url,
            data=None,
            access_token=self.access_token,
            company_uuid=self.company.uuid,
        )

    def _make_get_request(self, *, url, data=None):
        return self._make_request(
            method="get",
            url=url,
            data=data,
            access_token=self.access_token,
            company_uuid=self.company.uuid,
        )

    def _make_put_request(self, *, url, data):

        return self._make_request(
            method="put",
            url=url,
            data=data,
            access_token=self.access_token,
            company_uuid=self.company.uuid,
        )
