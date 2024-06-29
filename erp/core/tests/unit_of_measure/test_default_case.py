import uuid

from core.models import UnitOfMeasure
from rest_framework.reverse import reverse
from core.tests.authentication_api_test_case import AuthenticationApiTestCase
from core.tests.crud_api_test_case import CRUDApiTestCase


class DefaultTestCase(AuthenticationApiTestCase, CRUDApiTestCase):

    def setUp(self):
        super().setUp()
        self.model_class = UnitOfMeasure

        self.invalid_uuid_url = reverse(
            "unitofmeasure-detail", kwargs={"uuid": uuid.uuid4()}
        )

        self.default_page_size = 10

        self.required_fields = ["name", "abbreviation"]
        self.expected_fields = ["uuid", "name", "abbreviation"]

    def test_init(self):
        self._execute_authentication_tests()
        self._execute_crud_tests()

    def _get_instance_data(self):
        return {"name": self.fake.word(), "abbreviation": self.fake.word()[:5].upper()}

    def _create_instance(self, *, company):
        return UnitOfMeasure.objects.create(
            company=company, **self._get_instance_data()
        )

    def _generate_create_url(self):
        return reverse("unitofmeasure-list")

    def _generate_update_url(self, *, instance=None):
        if instance is None:
            instance = self._create_instance(company=self.company)
        return reverse("unitofmeasure-detail", kwargs={"uuid": instance.uuid})

    def _generate_delete_url(self, *, instance=None):
        if instance is None:
            instance = self._create_instance(company=self.company)
        return reverse("unitofmeasure-detail", kwargs={"uuid": instance.uuid})

    def _generate_detail_url(self, *, instance=None):
        if instance is None:
            instance = self._create_instance(company=self.company)
        return reverse("unitofmeasure-detail", kwargs={"uuid": instance.uuid})

    def _get_requests(self):
        return [
            ("post", self._generate_create_url(), self._get_instance_data()),
            ("put", self._generate_update_url(), self._get_instance_data()),
            ("delete", self._generate_delete_url(), None),
            ("get", self._generate_detail_url(), None),
            ("get", self._generate_list_url(), None),
        ]

    def _generate_list_url(self):
        return reverse("unitofmeasure-list")

    def _get_model_class(self):
        return self.model_class

    def _get_required_fields(self):
        return self.required_fields

    def _get_expected_fields(self):
        return self.expected_fields
