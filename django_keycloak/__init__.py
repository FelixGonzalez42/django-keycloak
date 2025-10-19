from django.conf import settings

from . import app_settings as defaults

try:  # pragma: no cover - defensive patch for upstream changes
    import keycloak.exceptions as _keycloak_exceptions
except ImportError:  # pragma: no cover - keycloak optional during tests
    _keycloak_exceptions = None
else:
    if _keycloak_exceptions and not hasattr(_keycloak_exceptions, "KeycloakClientError"):
        class KeycloakClientError(_keycloak_exceptions.KeycloakError):
            """Compatibility shim for legacy python-keycloak client errors."""

            pass

        _keycloak_exceptions.KeycloakClientError = KeycloakClientError


default_app_config = 'django_keycloak.apps.KeycloakAppConfig'

# Set some app default settings
for name in dir(defaults):
    if name.isupper() and not hasattr(settings, name):
        setattr(settings, name, getattr(defaults, name))
