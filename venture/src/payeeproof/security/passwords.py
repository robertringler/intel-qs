"""Password hashing (argon2id) and password policy."""

from __future__ import annotations

from functools import lru_cache
from importlib import resources

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

# OWASP-recommended argon2id parameters (m=19 MiB, t=2, p=1) are the floor; we use m=64 MiB, t=3.
_hasher = PasswordHasher(time_cost=3, memory_cost=64 * 1024, parallelism=2, hash_len=32, salt_len=16)

MIN_LENGTH = 12
MAX_LENGTH = 256


class PasswordPolicyError(ValueError):
    pass


@lru_cache(maxsize=1)
def _common_passwords() -> frozenset[str]:
    text = resources.files("payeeproof.data").joinpath("common_passwords.txt").read_text()
    return frozenset(line.strip().lower() for line in text.splitlines() if line.strip())


def check_policy(password: str, email: str | None = None) -> None:
    if len(password) < MIN_LENGTH:
        raise PasswordPolicyError(f"Password must be at least {MIN_LENGTH} characters.")
    if len(password) > MAX_LENGTH:
        raise PasswordPolicyError(f"Password must be at most {MAX_LENGTH} characters.")
    lowered = password.lower()
    if lowered in _common_passwords() or len(set(password)) < 5:
        raise PasswordPolicyError("Password is too common or too simple.")
    if email:
        local = email.split("@", 1)[0].lower()
        if len(local) >= 4 and local in lowered:
            raise PasswordPolicyError("Password must not contain your email name.")


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(stored_hash: str, password: str) -> bool:
    try:
        return _hasher.verify(stored_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def needs_rehash(stored_hash: str) -> bool:
    return _hasher.check_needs_rehash(stored_hash)


# A valid hash of a random string, used to equalise timing when a user does not exist.
DUMMY_HASH = _hasher.hash("timing-equaliser-not-a-real-password")
