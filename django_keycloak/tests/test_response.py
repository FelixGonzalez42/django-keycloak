from django.test import SimpleTestCase

from django_keycloak.response import HttpResponseNotAuthorized


class HttpResponseNotAuthorizedTests(SimpleTestCase):
    def test_attributes_are_sanitized(self):
        response = HttpResponseNotAuthorized(
            attributes={"realm": "example", "error": 'bad"value\r\nmalicious'}
        )

        header = response["WWW-Authenticate"]
        self.assertEqual(header, 'Bearer realm="example", error="bad\\"valuemalicious"')
        self.assertNotIn("\n", header)
        self.assertNotIn("\r", header)

    def test_invalid_authorization_method_falls_back_to_bearer(self):
        response = HttpResponseNotAuthorized(authorization_method="Bearer\r\nFoo: bar")

        self.assertEqual(response["WWW-Authenticate"], "Bearer")
