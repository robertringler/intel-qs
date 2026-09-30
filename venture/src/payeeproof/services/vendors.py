"""Vendor master: creation, CSV import, contact data (the root of trust for callbacks)."""

from __future__ import annotations

import csv
import io
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..billing.plans import check_vendor_capacity
from ..models import Organization, Vendor, VendorBankAccount
from ..security.crypto import account_fingerprint, last4
from ..security.keys import cipher, fingerprint_key
from . import audit, validation
from .context import Ctx
from .errors import NotFound, ValidationFailed

MAX_IMPORT_ROWS = 5000


def get_org(db: Session, ctx: Ctx) -> Organization:
    org = db.get(Organization, ctx.org_id)
    if org is None:
        raise NotFound("Organisation not found.")
    return org


def get_vendor(db: Session, ctx: Ctx, vendor_id: uuid.UUID) -> Vendor:
    v = db.execute(select(Vendor).where(Vendor.id == vendor_id, Vendor.org_id == ctx.org_id)).scalar_one_or_none()
    if v is None:
        raise NotFound("Vendor not found.")
    return v


def create_vendor(
    db: Session,
    ctx: Ctx,
    *,
    name: str,
    legal_name: str | None = None,
    external_ref: str | None = None,
    contact_name: str | None = None,
    contact_email: str | None = None,
    contact_phone: str | None = None,
    check_capacity: bool = True,
) -> Vendor:
    ctx.require("vendors.write")
    org = get_org(db, ctx)
    if check_capacity:
        check_vendor_capacity(db, org)
    v = Vendor(
        org_id=ctx.org_id,
        name=validation.text(name, "Vendor name", 200, required=True) or "",
        legal_name=validation.text(legal_name, "Legal name", 200),
        external_ref=validation.text(external_ref, "External reference", 100),
        contact_name=validation.text(contact_name, "Contact name", 200),
        contact_email=validation.email(contact_email, required=False),
        contact_phone=validation.phone(contact_phone),
    )
    if (
        v.external_ref
        and db.execute(
            select(Vendor.id).where(Vendor.org_id == ctx.org_id, Vendor.external_ref == v.external_ref)
        ).first()
    ):
        raise ValidationFailed(f"A vendor with reference {v.external_ref!r} already exists.")
    db.add(v)
    db.flush()
    audit.record(
        db,
        ctx.org_id,
        ctx.actor,
        "vendor.created",
        "vendor",
        v.id,
        {"name": v.name, "has_phone": bool(v.contact_phone), "has_email": bool(v.contact_email)},
        ctx.ip,
    )
    return v


def add_unverified_account(
    db: Session, ctx: Ctx, vendor: Vendor, routing: str, account: str, account_type: str
) -> VendorBankAccount:
    """Register an existing (legacy) account as UNVERIFIED. Used by import only; new or changed
    accounts go through change requests."""
    r = validation.routing(routing)
    a = validation.account(account)
    t = validation.account_type(account_type)
    ba = VendorBankAccount(
        org_id=ctx.org_id,
        vendor_id=vendor.id,
        routing_number=r,
        account_enc=cipher().encrypt(a, f"vba:{ctx.org_id}"),
        account_fp=account_fingerprint(fingerprint_key(), str(ctx.org_id), r, a),
        account_last4=last4(a),
        account_type=t,
        status="unverified",
    )
    db.add(ba)
    db.flush()
    audit.record(
        db,
        ctx.org_id,
        ctx.actor,
        "bank_account.registered_unverified",
        "vendor",
        vendor.id,
        {"routing": r, "last4": ba.account_last4, "bank_account_id": str(ba.id)},
        ctx.ip,
    )
    return ba


def list_vendors(db: Session, ctx: Ctx, q: str | None = None, limit: int = 100, offset: int = 0) -> list[Vendor]:
    ctx.require("vendors.read")
    stmt = select(Vendor).where(Vendor.org_id == ctx.org_id)
    if q:
        stmt = stmt.where(Vendor.name.ilike(f"%{q.replace('%', '').replace('_', '')}%"))
    return list(db.execute(stmt.order_by(Vendor.name).limit(min(limit, 500)).offset(offset)).scalars())


def accounts_for(db: Session, ctx: Ctx, vendor_id: uuid.UUID) -> list[VendorBankAccount]:
    return list(
        db.execute(
            select(VendorBankAccount)
            .where(VendorBankAccount.org_id == ctx.org_id, VendorBankAccount.vendor_id == vendor_id)
            .order_by(VendorBankAccount.created_at.desc())
        ).scalars()
    )


@dataclass
class ImportReport:
    created: int
    accounts: int
    errors: list[str]


IMPORT_COLUMNS = [
    "name",
    "legal_name",
    "external_ref",
    "contact_name",
    "contact_email",
    "contact_phone",
    "routing_number",
    "account_number",
    "account_type",
]


def import_csv(db: Session, ctx: Ctx, data: bytes) -> ImportReport:
    """All-or-nothing import. Rows with errors abort the import and are reported."""
    ctx.require("vendors.write")
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValidationFailed("CSV must be UTF-8 encoded.") from exc
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames or "name" not in [f.strip().lower() for f in reader.fieldnames]:
        raise ValidationFailed("CSV must have a header row including 'name'. Columns: " + ", ".join(IMPORT_COLUMNS))
    rows = []
    for i, row in enumerate(reader, start=2):
        if i - 1 > MAX_IMPORT_ROWS:
            raise ValidationFailed(f"Import is limited to {MAX_IMPORT_ROWS} rows per file.")
        rows.append((i, {(k or "").strip().lower(): (v or "").strip() for k, v in row.items()}))
    org = get_org(db, ctx)
    check_vendor_capacity(db, org, adding=len(rows))
    errors: list[str] = []
    created = accounts = 0
    for line, row in rows:
        try:
            with db.begin_nested():
                v = create_vendor(
                    db,
                    ctx,
                    name=row.get("name", ""),
                    legal_name=row.get("legal_name"),
                    external_ref=row.get("external_ref"),
                    contact_name=row.get("contact_name"),
                    contact_email=row.get("contact_email"),
                    contact_phone=row.get("contact_phone"),
                    check_capacity=False,
                )
                created += 1
                if row.get("routing_number") or row.get("account_number"):
                    add_unverified_account(
                        db,
                        ctx,
                        v,
                        row.get("routing_number", ""),
                        row.get("account_number", ""),
                        row.get("account_type") or "checking",
                    )
                    accounts += 1
        except ValidationFailed as exc:
            errors.append(f"Row {line}: {exc.message}")
    if errors:
        raise ValidationFailed("Import aborted; no vendors were created. " + " | ".join(errors[:20]))
    audit.record(
        db,
        ctx.org_id,
        ctx.actor,
        "vendor.import",
        "org",
        ctx.org_id,
        {"vendors": created, "accounts": accounts},
        ctx.ip,
    )
    return ImportReport(created, accounts, errors)


def contact_age_days(v: Vendor, now: datetime | None = None) -> int:
    now = now or datetime.now(UTC)
    return max(0, (now - v.contact_updated_at).days)
