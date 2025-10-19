==============
Django Keycloak
==============

Django Keycloak integrates `Keycloak <https://www.keycloak.org/>`_ authentication
and authorization flows into Django projects. It provides middleware, reusable
views, authentication backends and management commands to synchronize service
accounts, UMA resources and roles.

The repository includes a Spanish ``README.md`` with an extended tour of the
features. The Sphinx documentation in ``docs/`` mirrors the same content and can
be built locally with ``make -C docs html``.

Key features
============

* Authorization Code login flow with optional automatic creation of local or
  remote users.
* Stateless bearer-token middleware to protect API endpoints.
* UMA resource synchronization for permissions based on scopes.
* Django Admin integration to register Keycloak servers, realms and clients.
* Management commands such as ``keycloak_refresh_realm`` and
  ``keycloak_sync_resources`` to keep metadata up to date.

Quickstart
==========

The library targets Python 3.10+, Django 4.2+ and Keycloak 21+. The fastest way
to try it is by bootstrapping a new Django project:

1. Create and activate a virtual environment and install the dependencies::

      python -m venv .venv
      source .venv/bin/activate
      pip install django
      pip install "git+https://github.com/Tehnari/django-keycloak.git"

2. Start a demo project and add the app configuration::

      django-admin startproject demo
      cd demo

   ``demo/settings.py`` requires the Django Keycloak app, middleware and
   authentication backend::

      INSTALLED_APPS = [
          # ...
          "django.contrib.sessions",
          "django.contrib.messages",
          "django_keycloak",
      ]

      MIDDLEWARE = [
          "django.middleware.security.SecurityMiddleware",
          "django.contrib.sessions.middleware.SessionMiddleware",
          "django.middleware.common.CommonMiddleware",
          "django.middleware.csrf.CsrfViewMiddleware",
          "django.contrib.auth.middleware.AuthenticationMiddleware",
          "django.contrib.messages.middleware.MessageMiddleware",
          "django.middleware.clickjacking.XFrameOptionsMiddleware",
          "django_keycloak.middleware.BaseKeycloakMiddleware",
          "django_keycloak.middleware.RemoteUserAuthenticationMiddleware",  # optional
      ]

      AUTHENTICATION_BACKENDS = [
          "django_keycloak.auth.backends.KeycloakAuthorizationCodeBackend",
          "django.contrib.auth.backends.ModelBackend",
      ]

      LOGIN_URL = "keycloak_login"
      LOGIN_REDIRECT_URL = "home"
      LOGOUT_REDIRECT_URL = "home"
      KEYCLOAK_PERMISSIONS_METHOD = "role"  # or "resource" when using UMA scopes

   For stateless APIs include
   ``django_keycloak.middleware.KeycloakStatelessBearerAuthenticationMiddleware``
   and configure ``KEYCLOAK_BEARER_AUTHENTICATION_EXEMPT_PATHS``.

3. Apply migrations and create a superuser::

      python manage.py migrate
      python manage.py createsuperuser

4. Configure Keycloak:

   * Create a realm (e.g. ``demo``).
   * Register a confidential client with **Standard Flow** enabled and set the
     redirect URI to ``http://127.0.0.1:8000/keycloak/login-complete`` and the
     post-logout URI to ``http://127.0.0.1:8000/keycloak/logout``.
   * Enable the service account and grant it the roles
     ``realm-management:view-clients``, ``realm-management:manage-clients`` and
     ``view-users`` (add ``manage-users`` only when creating users from Django).

5. In Django Admin (``http://127.0.0.1:8000/admin/``) create a ``Server`` with
   the public Keycloak URL (``http://127.0.0.1:8080`` by default), then add the
   corresponding ``Realm`` and inline ``Client`` with the ``client_id`` and
   secret. Trigger **Refresh OpenID Connect .well-known** and
   **Refresh Certificates** or execute ``python manage.py keycloak_refresh_realm``.

6. Finally run ``python manage.py runserver`` and visit
   ``http://127.0.0.1:8000/keycloak/login`` to verify the login flow.

Example project
===============

An end-to-end Docker Compose demo lives in ``example/``. It provisions Keycloak,
Nginx, a sample Django site and a REST API. To run it:

#. Ensure ``resource-provider.localhost.yarf.nl``,
   ``resource-provider-api.localhost.yarf.nl`` and
   ``identity.localhost.yarf.nl`` resolve to ``127.0.0.1`` on your machine
   (e.g. via ``/etc/hosts``).
#. From the repository root execute ``docker compose up --build``.
#. Accept the bundled certificate authority found at
   ``example/nginx/certs/ca.pem`` or bypass the certificate warning in the
   browser.

The web application is available at
``https://resource-provider.localhost.yarf.nl/`` (``testuser`` / ``password``),
while Keycloak runs at ``https://identity.localhost.yarf.nl/`` (``admin`` /
``admin``).

Development
===========

Install the project in editable mode with Poetry::

   poetry install

Run the test-suite with::

   poetry run pytest

Sphinx documentation can be built locally with::

   make -C docs html

To publish a package, build a distribution and upload it with Twine::

   poetry build
   twine upload dist/*
