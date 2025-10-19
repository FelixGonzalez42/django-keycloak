from django.test import TestCase

from django_keycloak.factories import ServerFactory, RealmFactory

import django_keycloak.services.realm


class ServicesRealmHelpersTestCase(TestCase):

    def setUp(self):
        self.server = ServerFactory(
            url='https://some-url',
            internal_url=''
        )

        self.realm = RealmFactory(
            server=self.server,
            name='test-realm'
        )

    def test_get_realm_server_config(self):
        server_url, headers = django_keycloak.services.realm.\
            get_realm_server_config(realm=self.realm)

        self.assertEqual(server_url, self.server.url)
        self.assertEqual(headers, {})

    def test_get_realm_server_config_with_internal_url(self):
        self.server.internal_url = 'https://some-internal-url'

        server_url, headers = django_keycloak.services.realm.\
            get_realm_server_config(realm=self.realm)

        self.assertEqual(server_url, self.server.internal_url)
        self.assertEqual(headers['Host'], 'some-url')
        self.assertEqual(headers['X-Forwarded-Proto'], 'https')

    def test_build_endpoint(self):
        endpoint = django_keycloak.services.realm.build_endpoint(
            self.realm, '/protocol/openid-connect/token'
        )
        self.assertEqual(
            endpoint,
            'https://some-url/protocol/openid-connect/token'
        )
