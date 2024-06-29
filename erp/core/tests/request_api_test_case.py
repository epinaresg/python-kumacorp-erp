from core.tests.base_api_test_case import BaseAPITestCase


class RequestAPITestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()

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
