"""Default organisation control settings (overridable per org, within bounds)."""

from __future__ import annotations

from typing import Any

from .errors import ValidationFailed

DEFAULTS: dict[str, Any] = {
    "sod_approver_not_verifier": True,
    "recent_change_days": 14,
    "dual_approval_threshold_cents": 5_000_000,
    "large_round_amount_cents": 1_000_000,
    "anomaly_min_history": 5,
    "anomaly_z": 3.5,
    "name_match_threshold": 0.5,
    "attestation_ttl_hours": 72,
    "known_contact_min_age_days": 30,
    "block_on_integrity_issues": True,
}

BOUNDS: dict[str, tuple[type, Any, Any]] = {
    "sod_approver_not_verifier": (bool, None, None),
    "recent_change_days": (int, 1, 90),
    "dual_approval_threshold_cents": (int, 0, 10**12),
    "large_round_amount_cents": (int, 100_000, 10**12),
    "anomaly_min_history": (int, 3, 50),
    "anomaly_z": (float, 2.0, 10.0),
    "name_match_threshold": (float, 0.0, 1.0),
    "attestation_ttl_hours": (int, 1, 168),
    "known_contact_min_age_days": (int, 0, 365),
    "block_on_integrity_issues": (bool, None, None),
}


def effective(settings: dict[str, Any] | None) -> dict[str, Any]:
    out = dict(DEFAULTS)
    for k, v in (settings or {}).items():
        if k in DEFAULTS:
            out[k] = v
    return out


def validate_update(values: dict[str, Any]) -> dict[str, Any]:
    clean: dict[str, Any] = {}
    for k, v in values.items():
        if k not in BOUNDS:
            raise ValidationFailed(f"Unknown setting: {k}")
        typ, lo, hi = BOUNDS[k]
        try:
            if typ is bool:
                cv: Any = v if isinstance(v, bool) else str(v).lower() in ("1", "true", "on", "yes")
            else:
                cv = typ(v)
        except (TypeError, ValueError) as exc:
            raise ValidationFailed(f"Invalid value for {k}") from exc
        if lo is not None and not (lo <= cv <= hi):
            raise ValidationFailed(f"{k} must be between {lo} and {hi}")
        clean[k] = cv
    return clean
