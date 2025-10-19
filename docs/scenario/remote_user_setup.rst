.. _remote_user_setup:

=====================
Setup for remote user
=====================

Si no necesitas crear un ``User`` en la base de datos por cada identidad autenticada puedes activar el modo **remote user**. En este modo Django Keycloak expone un objeto compatible con ``django.contrib.auth`` que vive solo en memoria.

.. note:: El panel de administración de Django requiere usuarios persistidos en base de datos. No habilites el modo remoto para cuentas que deban acceder al admin.

.. warning:: Ajusta este modo **antes** de ejecutar las migraciones para que la tabla ``openidconnectprofile`` se cree con el modelo correcto.

Configura el modelo de perfil OIDC en ``settings.py``:

.. code-block:: python

    KEYCLOAK_OIDC_PROFILE_MODEL = "django_keycloak.RemoteUserOpenIdConnectProfile"

Asegúrate de registrar el middleware remoto:

.. code-block:: python

    MIDDLEWARE = [
        # …
        "django_keycloak.middleware.BaseKeycloakMiddleware",
        "django_keycloak.middleware.RemoteUserAuthenticationMiddleware",
    ]

De forma predeterminada se usa ``django_keycloak.remote_user.KeycloakRemoteUser``. Si necesitas atributos adicionales define una clase propia e indícala mediante ``KEYCLOAK_REMOTE_USER_MODEL``:

.. code-block:: python

    KEYCLOAK_REMOTE_USER_MODEL = "path.to.MyRemoteUser"

El método ``RemoteUserOpenIdConnectProfile.user`` instanciará la clase configurada con los datos devueltos por ``userinfo`` (token de acceso). Puedes extenderla para mapear atributos personalizados.
