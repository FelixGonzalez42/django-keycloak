import mock

from datetime import datetime

from django.test import TestCase
from keycloak import KeycloakOpenID

from django_keycloak.factories import OpenIdConnectProfileFactory
from django_keycloak.tests.mixins import MockTestCaseMixin

import django_keycloak.services.oidc_profile


class ServicesKeycloakOpenIDProfileGetActiveAccessTokenTestCase(
        MockTestCaseMixin, TestCase):

    def setUp(self):
        self.mocked_get_active_access_token = self.setup_mock(
            'django_keycloak.services.oidc_profile'
            '.get_active_access_token'
        )

        self.oidc_profile = OpenIdConnectProfileFactory(
            access_token='access-token',
            expires_before=datetime(2018, 3, 5, 1, 0, 0),
            refresh_token='refresh-token'
        )
        self.oidc_profile.realm.client.openid_api_client = mock.MagicMock(
            spec_set=KeycloakOpenID)
        self.oidc_profile.realm.client.authz_api_client = mock.MagicMock()
        self.oidc_profile.realm.client.authz_api_client.entitlement\
            .return_value = {
                'rpt': 'RPT_VALUE'
            }
        self.build_jwk_set_mock = self.setup_mock(
            'django_keycloak.services.client.build_jwk_set'
        )
        self.build_jwk_set_mock.return_value = mock.sentinel.jwks

    def test(self):
        django_keycloak.services.oidc_profile.get_entitlement(
            oidc_profile=self.oidc_profile
        )
        self.oidc_profile.realm.client.authz_api_client.entitlement\
            .assert_called_once_with(
                token=self.mocked_get_active_access_token.return_value
            )
        self.oidc_profile.realm.client.openid_api_client.decode_token\
            .assert_called_once_with(
                'RPT_VALUE',
                key=mock.sentinel.jwks,
            )
