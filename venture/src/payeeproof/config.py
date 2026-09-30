"""Application configuration loaded from environment variables.

Secrets are never given defaults in production. ``Settings.validate_for_runtime``
refuses to start with insecure configuration when ``PP_ENV=production``.
"""

from __future__ import annotations

import base64
import binascii
from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigError(RuntimeError):
    """Raised when configuration is unsafe or incomplete."""


def _decode_key(material: str, name: str) -> bytes:
    try:
        raw = base64.urlsafe_b64decode(material + "=" * (-len(material) % 4))
    except (binascii.Error, ValueError) as exc:
        raise ConfigError(f"{name}: key material is not valid base64") from exc
    if len(raw) != 32:
        raise ConfigError(f"{name}: key must decode to exactly 32 bytes, got {len(raw)}")
    return raw


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PP_", env_file=None, extra="ignore")

    env: Literal["development", "test", "production"] = "development"
    base_url: str = "http://localhost:8000"
    app_name: str = "PayeeProof"

    # Database: the app connects as a NON-superuser role subject to row-level security.
    database_url: str = "postgresql+psycopg://payeeproof_app:payeeproof_app@localhost:5432/payeeproof"
    # Migrations run as the schema owner role.
    migration_database_url: str | None = None
    db_pool_size: int = 10
    db_max_overflow: int = 10

    # Crypto. FIELD_ENCRYPTION_KEYS: comma-separated "kid:base64key"; first entry is primary.
    field_encryption_keys: str = ""
    fingerprint_key: str = ""
    network_fingerprint_key: str = ""
    audit_chain_key: str = ""

    # Sessions
    session_idle_minutes: int = 30
    session_absolute_hours: int = 12
    cookie_secure: bool = True

    # Security posture
    mfa_required: bool = True
    login_max_failures: int = 5
    login_lockout_minutes: int = 15
    max_upload_bytes: int = 5 * 1024 * 1024
    redis_url: str | None = None
    trusted_proxy_count: int = 0

    # Email
    email_backend: Literal["console", "smtp", "memory"] = "console"
    email_from: str = "PayeeProof <no-reply@localhost>"
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_starttls: bool = True

    # Billing (Stripe). Billing is disabled unless secret key and webhook secret are set.
    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None
    stripe_price_starter_monthly: str | None = None
    stripe_price_starter_annual: str | None = None
    stripe_price_growth_monthly: str | None = None
    stripe_price_growth_annual: str | None = None
    stripe_price_scale_monthly: str | None = None
    stripe_price_scale_annual: str | None = None
    billing_grace_days: int = 7

    # Observability
    log_level: str = "INFO"
    metrics_token: str | None = None
    sentry_dsn: str | None = None

    # Network (cross-customer reputation) is opt-in per org; this switch disables it globally.
    network_enabled: bool = True

    worker_poll_seconds: float = Field(default=2.0, ge=0.1)

    @field_validator("base_url")
    @classmethod
    def _strip_slash(cls, v: str) -> str:
        return v.rstrip("/")

    # ---- derived key material -------------------------------------------------
    def encryption_keyring(self) -> list[tuple[str, bytes]]:
        if not self.field_encryption_keys:
            raise ConfigError("PP_FIELD_ENCRYPTION_KEYS is not set")
        ring: list[tuple[str, bytes]] = []
        for raw in self.field_encryption_keys.split(","):
            item = raw.strip()
            if not item:
                continue
            if ":" not in item:
                raise ConfigError("PP_FIELD_ENCRYPTION_KEYS entries must be 'kid:base64key'")
            kid, material = item.split(":", 1)
            if not kid.isalnum() or len(kid) > 16:
                raise ConfigError("key id must be alphanumeric, <=16 chars")
            ring.append((kid, _decode_key(material, f"PP_FIELD_ENCRYPTION_KEYS[{kid}]")))
        if not ring:
            raise ConfigError("PP_FIELD_ENCRYPTION_KEYS has no keys")
        if len({k for k, _ in ring}) != len(ring):
            raise ConfigError("duplicate key id in PP_FIELD_ENCRYPTION_KEYS")
        return ring

    def key_bytes(self, name: str) -> bytes:
        value = getattr(self, name)
        if not value:
            raise ConfigError(f"PP_{name.upper()} is not set")
        return _decode_key(value, f"PP_{name.upper()}")

    @property
    def billing_enabled(self) -> bool:
        return bool(self.stripe_secret_key and self.stripe_webhook_secret)

    def validate_for_runtime(self) -> None:
        """Fail fast on unsafe configuration."""
        self.encryption_keyring()
        keys = {n: self.key_bytes(n) for n in ("fingerprint_key", "network_fingerprint_key", "audit_chain_key")}
        enc = {k for _, k in self.encryption_keyring()}
        all_keys = list(keys.values()) + list(enc)
        if len(set(all_keys)) != len(all_keys):
            raise ConfigError("encryption, fingerprint, network and audit keys must all be distinct")
        if self.env == "production":
            if not self.cookie_secure:
                raise ConfigError("PP_COOKIE_SECURE must be true in production")
            if not self.base_url.startswith("https://"):
                raise ConfigError("PP_BASE_URL must be https in production")
            if self.email_backend != "smtp":
                raise ConfigError("PP_EMAIL_BACKEND must be 'smtp' in production")
            if "payeeproof_app:payeeproof_app@" in self.database_url:
                raise ConfigError("default database password must not be used in production")
            if not self.mfa_required:
                raise ConfigError("MFA cannot be disabled in production")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
