import json
import mock

from django.test import TestCase

from django_keycloak.factories import RealmFactory
from django_keycloak.services.client import UMAResourceClient
from django_keycloak.tests.mixins import MockTestCaseMixin


class UMAResourceClientTestCase(MockTestCaseMixin, TestCase):
    def setUp(self):
        self.realm = RealmFactory(
            server__url='https://public.example.com',
            server__internal_url='https://internal.example.com',
        )
        self.client = UMAResourceClient(self.realm)
        self.requests_get = self.setup_mock('django_keycloak.services.client.requests.get')
        self.requests_post = self.setup_mock('django_keycloak.services.client.requests.post')

        self.requests_get.return_value = mock.MagicMock(
            status_code=200,
            json=mock.MagicMock(return_value={'resource_registration_endpoint': 'https://internal.example.com/uma'}),
        )
        self.requests_post.return_value = mock.MagicMock(status_code=201, json=mock.MagicMock(return_value={}), content=b'{}')

    def test_resource_set_create_uses_internal_url_and_headers(self):
        self.client.resource_set_create(
            token='ACCESS',
            name='app.model',
            scopes=['read', 'write'],
        )

        self.requests_get.assert_called_once()
        self.requests_post.assert_called_once()
        args, kwargs = self.requests_post.call_args
        self.assertEqual(args[0], 'https://internal.example.com/uma')
        self.assertEqual(kwargs['headers']['Authorization'], 'Bearer ACCESS')
        self.assertEqual(kwargs['headers']['Content-Type'], 'application/json')
        self.assertEqual(kwargs['headers']['Host'], 'public.example.com')
        self.assertEqual(kwargs['headers']['X-Forwarded-Proto'], 'https')
        self.assertEqual(json.loads(json.dumps(kwargs['json']))['name'], 'app.model')
