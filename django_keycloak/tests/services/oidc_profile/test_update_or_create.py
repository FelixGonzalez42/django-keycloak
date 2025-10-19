import mock

from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from freezegun import freeze_time
from keycloak import KeycloakOpenID

from django_keycloak.factories import ClientFactory
from django_keycloak.models import OpenIdConnectProfile
from django_keycloak.tests.mixins import MockTestCaseMixin

import django_keycloak.services.oidc_profile


class ServicesKeycloakOpenIDProfileUpdateOrCreateTestCase(MockTestCaseMixin,
                                                          TestCase):

    def setUp(self):
        self.client = ClientFactory(
            realm___certs='{}',
            realm___well_known_oidc='{"issuer": "https://issuer"}'
        )
        self.client.openid_api_client = mock.MagicMock(
            spec_set=KeycloakOpenID)
        self.client.openid_api_client.token.return_value = {
            'id_token': 'id-token',
            'expires_in': 600,
            'refresh_expires_in': 3600,
            'access_token': 'access-token',
            'refresh_token': 'refresh-token'
        }
        self.client.openid_api_client.decode_token.return_value = {
            'sub': 'some-sub',
            'email': 'test@example.com',
            'given_name': 'Some given name',
            'family_name': 'Some family name'
        }
        self.build_jwk_set_mock = self.setup_mock(
            'django_keycloak.services.client.build_jwk_set'
        )
        self.build_jwk_set_mock.return_value = mock.sentinel.jwks

    @freeze_time('2018-03-01 00:00:00')
    def test_create(self):
        django_keycloak.services.oidc_profile.update_or_create_from_code(
            client=self.client,
            code='some-code',
            redirect_uri='https://redirect'
        )
        self.client.openid_api_client.token.assert_called_once_with(
            code='some-code',
            redirect_uri='https://redirect',
            grant_type=['authorization_code']
        )
        self.client.openid_api_client.decode_token.assert_called_once_with(
            'id-token',
            key=mock.sentinel.jwks,
            check_claims={'iss': 'https://issuer', 'aud': self.client.client_id},
            access_token='access-token'
        )

        profile = OpenIdConnectProfile.objects.get(sub='some-sub')
        self.assertEqual(profile.sub, 'some-sub'),
        self.assertEqual(profile.access_token, 'access-token')
        self.assertEqual(profile.refresh_token, 'refresh-token')
        self.assertEqual(profile.expires_before, datetime(
            year=2018, month=3, day=1, hour=0, minute=10, second=0
        ))
        self.assertEqual(profile.refresh_expires_before, datetime(
            year=2018, month=3, day=1, hour=1, minute=0, second=0
        ))

        user = profile.user
        self.assertEqual(user.username, 'some-sub')
        self.assertEqual(user.first_name, 'Some given name')
        self.assertEqual(user.last_name, 'Some family name')

    @freeze_time('2018-03-01 00:00:00')
    def test_update(self):
        UserModel = get_user_model()
        user = UserModel.objects.create(
            username='some-sub',
            email='',
            first_name='',
            last_name=''
        )
        profile = OpenIdConnectProfile.objects.create(
            realm=self.client.realm,
            sub='some-sub',
            user=user,
            access_token='another-access-token',
            expires_before=datetime.now(),
            refresh_token='another-refresh-token',
            refresh_expires_before=datetime.now()
        )

        django_keycloak.services.oidc_profile.update_or_create_from_code(
            client=self.client,
            code='some-code',
            redirect_uri='https://redirect'
        )
        self.client.openid_api_client.token.assert_called_once_with(
            code='some-code',
            redirect_uri='https://redirect',
            grant_type=['authorization_code']
        )
        self.client.openid_api_client.decode_token.assert_called_once_with(
            'id-token',
            key=mock.sentinel.jwks,
            check_claims={'iss': 'https://issuer', 'aud': self.client.client_id},
            access_token='access-token'
        )

        profile.refresh_from_db()
        self.assertEqual(profile.sub, 'some-sub')
        self.assertEqual(profile.access_token, 'access-token')
        self.assertEqual(profile.refresh_token, 'refresh-token')
        self.assertEqual(profile.expires_before, datetime(
            year=2018, month=3, day=1, hour=0, minute=10, second=0
        ))
        self.assertEqual(profile.refresh_expires_before, datetime(
            year=2018, month=3, day=1, hour=1, minute=0, second=0
        ))

        user = profile.user
        user.refresh_from_db()
        self.assertEqual(user.username, 'some-sub')
        self.assertEqual(user.first_name, 'Some given name')
        self.assertEqual(user.last_name, 'Some family name')
