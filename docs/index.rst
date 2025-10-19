Bienvenido a la documentación de Django Keycloak
================================================

Django Keycloak añade autenticación basada en OpenID Connect y autorización UMA a tus proyectos Django reutilizando toda la infraestructura de Keycloak. La librería funciona sobre el sistema de autenticación estándar de Django y proporciona middleware, backends y vistas preparados para iniciar sesión, cerrar sesión, registrar usuarios y validar tokens portadores.

Si es tu primera vez, comienza por la :doc:`guía rápida <quickstart>`; allí encontrarás un recorrido completo para instalar, configurar Keycloak y proteger tus vistas en minutos.

.. toctree::
   :maxdepth: 2
   :caption: Guías principales

   quickstart
   production-guide

.. toctree::
   :maxdepth: 2
   :caption: Escenarios paso a paso

   scenario/example_project
   scenario/initial_setup
   scenario/local_user_setup
   scenario/remote_user_setup
   scenario/permissions_by_roles
   scenario/permissions_by_resources_and_scopes
   scenario/migrating
   scenario/multi_tenancy

Funciones principales
=====================

- Backends de autenticación para flujos de **authorization code**, **password credentials** y validación de **bearer tokens**.
- Middleware para inyectar el *realm* en cada petición, gestionar sesiones y validar tokens portadores sin estado.
- Modelos y comandos de gestión para sincronizar permisos, recursos UMA y cuentas de servicio.
- Vistas listas (`/keycloak/login`, `/keycloak/logout`, `/keycloak/register`) que implementan el flujo completo de OpenID Connect.

Compatibilidad
==============

- Python 3.10 o superior.
- Django 4.1 y 4.2.
- Keycloak 20 o superior (probado con Keycloak.x y distribución Quarkus).
- Cliente ``python-keycloak`` >= 4.1.

Consulta el archivo ``README.md`` en la raíz del repositorio para conocer el historial de cambios y enlaces adicionales.
