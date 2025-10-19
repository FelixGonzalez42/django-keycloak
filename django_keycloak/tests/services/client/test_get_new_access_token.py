import mock
from django.test import TestCase

from django_keycloak.factories import ClientFactory
from django_keycloak.services import client as client_services


class GetNewAccessTokenTests(TestCase):
    def setUp(self):
        self.client = ClientFactory(
            realm___certs='{}',
            realm___well_known_oidc='{"issuer": "https://issuer"}'
        )
        self.openid_client_mock = mock.MagicMock()
        self.client.openid_api_client = self.openid_client_mock

    def test_uses_client_credentials_grant(self):
        self.openid_client_mock.token.return_value = {
            'access_token': 'token',
            'expires_in': 60,
        }

        response, initiate_time = client_services.get_new_access_token(self.client)

        self.assertEqual(response['access_token'], 'token')
        self.assertIsNotNone(initiate_time)
        self.openid_client_mock.token.assert_called_once_with(
            grant_type='client_credentials',
            scope='realm-management openid',
        )
