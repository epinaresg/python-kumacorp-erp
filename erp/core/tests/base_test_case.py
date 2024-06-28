from faker import Faker
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from authentication.models import CustomUser
from core.models import Brand, Company, UnitOfMeasure

class BaseAPITestCase(APITestCase):
    def setUp(self):
        self.fake = Faker('es_ES')

        self.user = self.create_user(email='testuser@gmail.com', password='testuser@gmail.com')
        self.other_user = self.create_user(email='testuser1@gmail.com', password='testuser1@gmail.com')

        self.company = self.create_company(user=self.user)
        self.other_company = self.create_company(user=self.other_user)

        self.access_token = self.make_request(
            method='post',
            url=reverse('token-obtain'),
            data={'email': 'testuser@gmail.com', 'password': 'testuser@gmail.com'}
        ).data['access']

    def create_user(self, *, email, password):
        return CustomUser.objects.create_user(email=email, password=password)

    def create_company(self, *, user):
        return Company.objects.create(user=user, name=self.fake.company())


    def get_brand_data(self):
        return {'name': self.fake.word(), "description": self.fake.paragraph()}

    def create_brand(self, *, company):
        return Brand.objects.create(company=company, **self.get_brand_data())

    def get_unit_of_measure_data(self):
        return {'name': self.fake.word(), 'abbreviation': self.fake.word()[0:4]}

    def create_unit_of_measure(self, *, company):
        return UnitOfMeasure.objects.create(company=company, **self.get_unit_of_measure_data())

    def get_access_token(self, *, email, password):
        url_get_token = reverse('token-obtain')
        response = self.make_request('post', {'email': email, 'password': password})
        return response.data['access']


    def make_request(self, *, method, url, data=None, access_token=None, company_uuid=None):
        headers = {}
        if access_token:
            headers['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
        if company_uuid:
            headers['HTTP_X_COMPANY_UUID'] = company_uuid

        if headers:
            self.client.credentials(**headers)

        methods = {
            'get': self.client.get,
            'post': self.client.post,
            'put': self.client.put,
            'delete': self.client.delete
        }

        if method in methods:
            return methods[method](url, data, format='json')
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

