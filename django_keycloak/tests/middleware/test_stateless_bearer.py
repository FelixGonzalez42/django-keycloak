from unittest import mock

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase

from django_keycloak.factories import RealmFactory
from django_keycloak.middleware import (
    BaseKeycloakMiddleware,
    KeycloakStatelessBearerAuthenticationMiddleware,
)
from django_keycloak.response import HttpResponseNotAuthorized


class KeycloakStatelessBearerAuthenticationMiddlewareTests(TestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.middleware = KeycloakStatelessBearerAuthenticationMiddleware(lambda request: request)
        BaseKeycloakMiddleware(lambda request: request)  # ensure middleware import side effects
        self.realm = RealmFactory()

    def _prepare_request(self, header=None):
        request = self.factory.get("/protected")
        if header is not None:
            request.META["HTTP_AUTHORIZATION"] = header
        request.user = AnonymousUser()
        # Attach realm information via the base middleware
        base_middleware = BaseKeycloakMiddleware(lambda req: req)
        base_middleware.process_request(request)
        return request

    def test_missing_authorization_header_returns_unauthorized(self):
        request = self._prepare_request()

        response = self.middleware.process_request(request)

        self.assertIsInstance(response, HttpResponseNotAuthorized)
        self.assertEqual(response.status_code, 401)

    def test_invalid_authorization_scheme_is_rejected(self):
        request = self._prepare_request("Basic Zm9vOmJhcg==")

        with mock.patch("django_keycloak.middleware.authenticate") as authenticate_mock:
            response = self.middleware.process_request(request)

        self.assertIsInstance(response, HttpResponseNotAuthorized)
        authenticate_mock.assert_not_called()

    def test_malformed_authorization_header_is_rejected(self):
        request = self._prepare_request("Bearer")

        with mock.patch("django_keycloak.middleware.authenticate") as authenticate_mock:
            response = self.middleware.process_request(request)

        self.assertIsInstance(response, HttpResponseNotAuthorized)
        authenticate_mock.assert_not_called()

    def test_valid_bearer_token_authenticates_request(self):
        request = self._prepare_request("Bearer valid-token")
        user = object()

        with mock.patch("django_keycloak.middleware.authenticate", return_value=user) as authenticate_mock:
            response = self.middleware.process_request(request)

        authenticate_mock.assert_called_once_with(request=request, access_token="valid-token")
        self.assertIsNone(response)
        self.assertIs(request.user, user)
