==========
Quickstart
==========

Esta guía explica cómo integrar Django Keycloak desde cero. Los pasos han sido probados con Python 3.10, Django 4.2 y Keycloak 21.

Requisitos previos
==================

- Tener un servidor de Keycloak accesible (local o remoto) con un usuario administrador.
- Python 3.10+ y pip instalados.
- Conocimientos básicos de cómo crear proyectos Django.

Instalación de Django Keycloak
==============================

1. Crea y activa un entorno virtual:

   .. code-block:: bash

      python -m venv .venv
      source .venv/bin/activate

2. Instala Django y la librería desde el repositorio:

   .. code-block:: bash

      pip install django
      pip install "git+https://github.com/FelixGonzalez42/django-keycloak.git"

3. Genera un proyecto de ejemplo y entra en él:

   .. code-block:: bash

      django-admin startproject demo
      cd demo

Configuración de Keycloak
=========================

1. **Crea un Realm** nuevo (p. ej. ``demo``) desde *Master* > *Add realm*.
2. **Registra un cliente confidencial** (p. ej. ``demo-backend``):

   - *Client Type*: OpenID Connect.
   - *Client Authentication*: ON (genera un ``Secret``).
   - *Standard Flow Enabled*: ON.
   - *Valid Redirect URIs*: ``http://127.0.0.1:8000/keycloak/login-complete``.
   - *Valid Post Logout Redirect URIs*: ``http://127.0.0.1:8000/keycloak/logout``.
   - *Web Origins*: ``http://127.0.0.1:8000`` (o ``*`` solo para pruebas locales).

3. **Activa el Service Account** en la pestaña *Service Account Roles* y otórgale al menos:

   - ``realm-management:view-clients`` y ``realm-management:manage-clients`` para sincronizar permisos y recursos.
   - ``view-users`` para consultar información del usuario autenticado.

4. Copia el ``Client ID`` y el ``Secret``: los necesitarás en Django.

Configuración de Django
=======================

1. Añade la aplicación, middleware y backend en ``demo/settings.py``:

   .. code-block:: python

      INSTALLED_APPS = [
          # Aplicaciones de Django…
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
          "django_keycloak.middleware.RemoteUserAuthenticationMiddleware",
      ]

      AUTHENTICATION_BACKENDS = [
          "django_keycloak.auth.backends.KeycloakAuthorizationCodeBackend",
          "django.contrib.auth.backends.ModelBackend",
      ]

      LOGIN_URL = "keycloak_login"
      LOGIN_REDIRECT_URL = "home"
      LOGOUT_REDIRECT_URL = "home"
      KEYCLOAK_PERMISSIONS_METHOD = "role"

   - Para APIs sin sesión añade ``django_keycloak.middleware.KeycloakStatelessBearerAuthenticationMiddleware``.
   - Si prefieres usuarios 100 % remotos ajusta ``KEYCLOAK_OIDC_PROFILE_MODEL = "django_keycloak.RemoteUserOpenIdConnectProfile"``.
   - ``BaseKeycloakMiddleware`` añade el ``realm`` a la petición y sincroniza la
     cookie ``session_state`` cuando exista un perfil OIDC activo.
   - ``RemoteUserAuthenticationMiddleware`` recupera al usuario remoto de la
     sesión de Keycloak y vuelve a poblar ``request.user`` a partir del perfil
     OIDC sin ejecutar un nuevo intercambio de tokens.
   - ``KeycloakStatelessBearerAuthenticationMiddleware`` valida tokens Bearer en
     cada request que no esté en ``KEYCLOAK_BEARER_AUTHENTICATION_EXEMPT_PATHS``.
   - ``KeycloakAuthorizationCodeBackend`` intercambia el *authorization code*
     por tokens y guarda el perfil OIDC asociado al usuario de Django.
   - ``KeycloakPasswordCredentialsBackend`` permite autenticar mediante usuario
     y contraseña directamente contra Keycloak.
   - ``KeycloakIDTokenAuthorizationBackend`` acepta un ID Token ya emitido por
     Keycloak, útil para integraciones server-to-server.

2. Aplica migraciones y crea un superusuario para ingresar al admin:

   .. code-block:: bash

      python manage.py migrate
      python manage.py createsuperuser

3. Ejecuta el servidor de desarrollo:

   .. code-block:: bash

      python manage.py runserver

4. Abre ``http://127.0.0.1:8000/admin`` y registra la conexión con Keycloak:

   - **Server**: usa la URL pública de Keycloak (p. ej. ``http://127.0.0.1:8080``). El campo ``internal_url`` permite definir una URL alternativa para llamadas internas (útil con Docker/Proxy).
   - **Realm**: crea un registro con el nombre del realm (``demo``) y añade el **Client** inline con ``client_id`` y ``secret``.
   - Desde las acciones del admin ejecuta **Refresh OpenID Connect .well-known** y **Refresh Certificates** para cachear la configuración.

5. Comprueba el inicio de sesión entrando a ``http://127.0.0.1:8000/keycloak/login``. Tras autenticarse en Keycloak se crea o actualiza el usuario en Django y se redirige a ``LOGIN_REDIRECT_URL``.

Buenas prácticas inmediatas
===========================

- Cambia ``LOGIN_REDIRECT_URL`` y ``LOGOUT_REDIRECT_URL`` por vistas reales de tu proyecto.
- Protege tus vistas usando decoradores estándar de Django como ``@login_required``.
- Define ``KEYCLOAK_BEARER_AUTHENTICATION_EXEMPT_PATHS`` cuando uses autenticación portadora sin sesión.

Próximos pasos
==============

- Revisa :doc:`production-guide` para endurecer la seguridad antes de desplegar.
- Consulta los escenarios en ``docs/scenario`` para sincronizar permisos, usuarios remotos o multi-tenant.
