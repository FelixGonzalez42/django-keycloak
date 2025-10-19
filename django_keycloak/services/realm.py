from __future__ import annotations

from typing import Dict, Tuple

try:
    from urllib.parse import urljoin, urlparse
except ImportError:  # pragma: no cover
    from urlparse import urljoin, urlparse  # type: ignore

from keycloak import KeycloakOpenID


def get_realm_server_config(realm) -> Tuple[str, Dict[str, str]]:
    """Return the Keycloak base URL and headers for the given realm."""

    headers: Dict[str, str] = {}
    server_url = realm.server.url.rstrip("/")

    if realm.server.internal_url:
        server_url = realm.server.internal_url.rstrip("/")
        parsed_url = urlparse(realm.server.url)
        headers["Host"] = parsed_url.netloc

        if parsed_url.scheme == "https":
            headers["X-Forwarded-Proto"] = "https"

    return server_url, headers


def _build_openid_client(realm, client_id: str = "", client_secret: str | None = None) -> KeycloakOpenID:
    server_url, headers = get_realm_server_config(realm)
    return KeycloakOpenID(
        server_url=f"{server_url}/",
        realm_name=realm.name,
        client_id=client_id,
        client_secret_key=client_secret,
        custom_headers=headers or None,
    )


def refresh_certs(realm):
    """Refresh the cached JWKS for the realm."""

    client = getattr(realm, "client", None)
    openid = _build_openid_client(
        realm,
        client_id=client.client_id if client else "",
        client_secret=client.secret if client else None,
    )

    realm.certs = openid.certs()
    realm.save(update_fields=["_certs"])
    return realm


def refresh_well_known_oidc(realm):
    """Refresh the cached OIDC discovery document for the realm."""

    openid = _build_openid_client(realm)
    realm.well_known_oidc = openid.well_known()
    realm.save(update_fields=["_well_known_oidc"])
    return realm


def get_issuer(realm) -> str:
    """Return the issuer URL used to validate tokens for the realm."""

    if not realm._well_known_oidc:
        refresh_well_known_oidc(realm)

    issuer = realm.well_known_oidc["issuer"]

    if realm.server.internal_url:
        return issuer.replace(realm.server.internal_url.rstrip("/"), realm.server.url.rstrip("/"), 1)

    return issuer


def build_endpoint(realm, path: str) -> str:
    """Construct an absolute URL for the realm based on the configured server."""

    server_url, _ = get_realm_server_config(realm)
    return urljoin(f"{server_url}/", path.lstrip("/"))
