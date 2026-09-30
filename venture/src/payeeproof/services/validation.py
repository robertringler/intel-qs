"""Input normalisation/validation shared by web and API layers."""

from __future__ import annotations

import re

from ..nacha.routing import is_valid_routing
from .errors import ValidationFailed

_EMAIL = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$"
)
_ACCOUNT = re.compile(r"^[0-9A-Za-z]{4,17}$")


def email(value: str | None, required: bool = True) -> str | None:
    v = (value or "").strip().lower()
    if not v:
        if required:
            raise ValidationFailed("Email is required.")
        return None
    if len(v) > 320 or not _EMAIL.match(v):
        raise ValidationFailed("Enter a valid email address.")
    return v


def phone(value: str | None, required: bool = False) -> str | None:
    """Normalise to +<digits> (E.164-like). US 10-digit numbers get +1."""
    raw = (value or "").strip()
    if not raw:
        if required:
            raise ValidationFailed("Phone number is required.")
        return None
    digits = re.sub(r"\D", "", raw)
    if raw.startswith("+"):
        out = "+" + digits
    elif len(digits) == 10:
        out = "+1" + digits
    elif len(digits) == 11 and digits.startswith("1"):
        out = "+" + digits
    else:
        out = "+" + digits
    if not (8 <= len(out) - 1 <= 15):
        raise ValidationFailed("Enter a valid phone number including area code.")
    return out


def routing(value: str | None) -> str:
    v = re.sub(r"\s", "", value or "")
    if not is_valid_routing(v):
        raise ValidationFailed("Routing number must be 9 digits with a valid ABA check digit.")
    return v


def account(value: str | None) -> str:
    v = re.sub(r"[\s-]", "", value or "")
    if not _ACCOUNT.match(v):
        raise ValidationFailed("Account number must be 4-17 letters or digits.")
    return v


def account_type(value: str | None) -> str:
    v = (value or "checking").strip().lower()
    if v not in ("checking", "savings"):
        raise ValidationFailed("Account type must be checking or savings.")
    return v


def text(value: str | None, field: str, max_len: int, required: bool = False) -> str | None:
    v = (value or "").strip()
    if not v:
        if required:
            raise ValidationFailed(f"{field} is required.")
        return None
    if len(v) > max_len:
        raise ValidationFailed(f"{field} must be at most {max_len} characters.")
    if any(ord(c) < 32 and c not in "\n\t" for c in v):
        raise ValidationFailed(f"{field} contains invalid characters.")
    return v


CHANNELS = ("email", "phone", "vendor_portal", "mail", "in_person", "other", "baseline_review")


def channel(value: str | None) -> str:
    v = (value or "").strip().lower()
    if v not in CHANNELS:
        raise ValidationFailed("Select how the change request was received.")
    return v
