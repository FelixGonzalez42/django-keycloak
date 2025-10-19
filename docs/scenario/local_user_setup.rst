.. _local_user_setup:

============================
Setup for local user storage
============================

.. toctree::
   :maxdepth: 4

En el modo **local** se crea un `objeto User de Django <https://docs.djangoproject.com/en/stable/topics/auth/default/#user-objects>`_ por cada identidad autenticada. Úsalo cuando necesites relacionar modelos propios con usuarios o aprovechar la administración estándar de Django. Si prefieres evitar usuarios locales consulta el escenario :ref:`remote_user_setup`.

Este es el comportamiento predeterminado de Django Keycloak, por lo que no necesitas cambiar ajustes. Asegúrate de que ``KEYCLOAK_OIDC_PROFILE_MODEL`` apunta a ``django_keycloak.OpenIdConnectProfile`` (valor por defecto). Este modelo almacena tokens, fecha de expiración y un FK al usuario de Django.

.. code-block:: python

    # settings.py
    KEYCLOAK_OIDC_PROFILE_MODEL = "django_keycloak.OpenIdConnectProfile"

Cuando se recibe un token válido el backend ``KeycloakAuthorizationCodeBackend`` crea o actualiza el usuario local con los campos ``email``, ``first_name`` y ``last_name`` del ``id_token``. Posteriormente sincroniza los permisos leyendo los roles o scopes configurados.
