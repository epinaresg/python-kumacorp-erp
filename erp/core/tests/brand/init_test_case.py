import uuid

from core.models import Brand
from rest_framework.reverse import reverse
from core.tests.base_test_case import BaseAPITestCase
from core.tests.authentication_test_case import AuthenticationApiTestCase
from core.tests.crud_test_case import CRUDApiTestCase

class InitTestCase(BaseAPITestCase, AuthenticationApiTestCase, CRUDApiTestCase):
    def setUp(self):
        super().setUp()

        self.model_class = Brand

        self.instance = self.create_brand(company=self.company)
        self.other_company_instance = self.create_brand(company=self.other_company)

        self.create_url = reverse('brand-list')
        self.update_url = reverse('brand-detail', kwargs={'uuid': self.instance.uuid})
        self.delete_url = reverse('brand-detail', kwargs={'uuid': self.instance.uuid})
        self.detail_url = reverse('brand-detail', kwargs={'uuid': self.instance.uuid})
        self.list_url = reverse('brand-list')

        self.invalid_uuid_url = reverse('brand-detail', kwargs={'uuid': uuid.uuid4()})
        self.other_company_update_url = reverse('brand-detail', kwargs={'uuid': self.other_company_instance.uuid})

        self.requests = [
            ('post', self.create_url, self.get_brand_data()),
            ('put', self.update_url, self.get_brand_data()),
            ('delete', self.delete_url, None),
            ('get', self.detail_url, None),
            ('get', self.list_url, None),
        ]

        self.get_instance_data_fn = self.get_brand_data
        self.create_instance_fn = self.create_brand

        self.required_fields = ['name']
        self.expected_fields = ['uuid', 'name', 'description']

    def get_brand_data(self):
        return {'name': self.fake.word(), "description": self.fake.paragraph()}

    def create_brand(self, *, company):
        return Brand.objects.create(company=company, **self.get_brand_data())
