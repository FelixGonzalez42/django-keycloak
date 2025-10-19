.. _initial_setup:

=============
Initial setup
=============

Server configuration
====================

Registra tu servidor de Keycloak desde el admin de Django en ``Keycloak › Servers``.

.. image:: /add-server.png

.. note:: Si tu aplicación accede a Keycloak mediante una URL distinta a la pública (por ejemplo, servicios Docker detrás de un proxy), indica esa URL en ``internal_url``. Django Keycloak usará ``internal_url`` para las llamadas directas pero seguirá redirigiendo a los usuarios a la URL pública.

Realm configuration
===================

Después de crear un `Realm <https://www.keycloak.org/docs/latest/server_admin/#creating-and-configuring-a-realm>`_ y un `cliente confidencial <https://www.keycloak.org/docs/latest/server_admin/#client-registration>`_ en Keycloak, añádelos en el admin de Django.

.. note:: Django Keycloak soporta múltiples realms. Si configuras más de uno necesitarás escribir tu propio middleware que asigne ``request.realm`` según el dominio o la cabecera. El middleware por defecto toma siempre el primer realm disponible en la base de datos.

.. image:: /add-realm.png

Acciones recomendadas
=====================

Tras registrar el realm ejecuta las siguientes acciones desde el listado de realms o mediante los comandos equivalentes:

* :ref:`refresh_openid_connect_well_known` — cachea el documento ``.well-known`` (:command:`python manage.py keycloak_refresh_realm`).
* :ref:`refresh_certificates` — actualiza los certificados públicos (:command:`python manage.py keycloak_refresh_realm`).
* :ref:`synchronize_permissions` — necesario cuando utilizas el sistema de permisos basado en scopes (:command:`python manage.py keycloak_sync_resources`).

Tools
=====

.. _refresh_openid_connect_well_known:

----------------------------------
Refresh OpenID Connect .well-known
----------------------------------

En el admin aplica la acción "Refresh OpenID Connect .well-known" para un realm. Esto descarga el documento `OpenID Provider Configuration <https://www.rfc-editor.org/rfc/rfc8414>`_ y lo almacena en la base de datos, evitando llamadas repetidas en cada autenticación.

.. image:: /refresh_well_known.png

.. _refresh_certificates:

--------------------
Refresh Certificates
--------------------

Actualiza los certificados JWKS del realm. Estos certificados se usan para validar los tokens emitidos por Keycloak.

.. image:: /refresh_certificates.png

-------------------
Clear client tokens
-------------------

Mientras depuras permisos del *service account* puede ser necesario limpiar la sesión almacenada. Esta acción borra los tokens de la cuenta de servicio y fuerza a Django Keycloak a solicitar uno nuevo.

.. image:: /clear_client_tokens.png
