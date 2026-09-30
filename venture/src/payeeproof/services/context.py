"""Request/actor context passed to services."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from .errors import Forbidden

ROLES = ("owner", "admin", "approver", "clerk", "auditor")

PERMISSIONS: dict[str, frozenset[str]] = {
    "vendors.read": frozenset(ROLES),
    "vendors.write": frozenset({"owner", "admin", "approver", "clerk"}),
    "changes.create": frozenset({"owner", "admin", "approver", "clerk"}),
    "changes.verify": frozenset({"owner", "admin", "approver", "clerk"}),
    "changes.approve": frozenset({"owner", "admin", "approver"}),
    "screenings.read": frozenset(ROLES),
    "screenings.upload": frozenset({"owner", "admin", "approver", "clerk"}),
    "screenings.release": frozenset({"owner", "admin", "approver"}),
    "settings.manage": frozenset({"owner", "admin"}),
    "members.manage": frozenset({"owner", "admin"}),
    "billing.manage": frozenset({"owner", "admin"}),
    "apikeys.manage": frozenset({"owner", "admin"}),
    "audit.read": frozenset(ROLES),
    "reviews.sign": frozenset({"owner", "admin"}),
}

# API key scopes map onto the same permissions.
SCOPES: dict[str, str] = {
    "vendors:read": "vendors.read",
    "vendors:write": "vendors.write",
    "changes:write": "changes.create",
    "screenings:read": "screenings.read",
    "screenings:write": "screenings.upload",
    "audit:read": "audit.read",
}


@dataclass(frozen=True)
class Actor:
    type: str  # user | api | system | vendor
    id: str | None
    label: str | None


@dataclass(frozen=True)
class Ctx:
    org_id: uuid.UUID
    actor: Actor
    role: str | None = None  # for users
    scopes: frozenset[str] = frozenset()  # for API keys
    ip: str | None = None

    @property
    def user_id(self) -> uuid.UUID | None:
        return uuid.UUID(self.actor.id) if self.actor.type == "user" and self.actor.id else None

    def can(self, permission: str) -> bool:
        if self.actor.type == "user":
            return self.role in PERMISSIONS.get(permission, frozenset())
        if self.actor.type == "api":
            return any(SCOPES.get(s) == permission for s in self.scopes)
        return self.actor.type == "system"

    def require(self, permission: str) -> None:
        if not self.can(permission):
            raise Forbidden("You do not have permission to perform this action.")
