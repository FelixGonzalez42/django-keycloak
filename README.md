# Django Keycloak

Django Keycloak integra la autenticación de **Keycloak** en proyectos Django mediante el flujo de OpenID Connect. La aplicación expone middleware, backends de autenticación, vistas listas para usar y comandos de gestión que facilitan la sincronización de permisos y la administración de clientes desde Django.

> ¿Prefieres una guía paso a paso con capturas? Consulta la documentación generada con Sphinx dentro del directorio `docs/`. Ejecuta `make -C docs html` para construirla localmente.

---

## 🧭 Tabla de características

| Característica | Estado actual | Hoja de ruta / notas |
| --- | --- | --- |
| Inicio de sesión mediante Authorization Code | ✅ Disponible | Incluye middleware, vistas (`keycloak_login`, `keycloak_logout`) y creación automática de usuarios locales o remotos. |
| Middleware portador sin sesión (`KeycloakStatelessBearerAuthenticationMiddleware`) | ✅ Disponible | Valida tokens Bearer en APIs REST y permite excluir rutas con `KEYCLOAK_BEARER_AUTHENTICATION_EXEMPT_PATHS`. |
| Sincronización de recursos UMA | ✅ Disponible | `python manage.py keycloak_sync_resources` publica scopes definidos en tus modelos y actualiza permisos en Keycloak. |
| Administración desde Django Admin | ✅ Disponible | Modelos `Server`, `Realm` y `Client` para registrar múltiples instalaciones de Keycloak desde la interfaz administrativa. |
| Multi-realm / multi-tenant | ✅ Disponible | Puedes añadir varios realms y seleccionar uno dinámicamente con middleware propio basado en dominio o cabeceras. |
| Auditoría y métricas en Django Admin | 🚧 Planeado | Documentaremos un panel de auditoría y métricas básicas para revisar sesiones y fallos de sincronización desde la interfaz administrativa. |
| Rotación automática de secretos vía tareas programadas | 🚧 Planeado | Se evaluará una integración opcional con Celery/cronjobs para rotar el `client_secret` y recargar certificados sin intervención manual. |

---

## 🚀 Quickstart

La forma más rápida de probar la librería es crear un proyecto Django nuevo y conectar un cliente confidencial de Keycloak. Estos pasos están verificados con Python 3.10+, Django 4.2+ y Keycloak 21 o superior.

1. **Instala las dependencias**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install django
   pip install "git+https://github.com/Tehnari/django-keycloak.git"
   django-admin startproject demo
   cd demo
   ```

2. **Registra la app y el middleware de Keycloak** en `demo/settings.py`.

   ```python
   INSTALLED_APPS = [
       # …
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
       "django_keycloak.middleware.RemoteUserAuthenticationMiddleware",  # opcional para usuarios remotos
   ]

   AUTHENTICATION_BACKENDS = [
       "django_keycloak.auth.backends.KeycloakAuthorizationCodeBackend",
       "django.contrib.auth.backends.ModelBackend",
   ]

   LOGIN_URL = "keycloak_login"
   LOGIN_REDIRECT_URL = "home"
   LOGOUT_REDIRECT_URL = "home"
   KEYCLOAK_PERMISSIONS_METHOD = "role"  # o "resource" si usas permisos UMA
   ```

   - Si deseas autenticación tipo API sin sesión, añade `django_keycloak.middleware.KeycloakStatelessBearerAuthenticationMiddleware`.
   - Cambia `KEYCLOAK_OIDC_PROFILE_MODEL` a `"django_keycloak.RemoteUserOpenIdConnectProfile"` para evitar crear usuarios locales.

3. **Aplica las migraciones y crea un superusuario** para entrar al admin de Django.

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Configura Keycloak** (en la consola de administración):

   - Crea un *Realm* nuevo (por ejemplo `demo`).
   - Añade un cliente confidencial (por ejemplo `demo-backend`) con *Standard Flow* habilitado, URI de redirección `http://127.0.0.1:8000/keycloak/login-complete` y URI de logout `http://127.0.0.1:8000/keycloak/logout`.
   - En la pestaña **Credentials** copia el *Secret*.
   - Activa el *Service Account* y concédele los roles mínimos: `realm-management:view-clients`, `realm-management:manage-clients` (para sincronizar permisos) y `view-users`.

5. **Crea el vínculo en Django Admin** (`http://127.0.0.1:8000/admin/`):

   - Añade un **Server** con la URL pública de Keycloak (por ejemplo `http://127.0.0.1:8080`) y, si usas Docker/Proxy, define `internal_url` para las llamadas internas.
   - Dentro de ese servidor crea un **Realm** con el mismo nombre que en Keycloak (`demo`) y agrega un **Client** en la sección inline con el `client_id` y `secret` configurados.
   - Desde las acciones del admin ejecuta **Refresh OpenID Connect .well-known** y **Refresh Certificates** para cachear la configuración, o usa `python manage.py keycloak_refresh_realm`.

