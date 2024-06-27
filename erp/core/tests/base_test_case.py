from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from authentication.models import CustomUser
from core.models import Brand, Company, UnitOfMeasure

class BaseAPITestCase(APITestCase):
    def setUp(self):
        self.user = self.create_user(email='testuser@gmail.com', password='testuser@gmail.com')
        self.company = self.create_company(user=self.user, name='Test company')

        self.other_user = self.create_user(email='testuser1@gmail.com', password='testuser1@gmail.com')
        self.other_company = self.create_company(user=self.other_user, name='Other Test company')

        self.access_token = self.get_access_token(email='testuser@gmail.com', password='testuser@gmail.com')

    def create_user(self, *, email, password):
        return CustomUser.objects.create_user(email=email, password=password)

    def create_company(self, *, user, name):
        return Company.objects.create(user=user, name=name)

    def create_brand(self, *, company, name):
        return Brand.objects.create(company=company, name=name)

    def create_unit_of_measure(self, *, company, name, abbreviation):
        return UnitOfMeasure.objects.create(company=company, name=name, abbreviation=abbreviation)

    def get_access_token(self, *, email, password):
        url_get_token = reverse('token-obtain')
        response = self.client.post(url_get_token, {'email': email, 'password': password}, format='json')
        return response.data['access']
