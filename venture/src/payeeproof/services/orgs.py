"""Organisation administration: members, roles, control settings, ACH origination details."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import Membership, Organization, User
from . import audit, validation
from .context import ROLES, Ctx
from .errors import Conflict, NotFound, ValidationFailed
from .settings_defaults import effective, validate_update
from .vendors import get_org


def members(db: Session, ctx: Ctx) -> list[tuple[Membership, User]]:
    rows = db.execute(
        select(Membership, User)
        .join(User, User.id == Membership.user_id)
        .where(Membership.org_id == ctx.org_id)
        .order_by(User.email)
    ).all()
    return [(m, u) for m, u in rows]


def change_role(db: Session, ctx: Ctx, membership_id: uuid.UUID, role: str) -> Membership:
    ctx.require("members.manage")
    if role not in ROLES:
        raise ValidationFailed("Invalid role.")
    m = db.execute(
        select(Membership).where(Membership.id == membership_id, Membership.org_id == ctx.org_id)
    ).scalar_one_or_none()
    if m is None:
        raise NotFound("Member not found.")
    if role == "owner" and ctx.role != "owner":
        raise ValidationFailed("Only an owner can grant the owner role.")
    if m.role == "owner" and role != "owner":
        owners = db.execute(
            select(func.count())
            .select_from(Membership)
            .where(Membership.org_id == ctx.org_id, Membership.role == "owner")
        ).scalar_one()
        if owners <= 1:
            raise Conflict("An organisation must keep at least one owner.")
        if ctx.role != "owner":
            raise ValidationFailed("Only an owner can change another owner's role.")
    old = m.role
    m.role = role
    audit.record(
        db,
        ctx.org_id,
        ctx.actor,
        "member.role_changed",
        "membership",
        m.id,
        {"from": old, "to": role, "user_id": str(m.user_id)},
        ctx.ip,
    )
    return m


def remove_member(db: Session, ctx: Ctx, membership_id: uuid.UUID) -> None:
    ctx.require("members.manage")
    m = db.execute(
        select(Membership).where(Membership.id == membership_id, Membership.org_id == ctx.org_id)
    ).scalar_one_or_none()
    if m is None:
        raise NotFound("Member not found.")
    if m.role == "owner":
        owners = db.execute(
            select(func.count())
            .select_from(Membership)
            .where(Membership.org_id == ctx.org_id, Membership.role == "owner")
        ).scalar_one()
        if owners <= 1:
            raise Conflict("An organisation must keep at least one owner.")
        if ctx.role != "owner":
            raise ValidationFailed("Only an owner can remove an owner.")
    audit.record(
        db,
        ctx.org_id,
        ctx.actor,
        "member.removed",
        "membership",
        m.id,
        {"user_id": str(m.user_id), "role": m.role},
        ctx.ip,
    )
    db.delete(m)


def update_settings(db: Session, ctx: Ctx, values: dict[str, Any]) -> dict[str, Any]:
    ctx.require("settings.manage")
    org = get_org(db, ctx)
    clean = validate_update(values)
    before = effective(org.settings)
    merged = {**(org.settings or {}), **clean}
    org.settings = merged
    after = effective(merged)
    changed = {k: {"from": before[k], "to": after[k]} for k in after if before[k] != after[k]}
    if changed:
        audit.record(db, ctx.org_id, ctx.actor, "settings.updated", "org", ctx.org_id, {"changed": changed}, ctx.ip)
    return after


def update_nacha_settings(db: Session, ctx: Ctx, values: dict[str, str]) -> dict[str, str]:
    ctx.require("settings.manage")
    org = get_org(db, ctx)
    clean = {
        "immediate_destination": validation.routing(values.get("immediate_destination")),
        "odfi_routing": validation.routing(values.get("odfi_routing")),
        "immediate_origin": (values.get("immediate_origin") or "").strip(),
        "destination_name": validation.text(values.get("destination_name"), "Bank name", 23, required=True) or "",
        "company_name": validation.text(values.get("company_name"), "Company name", 16, required=True) or "",
        "company_id": (values.get("company_id") or "").strip(),
    }
    for k in ("immediate_origin", "company_id"):
        v = clean[k]
        if not (1 <= len(v) <= 10 and v.replace(" ", "").isalnum()):
            raise ValidationFailed(f"{k.replace('_', ' ').capitalize()} must be 1-10 letters or digits.")
    org.nacha_settings = clean
    audit.record(
        db,
        ctx.org_id,
        ctx.actor,
        "settings.nacha_updated",
        "org",
        ctx.org_id,
        {"odfi_routing": clean["odfi_routing"], "company_id": clean["company_id"]},
        ctx.ip,
    )
    return clean


def set_network_participation(db: Session, ctx: Ctx, enabled: bool) -> Organization:
    ctx.require("settings.manage")
    org = get_org(db, ctx)
    if org.network_participation != enabled:
        org.network_participation = enabled
        audit.record(
            db, ctx.org_id, ctx.actor, "settings.network_participation", "org", ctx.org_id, {"enabled": enabled}, ctx.ip
        )
    return org


def rename(db: Session, ctx: Ctx, name: str) -> Organization:
    ctx.require("settings.manage")
    org = get_org(db, ctx)
    new = validation.text(name, "Company name", 200, required=True) or org.name
    if new != org.name:
        audit.record(db, ctx.org_id, ctx.actor, "org.renamed", "org", org.id, {"from": org.name, "to": new}, ctx.ip)
        org.name = new
    return org
