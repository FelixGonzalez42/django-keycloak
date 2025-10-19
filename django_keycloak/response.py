import re
from typing import Dict, Iterable, Optional

from django.http.response import HttpResponse


_TOKEN_RE = re.compile(r"^[!#$%&'*+\-.^_`|~0-9A-Za-z]+$")


def _sanitize_token(value: str, default: Optional[str] = None) -> Optional[str]:
    """Return a RFC7235 token or a safe default."""

    token = str(value).strip()
    if _TOKEN_RE.fullmatch(token):
        return token
    return default


def _format_auth_attributes(attributes: Dict[str, object]) -> Iterable[str]:
    """Yield sanitized WWW-Authenticate attribute pairs."""

    for key, raw_value in attributes.items():
        sanitized_key = _sanitize_token(key)
        if not sanitized_key:
            continue

        value = str(raw_value).replace("\\", "\\\\").replace('"', '\\"')
        value = value.replace("\r", "").replace("\n", "")
        yield f'{sanitized_key}="{value}"'


class HttpResponseNotAuthorized(HttpResponse):
    status_code = 401

    def __init__(self, content=b'', authorization_method='Bearer',
                 attributes=None, *args, **kwargs):
        super(HttpResponseNotAuthorized, self).__init__(content, *args,
                                                        **kwargs)

        attributes = attributes or {}

        sanitized_method = _sanitize_token(authorization_method, default='Bearer') or 'Bearer'
        attribute_segments = list(_format_auth_attributes(attributes))

        header_value = sanitized_method
        if attribute_segments:
            header_value = f"{sanitized_method} {', '.join(attribute_segments)}"

        self['WWW-Authenticate'] = header_value
