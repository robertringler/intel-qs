import base64
import os

import pytest

from payeeproof.security.crypto import (
    DecryptionError,
    FieldCipher,
    account_fingerprint,
    last4,
    network_fingerprint,
    normalize_account,
)


def key():
    return os.urandom(32)


def test_roundtrip_and_context_binding():
    c = FieldCipher([("a", key())])
    t = c.encrypt("123456789", "vba:org1")
    assert t.startswith("v1.a.")
    assert c.decrypt(t, "vba:org1") == "123456789"
    with pytest.raises(DecryptionError):
        c.decrypt(t, "vba:org2")  # ciphertext moved to another tenant fails


def test_nonce_uniqueness():
    c = FieldCipher([("a", key())])
    assert c.encrypt("x", "c") != c.encrypt("x", "c")


def test_tamper_detected():
    c = FieldCipher([("a", key())])
    t = c.encrypt("secret", "ctx")
    v, kid, payload = t.split(".")
    raw = bytearray(base64.urlsafe_b64decode(payload + "=="))
    raw[-1] ^= 1
    bad = f"{v}.{kid}.{base64.urlsafe_b64encode(bytes(raw)).decode().rstrip('=')}"
    with pytest.raises(DecryptionError):
        c.decrypt(bad, "ctx")
    with pytest.raises(DecryptionError):
        c.decrypt("garbage", "ctx")
    with pytest.raises(DecryptionError):
        c.decrypt("v1.zz.AAAA", "ctx")


def test_rotation():
    old, new = key(), key()
    c_old = FieldCipher([("k1", old)])
    t = c_old.encrypt("acct", "ctx")
    c_rot = FieldCipher([("k2", new), ("k1", old)])
    assert c_rot.decrypt(t, "ctx") == "acct"
    assert c_rot.needs_rotation(t)
    t2 = c_rot.encrypt("acct", "ctx")
    assert not c_rot.needs_rotation(t2)


def test_normalization_and_fingerprints():
    assert normalize_account("00012-345 678") == "12345678"
    assert normalize_account("0000") == "0"
    k = key()
    a = account_fingerprint(k, "org1", "011000015", "0012345678")
    b = account_fingerprint(k, "org1", "011000015", "12345678")
    assert a == b
    assert a != account_fingerprint(k, "org2", "011000015", "12345678")
    assert a != account_fingerprint(k, "org1", "026009593", "12345678")
    n1 = network_fingerprint(k, "011000015", "12345678")
    assert n1 == network_fingerprint(k, "011000015", "0012345678")
    assert last4("12") == "**12" and last4("0987654321") == "4321"
