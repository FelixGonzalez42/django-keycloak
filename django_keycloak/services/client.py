from __future__ import annotations

import json
import logging
from functools import partial
from typing import Optional

import requests
from jwcrypto import jwk
from keycloak import KeycloakAdmin, KeycloakOpenID
from keycloak.openid_connection import KeycloakOpenIDConnection

from django.utils import timezone

from django_keycloak.services.exceptions import TokensExpired

import django_keycloak.services.oidc_profile
import django_keycloak.services.realm


logger = logging.getLogger(__name__)


class CachedKeycloakOpenID(KeycloakOpenID):
    """Keycloak OpenID client that honours cached discovery data."""

    def __init__(self, *args, cached_well_known=None, cached_certs=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._cached_well_known = cached_well_known
        self._cached_certs = cached_certs

    def well_known(self):  # pragma: no cover - exercised via decode/token flows
        if self._cached_well_known is not None:
            return self._cached_well_known
        self._cached_well_known = super().well_known()
        return self._cached_well_known

    def certs(self):  # pragma: no cover - exercised via decode/token flows
        if self._cached_certs is not None:
            return self._cached_certs
        self._cached_certs = super().certs()
        return self._cached_certs


class AuthzAdapter:
    """Minimal adapter exposing the legacy entitlement API."""

    def __init__(self, openid_client: KeycloakOpenID, resource_server_id: str):
        self._openid_client = openid_client
        self._resource_server_id = resource_server_id

    def entitlement(self, token: str):
        return self._openid_client.entitlement(token, resource_server_id=self._resource_server_id)


class UMAResourceClient:
    """Client for UMA resource registration using the discovery document."""

    def __init__(self, realm):
        self._realm = realm
        self._config: Optional[dict] = None
        server_url, headers = django_keycloak.services.realm.get_realm_server_config(realm)
        self._base_url = f"{server_url}/"
        self._headers = headers

    def _get_config(self) -> dict:
        if self._config is None:
            url = django_keycloak.services.realm.build_endpoint(
                self._realm,
                f"/realms/{self._realm.name}/.well-known/uma-configuration",
            )
            response = requests.get(url, headers=self._headers)
            response.raise_for_status()
            self._config = response.json()
        return self._config

    def resource_set_create(self, token: str, name: str, **kwargs):
        endpoint = self._get_config()["resource_registration_endpoint"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        headers.update(self._headers)
        payload = {"name": name}
        payload.update(kwargs)
        response = requests.post(endpoint, headers=headers, json=payload)
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:  # pragma: no cover - network dependent
            raise exc
        return response.json() if response.content else None


def get_keycloak_id(client):
    """Get the internal Keycloak identifier for the configured client."""

    clients = client.admin_api_client.get_clients(realm_name=client.realm.name)
    for keycloak_client in clients:
        if keycloak_client.get("clientId") == client.client_id:
            return keycloak_client.get("id")
    return None


def get_authz_api_client(client):
    """Return an adapter exposing the entitlement API."""

    return AuthzAdapter(client.openid_api_client, client.client_id)


def get_openid_client(client):
    """Return a KeycloakOpenID instance configured for the client."""

    server_url, headers = django_keycloak.services.realm.get_realm_server_config(client.realm)
    return CachedKeycloakOpenID(
        server_url=f"{server_url}/",
        realm_name=client.realm.name,
        client_id=client.client_id,
        client_secret_key=client.secret,
        custom_headers=headers or None,
        cached_well_known=client.realm.well_known_oidc if client.realm._well_known_oidc else None,
        cached_certs=client.realm.certs if client.realm._certs else None,
    )


def get_uma1_client(client):
    """Return a minimal UMA client for the realm."""

    return UMAResourceClient(client.realm)


def get_admin_client(client):
    """Return a KeycloakAdmin configured to act as the service account."""

    server_url, headers = django_keycloak.services.realm.get_realm_server_config(client.realm)
    connection = KeycloakOpenIDConnection(
        server_url=f"{server_url}/",
        realm_name=client.realm.name,
        client_id=client.client_id,
        client_secret_key=client.secret,
        custom_headers=headers or None,
    )
    return KeycloakAdmin(connection=connection)


def get_service_account_profile(client):
    """Retrieve or create the service-account profile for the client."""

    if client.service_account_profile:
        return client.service_account_profile

    token_response, initiate_time = get_new_access_token(client=client)

    oidc_profile = django_keycloak.services.oidc_profile._update_or_create(
        client=client,
        token_response=token_response,
        initiate_time=initiate_time,
    )

    client.service_account_profile = oidc_profile
    client.save(update_fields=["service_account_profile"])

    return oidc_profile


def get_new_access_token(client):
    """Obtain a fresh service-account access token."""

    scope = "realm-management openid"
    initiate_time = timezone.now()
    token_response = client.openid_api_client.token(
        grant_type="client_credentials", scope=scope
    )
    return token_response, initiate_time


def get_access_token(client):
    """Return an active access token for the client's service account."""

    oidc_profile = get_service_account_profile(client=client)

    try:
        return django_keycloak.services.oidc_profile.get_active_access_token(
            oidc_profile=oidc_profile
        )
    except TokensExpired:
        token_response, initiate_time = get_new_access_token(client=client)
        oidc_profile = django_keycloak.services.oidc_profile.update_tokens(
            token_model=oidc_profile,
            token_response=token_response,
            initiate_time=initiate_time,
        )
        return oidc_profile.access_token


def build_jwk_set(realm) -> jwk.JWKSet:
    """Return a JWKSet constructed from the cached realm certificates."""

    if not realm._certs:
        django_keycloak.services.realm.refresh_certs(realm)
    return jwk.JWKSet.from_json(json.dumps(realm.certs))
