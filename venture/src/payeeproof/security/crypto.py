"""Field-level encryption and keyed fingerprints for bank account numbers.

* Encryption: AES-256-GCM with a random 96-bit nonce. Ciphertext is bound to its
  context (table/column/org) through GCM associated data, so a ciphertext copied
  into another tenant's row fails authentication.
  Format: ``v1.<kid>.<urlsafe-b64(nonce || ciphertext+tag)>``. The key id enables
  rotation: new writes use the primary key, reads use whichever key id is embedded.
* Fingerprints: HMAC-SHA256 over a normalised (routing, account) pair. Per-tenant
  fingerprints include the org id, so equal accounts in two tenants do not
  correlate. Network fingerprints (opt-in reputation sharing) omit the org id and
  use a separate key.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import re

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

_NON_ALNUM = re.compile(r"[^0-9A-Za-z]")


class DecryptionError(Exception):
    pass


def _b64e(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode().rstrip("=")


def _b64d(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


class FieldCipher:
    def __init__(self, keyring: list[tuple[str, bytes]]):
        if not keyring:
            raise ValueError("empty keyring")
        self._primary_kid, primary = keyring[0]
        self._keys = {kid: AESGCM(key) for kid, key in keyring}
        del primary

    def encrypt(self, plaintext: str, context: str) -> str:
        nonce = os.urandom(12)
        ct = self._keys[self._primary_kid].encrypt(nonce, plaintext.encode(), context.encode())
        return f"v1.{self._primary_kid}.{_b64e(nonce + ct)}"

    def decrypt(self, token: str, context: str) -> str:
        try:
            version, kid, payload = token.split(".", 2)
        except ValueError as exc:
            raise DecryptionError("malformed ciphertext") from exc
        if version != "v1" or kid not in self._keys:
            raise DecryptionError("unknown ciphertext version or key id")
        raw = _b64d(payload)
        if len(raw) < 12 + 16:
            raise DecryptionError("ciphertext too short")
        try:
            return self._keys[kid].decrypt(raw[:12], raw[12:], context.encode()).decode()
        except InvalidTag as exc:
            raise DecryptionError("authentication failed") from exc

    def needs_rotation(self, token: str) -> bool:
        parts = token.split(".", 2)
        return len(parts) != 3 or parts[1] != self._primary_kid


def normalize_account(account: str) -> str:
    """Normalise an account number for matching.

    Removes spaces, dashes and other separators, upper-cases letters and strips
    leading zeros: ERP exports and bank files zero-pad inconsistently, and at a
    single routing number two genuinely different accounts differing only in
    leading zeros are not issued in practice.
    """
    cleaned = _NON_ALNUM.sub("", account).upper().lstrip("0")
    return cleaned or "0"


def account_fingerprint(key: bytes, org_id: str, routing: str, account: str) -> str:
    msg = f"{org_id}|{routing.strip()}|{normalize_account(account)}".encode()
    return hmac.new(key, msg, hashlib.sha256).hexdigest()


def network_fingerprint(key: bytes, routing: str, account: str) -> str:
    msg = f"{routing.strip()}|{normalize_account(account)}".encode()
    return hmac.new(key, msg, hashlib.sha256).hexdigest()


def last4(account: str) -> str:
    n = normalize_account(account)
    return n[-4:].rjust(4, "*")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
