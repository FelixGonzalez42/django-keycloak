import uuid
from unittest import mock

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from django_keycloak.factories import RealmFactory
from django_keycloak.middleware import BaseKeycloakMiddleware
from django_keycloak.views import LoginComplete


@override_settings(ROOT_URLCONF='django_keycloak.urls')
class LoginCompleteViewTests(TestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.realm = RealmFactory()

    def _prepare_request(self, state):
        request = self.factory.get(
            reverse('keycloak_login_complete'),
            {'code': 'abc123', 'state': state},
        )
        request.user = AnonymousUser()
        request.session = {'oidc_state': state}

        base_middleware = BaseKeycloakMiddleware(lambda req: req)
        base_middleware.process_request(request)
        return request

    def test_missing_nonce_redirects_to_login(self):
        state = str(uuid.uuid4())
        request = self._prepare_request(state)

        with mock.patch('django_keycloak.views.authenticate') as authenticate_mock:
            response = LoginComplete.as_view()(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('keycloak_login'))
        self.assertNotIn('oidc_state', request.session)
        authenticate_mock.assert_not_called()
