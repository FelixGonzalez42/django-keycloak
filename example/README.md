# Example project

This folder contains the Docker Compose showcase used in the documentation. It
spins up the following services:

- `identity` – Keycloak with a PostgreSQL backend.
- `resource-provider` – a small Django web application.
- `resource-provider-api` – a Django REST-style API protected with bearer tokens.
- `nginx` – reverse proxy that terminates TLS certificates for the demo domains.

## Prerequisites

- Docker and the Compose plugin installed.
- Local DNS entries for the demo domains. Add the following lines to your
  `hosts` file so they resolve to `127.0.0.1`:

  ```text
  127.0.0.1 resource-provider.localhost.yarf.nl
  127.0.0.1 resource-provider-api.localhost.yarf.nl
  127.0.0.1 identity.localhost.yarf.nl
  ```

## Run the project

From the repository root run:

```bash
docker compose up --build
```

The first run builds the Django images and imports the realms from
`example/keycloak/export`. A self-signed certificate authority is located at
`example/nginx/certs/ca.pem`; import it into your browser or skip the TLS warning
when visiting the demo URLs.

## URLs and credentials

| Service | URL | Username | Password |
|---------|-----|----------|----------|
| Web app | https://resource-provider.localhost.yarf.nl/ | `testuser` | `password` |
| Web admin | https://resource-provider.localhost.yarf.nl/admin/ | `admin` | `password` |
| API | https://resource-provider-api.localhost.yarf.nl/ | `admin` | `password` |
| Keycloak | https://identity.localhost.yarf.nl/ | `admin` | `admin` |

The service account associated with the `resource-provider` client already has
`realm-management:view-clients`, `realm-management:manage-clients` and
`view-users` so the synchronization commands in the docs work out of the box.
