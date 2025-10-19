#!/usr/bin/env sh
set -e

pip install -e ./../django-keycloak/
pip install -e ./../python-keycloak-client/ || true
pip install -e ./../django-dynamic-fixtures/ || true

if [ -f db.sqlite3 ]; then
    echo "Application already initialized."
else
    echo "Initializing application"

    # Run migrations
    python manage.py migrate

    python manage.py load_dynamic_fixtures myapp
fi

CERTIFI_PATH=$(python - <<'PY'
import certifi
print(certifi.where())
PY
)

if [ -f "$CERTIFI_PATH" ] && ! grep -q "Yarf" "$CERTIFI_PATH"; then
    echo "Add CA to trusted pool"
    {
        printf '\n\n# Yarf\n'
        cat /usr/src/ca.pem
    } >> "$CERTIFI_PATH"
else
    echo "CA already added"
fi

exec "$@"
