import base64
import os

import pyotp
import pytest

from payeeproof.config import ConfigError, Settings
from payeeproof.security import passwords, tokens, totp
from payeeproof.security.ratelimit import Limit, MemoryBackend, RateLimiter


def test_password_policy():
    for bad in ["short", "password1234", "aaaaaaaaaaaaaaa", "olivia-is-great-99"]:
        with pytest.raises(passwords.PasswordPolicyError):
            passwords.check_policy(bad, "olivia@acme.test")
    passwords.check_policy("correct horse battery staple 9", "olivia@acme.test")


def test_hash_verify():
    h = passwords.hash_password("correct horse battery staple 9")
    assert h.startswith("$argon2id$")
    assert passwords.verify_password(h, "correct horse battery staple 9")
    assert not passwords.verify_password(h, "wrong")
    assert not passwords.verify_password("not-a-hash", "x")


def test_totp_replay_prevention():
    secret = totp.new_secret()
    code = pyotp.TOTP(secret).now()
    step = totp.verify(secret, code, None)
    assert step is not None
    assert totp.verify(secret, code, step) is None  # replay rejected
    assert totp.verify(secret, "000000" if code != "000000" else "111111", None) is None
    assert totp.verify(secret, "abc", None) is None
    assert "<svg" in totp.qr_svg(totp.provisioning_uri(secret, "a@b.c", "PayeeProof"))


def test_tokens():
    t = tokens.new_token()
    assert len(t) >= 40 and tokens.hash_token(t) != t
    assert tokens.constant_time_equals("a", "a") and not tokens.constant_time_equals("a", "b")
    codes = tokens.new_recovery_codes()
    assert len(set(codes)) == 10


def test_rate_limiter():
    rl = RateLimiter(MemoryBackend())
    lim = Limit("t", 3, 60)
    assert [rl.allow(lim, "x") for _ in range(4)] == [True, True, True, False]
    assert rl.allow(lim, "y")


def k():
    return base64.urlsafe_b64encode(os.urandom(32)).decode()


def good(**over):
    base = {
        "field_encryption_keys": f"a:{k()}",
        "fingerprint_key": k(),
        "network_fingerprint_key": k(),
        "audit_chain_key": k(),
        "cookie_secure": True,
        "mfa_required": True,
        "email_backend": "console",
        "env": "development",
    }
    base.update(over)
    return Settings(**base)


def test_config_validation():
    good().validate_for_runtime()
    with pytest.raises(ConfigError):
        good(field_encryption_keys="").validate_for_runtime()
    with pytest.raises(ConfigError):
        good(field_encryption_keys="a:short").validate_for_runtime()
    same = k()
    with pytest.raises(ConfigError, match="distinct"):
        good(fingerprint_key=same, audit_chain_key=same).validate_for_runtime()
    with pytest.raises(ConfigError):
        good(field_encryption_keys=f"a:{k()},a:{k()}").validate_for_runtime()
    with pytest.raises(ConfigError, match="https"):
        good(
            env="production",
            email_backend="smtp",
            base_url="http://x",
            database_url="postgresql+psycopg://u:strong@h/db",
        ).validate_for_runtime()
    with pytest.raises(ConfigError, match="smtp"):
        good(
            env="production", base_url="https://x", database_url="postgresql+psycopg://u:strong@h/db"
        ).validate_for_runtime()
    good(
        env="production", base_url="https://x", email_backend="smtp", database_url="postgresql+psycopg://u:strong@h/db"
    ).validate_for_runtime()


def test_production_requires_secure_cookie_and_mfa():
    with pytest.raises(ConfigError, match="COOKIE"):
        good(
            env="production",
            base_url="https://x",
            email_backend="smtp",
            cookie_secure=False,
            database_url="postgresql+psycopg://u:strong@h/db",
        ).validate_for_runtime()
    with pytest.raises(ConfigError, match="MFA"):
        good(
            env="production",
            base_url="https://x",
            email_backend="smtp",
            mfa_required=False,
            database_url="postgresql+psycopg://u:strong@h/db",
        ).validate_for_runtime()
    with pytest.raises(ConfigError, match="default database password"):
        good(
            env="production",
            base_url="https://x",
            email_backend="smtp",
            database_url="postgresql+psycopg://payeeproof_app:payeeproof_app@localhost:5432/payeeproof",
        ).validate_for_runtime()
