======================
Guía de producción
======================

Este documento recopila recomendaciones para desplegar Django Keycloak de forma segura en entornos productivos.

Checklist de seguridad
======================

1. **HTTPS obligatorio**

   - Activa TLS en el balanceador o servidor frontal.
   - Ajusta en Django:

     .. code-block:: python

        SECURE_SSL_REDIRECT = True
        SESSION_COOKIE_SECURE = True
        CSRF_COOKIE_SECURE = True
        SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")  # si usas proxy

2. **Cookies y sesión**

   - Personaliza ``KEYCLOAK_SESSION_STATE_COOKIE_NAME`` para evitar colisiones con otras apps.
   - Define ``SESSION_COOKIE_DOMAIN`` cuando compartas autenticación entre subdominios.
   - Si usas ``KeycloakStatelessBearerAuthenticationMiddleware`` añade ``KEYCLOAK_BEARER_AUTHENTICATION_EXEMPT_PATHS`` con regex de rutas públicas.

3. **Gestión de secretos**

   - Almacena ``client_id`` y ``secret`` en un gestor de secretos o variables de entorno.
   - Rota el secreto de Keycloak periódicamente; ejecuta ``python manage.py keycloak_refresh_realm`` tras cada rotación para actualizar certificados.

4. **Roles mínimos para la service account**

   - Limita la cuenta de servicio a los roles estrictamente necesarios:

     - ``realm-management:view-clients`` y ``realm-management:manage-clients`` para sincronizar UMA.
     - ``view-users`` y ``query-users`` si necesitas rellenar perfiles locales.
     - Añade ``manage-users`` únicamente si vas a crear usuarios desde Django con ``keycloak_add_user``.

5. **Protección CSRF y cabeceras**

   - Ajusta ``CSRF_TRUSTED_ORIGINS`` con tus dominios.
   - Habilita ``SECURE_HSTS_SECONDS`` (por ejemplo ``31536000``) y ``SECURE_HSTS_INCLUDE_SUBDOMAINS``.

6. **Registro y auditoría**

   - Habilita el nivel ``INFO`` para ``django_keycloak`` y almacena logs de acceso.
   - Activa eventos en Keycloak para detectar sesiones sospechosas.

Automatización operativa
========================

- **Sincronizar configuración**: Programa ``python manage.py keycloak_refresh_realm`` cada cierto tiempo (ej. ``cron``) para mantener certificados y metadatos actualizados.
- **Recursos UMA**: si usas permisos por recursos y scopes, automatiza ``python manage.py keycloak_sync_resources`` durante tus despliegues.
- **Tokens caducados**: cuando detectes ``401`` por expiración de tokens de servicio, ejecuta ``keycloak_refresh_realm`` y reinicia la app para renovar el caché.

Multi-tenancy
=============

El middleware incluido selecciona el primer ``Realm`` disponible. Para multi-tenant:

- Define un middleware propio que resuelva ``request.realm`` según el dominio o cabecera.
- Registra cada ``Realm`` y ``Client`` en el admin con sus respectivos secretos.
- Usa rutas distintas o subdominios para evitar confusiones de sesión.

Integración con API
===================

Para proteger endpoints tipo REST:

1. Añade ``django_keycloak.middleware.KeycloakStatelessBearerAuthenticationMiddleware`` después del middleware de sesiones.
2. Define ``KEYCLOAK_BEARER_AUTHENTICATION_EXEMPT_PATHS`` con expresiones regulares para health checks públicos.
3. Usa ``request.user`` dentro de tus vistas: el backend ``KeycloakIDTokenAuthorizationBackend`` valida el token y rellena permisos basados en roles o scopes.

Planes de contingencia
======================

- **Fallo de Keycloak**: configura un mensaje claro cuando el middleware no obtenga token y documenta procedimientos manuales de recuperación.
- **Respaldo de configuración**: exporta el realm de Keycloak tras cada cambio y versiona los archivos resultantes.
- **Pruebas**: incluye escenarios E2E que validen login, logout y refresco de tokens antes de cada despliegue.