6. **Arranca el servidor** y prueba el login en `http://127.0.0.1:8000/keycloak/login`.

   ```bash
   python manage.py runserver
   ```

   Al autenticarte en Keycloak regresarás a Django con la sesión iniciada. Si definiste `LOGIN_REDIRECT_URL = "home"`, asegúrate de tener una vista con nombre `home`.

---

## 🔐 Mejores prácticas para producción

1. **Habilita HTTPS extremo a extremo.** Configura TLS en tu proxy o balanceador y replica los ajustes en Django:

   ```python
   # settings.py
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")  # si la app recibe tráfico tras un proxy
   SECURE_HSTS_SECONDS = 31536000
   SECURE_HSTS_INCLUDE_SUBDOMAINS = True
   SECURE_HSTS_PRELOAD = True
   ```

   Reinicia el servicio después de aplicar los cambios y ejecuta `python manage.py check --deploy` para validar que Django reconoce la configuración segura.

2. **Protege y rota credenciales del cliente.** Define el `client_id` y `client_secret` en variables de entorno y cárgalas desde `settings.py`:

   ```bash
   export KEYCLOAK_CLIENT_ID=demo-backend
   export KEYCLOAK_CLIENT_SECRET="<valor generado en Keycloak>"
   ```

   ```python
   # settings.py
   import os

   KEYCLOAK_DEFAULT_CLIENT = {
       "client_id": os.environ["KEYCLOAK_CLIENT_ID"],
       "secret": os.environ["KEYCLOAK_CLIENT_SECRET"],
   }
   ```

   Rota el secreto periódicamente desde Keycloak y, tras cada cambio, ejecuta `python manage.py keycloak_refresh_realm` para actualizar certificados en Django.

3. **Limita privilegios de la service account.** En la pestaña *Service Account Roles* asigna únicamente `realm-management:view-clients`, `realm-management:manage-clients` y `view-users`. Agrega `manage-users` solo si vas a crear usuarios desde Django con `keycloak_add_user`.

4. **Sincroniza configuración y recursos tras cada despliegue.** Añade tareas programadas (cronjobs o Celery beat) que ejecuten:

   ```bash
   python manage.py keycloak_refresh_realm
   python manage.py keycloak_sync_resources
   ```

   Así te aseguras de contar con certificados actualizados y recursos UMA alineados con tus modelos.

5. **Controla rutas abiertas en APIs protegidas con Bearer.** Cuando uses `KeycloakStatelessBearerAuthenticationMiddleware`, define explícitamente las rutas exentas en `settings.py`:

   ```python
   KEYCLOAK_BEARER_AUTHENTICATION_EXEMPT_PATHS = [r"^/healthz$", r"^/public/"]
   ```

   Mantén las vistas públicas al mínimo y cubre el resto con decoradores o permisos DRF.

6. **Ajusta dominios confiables y cabeceras.** Completa `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` y, si compartes sesión entre subdominios, establece `SESSION_COOKIE_DOMAIN`. Documenta estos valores en tu infraestructura como código.

Consulta la guía completa en `docs/production-guide.rst`.

---

## 🛠️ Comandos útiles

| Comando | Descripción |
| --- | --- |
| `python manage.py keycloak_refresh_realm` | Descarga certificados y el documento `.well-known` para todos los realms configurados. |
| `python manage.py keycloak_sync_resources [--client <client_id>]` | Registra los recursos UMA y sincroniza permisos basados en scopes. |
| `python manage.py keycloak_add_user --realm <realm> --user <username>` | Añade un usuario local de Django al realm correspondiente. |

---

## 📚 Documentación adicional

- `docs/quickstart.rst`: guía extendida paso a paso, incluidos escenarios multi-realm y API.
- `docs/production-guide.rst`: lista de comprobación de seguridad y operación.
- `docs/scenario/`: ejemplos completos para sincronizar usuarios, recursos y permisos.

Para construir la documentación HTML localmente:

```bash
make -C docs html
python -m http.server --directory docs/_build/html
```

---

## 🤝 Contribuir

1. Instala las dependencias de desarrollo: `make install-python`.
2. Ejecuta los tests antes de enviar cambios: `pytest`.
3. Sigue el estilo definido en la carpeta `django_keycloak` y añade pruebas o documentación cuando sea necesario.

---

## 📄 Licencia

Distribuido bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.
