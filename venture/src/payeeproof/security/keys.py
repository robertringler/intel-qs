"""Process-wide access to key material derived from settings."""

from __future__ import annotations

from functools import lru_cache

from ..config import get_settings
from .crypto import FieldCipher


@lru_cache(maxsize=1)
def cipher() -> FieldCipher:
    return FieldCipher(get_settings().encryption_keyring())


def fingerprint_key() -> bytes:
    return get_settings().key_bytes("fingerprint_key")


def network_key() -> bytes:
    return get_settings().key_bytes("network_fingerprint_key")


def reset_caches() -> None:
    cipher.cache_clear()
