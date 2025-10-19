.. _example_project:

================================
Testing with the Example project
================================

The repository ships with a Docker Compose showcase under ``example/``. It
starts Keycloak, a PostgreSQL database, an Nginx reverse proxy, a Django web app
and a separate API service so you can exercise both browser and bearer-token
flows.

Prerequisites
=============

* Docker and the Compose plugin installed.
* Hostnames ``resource-provider.localhost.yarf.nl``,
  ``resource-provider-api.localhost.yarf.nl`` and
  ``identity.localhost.yarf.nl`` resolving to ``127.0.0.1`` (add them to
  ``/etc/hosts`` on Linux/macOS or ``C:\Windows\System32\drivers\etc\hosts`` on
  Windows).

Running the stack
=================

.. code-block:: bash

    docker compose up --build

Compose pulls the latest Keycloak image, imports the realms found in
``example/keycloak/export`` and builds the Django services from source. The
self-signed certificate authority is stored in ``example/nginx/certs/ca.pem``;
import it into your browser or accept the warning page during testing.

Services
========

* Web app: https://resource-provider.localhost.yarf.nl/
* API: https://resource-provider-api.localhost.yarf.nl/
* Django admin (web app): https://resource-provider.localhost.yarf.nl/admin/
* Django admin (API): https://resource-provider-api.localhost.yarf.nl/admin/
* Keycloak: https://identity.localhost.yarf.nl/

Default credentials
===================

* Keycloak administrator: ``admin`` / ``admin``
* Web app Django admin: ``admin`` / ``password``
* API Django admin: ``admin`` / ``password``
* Demo Keycloak user: ``testuser`` / ``password``

The Keycloak service account already owns the roles required to run
``keycloak_sync_resources`` and the UMA synchronization examples described in the
rest of the documentation.
