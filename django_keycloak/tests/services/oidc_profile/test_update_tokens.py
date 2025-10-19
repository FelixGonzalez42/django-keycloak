from datetime import datetime, timedelta
from datetime import datetime, timedelta

from django.test import TestCase

from django_keycloak.factories import OpenIdConnectProfileFactory
import django_keycloak.services.oidc_profile as oidc_profile_service


class UpdateTokensTests(TestCase):
    def setUp(self):
        self.profile = OpenIdConnectProfileFactory(
            access_token='old-access-token',
            expires_before=datetime(2023, 1, 1, 12, 0, 0),
            refresh_token='old-refresh-token',
            refresh_expires_before=datetime(2023, 1, 1, 13, 0, 0),
        )

    def test_handles_missing_refresh_information(self):
        initiate_time = datetime(2024, 1, 1, 12, 0, 0)
        token_response = {
            'access_token': 'new-access-token',
            'expires_in': 120,
        }

        updated = oidc_profile_service.update_tokens(
            token_model=self.profile,
            token_response=token_response,
            initiate_time=initiate_time,
        )

        self.assertEqual(updated.access_token, 'new-access-token')
        self.assertEqual(
            updated.expires_before,
            initiate_time + timedelta(seconds=token_response['expires_in']),
        )
        self.assertIsNone(updated.refresh_token)
        self.assertIsNone(updated.refresh_expires_before)
