"""Sanitize MCP tool arguments before audit logging.

Removes or masks any field that looks like a credential / sensitive value.
"""

from __future__ import annotations

import copy
import re

# Fields whose values will be masked regardless of nesting level.
_SENSITIVE_KEYS: frozenset[str] = frozenset(
    {
        "password",
        "passwd",
        "pwd",
        "secret",
        "token",
        "api_key",
        "apikey",
        "dsn",
        "connection_string",
        "oracle_password",
        "oracle_user",   # keep user too — minimal surface
    }
)

_MASK = "***"


def sanitize_args(args: dict) -> dict:
    """
    Return a deep-copy of *args* with sensitive values masked.
    Non-dict / non-list values are passed through untouched (they are safe).
    """
    return _sanitize(copy.deepcopy(args))


def _sanitize(obj: object) -> object:
    if isinstance(obj, dict):
        return {
            k: _MASK if _is_sensitive(k) else _sanitize(v)
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [_sanitize(item) for item in obj]
    return obj


def _is_sensitive(key: str) -> bool:
    key_lower = key.lower()
    return key_lower in _SENSITIVE_KEYS or bool(
        re.search(r"(pass|secret|token|cred)", key_lower)
    )
