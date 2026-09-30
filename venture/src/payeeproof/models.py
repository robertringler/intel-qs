"""ORM models. The authoritative DDL (including RLS policies, triggers and
security-definer functions) lives in migrations; tests assert the ORM metadata
matches the migrated schema."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    type_annotation_map = {dict[str, Any]: JSONB, list[Any]: JSONB}


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


TS = DateTime(timezone=True)


class Organization(Base):
    __tablename__ = "organizations"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(80), unique=True)
    plan: Mapped[str] = mapped_column(String(20), default="free", server_default="free")
    plan_interval: Mapped[str | None] = mapped_column(String(10))
    subscription_status: Mapped[str | None] = mapped_column(String(30))
    stripe_customer_id: Mapped[str | None] = mapped_column(String(100), unique=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(100))
    current_period_end: Mapped[datetime | None] = mapped_column(TS)
    past_due_since: Mapped[datetime | None] = mapped_column(TS)
    settings: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, server_default="{}")
    nacha_settings: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, server_default="{}")
    network_participation: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(TS, server_default=func.now())


class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String(320), unique=True)
    full_name: Mapped[str] = mapped_column(String(200))
    password_hash: Mapped[str] = mapped_column(Text)
    totp_secret_enc: Mapped[str | None] = mapped_column(Text)
    totp_enabled: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    totp_last_step: Mapped[int | None] = mapped_column(BigInteger)
    recovery_codes: Mapped[list[Any]] = mapped_column(JSONB, default=list, server_default="[]")
    failed_logins: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    mfa_failures: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    locked_until: Mapped[datetime | None] = mapped_column(TS)
    created_at: Mapped[datetime] = mapped_column(TS, server_default=func.now())
    last_login_at: Mapped[datetime | None] = mapped_column(TS)


class Membership(Base):
    __tablename__ = "memberships"
    __table_args__ = (UniqueConstraint("org_id", "user_id", name="uq_membership_org_user"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(TS, server_default=func.now())


class Invitation(Base):
    __tablename__ = "invitations"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    email: Mapped[str] = mapped_column(String(320))
    role: Mapped[str] = mapped_column(String(20))
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    invited_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    expires_at: Mapped[datetime] = mapped_column(TS)
    accepted_at: Mapped[datetime | None] = mapped_column(TS)
    created_at: Mapped[datetime] = mapped_column(TS, server_default=func.now())


class UserSession(Base):
    __tablename__ = "sessions"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    org_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("organizations.id", ondelete="SET NULL"))
    csrf_token: Mapped[str] = mapped_column(String(64))
    mfa_verified: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(TS, server_default=func.now())
    last_seen_at: Mapped[datetime] = mapped_column(TS, server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(TS)
    revoked_at: Mapped[datetime | None] = mapped_column(TS)
    ip: Mapped[str | None] = mapped_column(String(64))
    user_agent: Mapped[str | None] = mapped_column(String(300))


class PasswordReset(Base):
    __tablename__ = "password_resets"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime] = mapped_column(TS)
    used_at: Mapped[datetime | None] = mapped_column(TS)
    created_at: Mapped[datetime] = mapped_column(TS, server_default=func.now())


class ApiKey(Base):
    __tablename__ = "api_keys"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100))
    prefix: Mapped[str] = mapped_column(String(16), unique=True)
    key_hash: Mapped[str] = mapped_column(String(64))
    scopes: Mapped[list[str]] = mapped_column(ARRAY(String(40)))
    created_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(TS, server_default=func.now())
    last_used_at: Mapped[datetime | None] = mapped_column(TS)
    revoked_at: Mapped[datetime | None] = mapped_column(TS)


class Vendor(Base):
    __tablename__ = "vendors"
    __table_args__ = (Index("ix_vendors_org_name", "org_id", "name"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(200))
    legal_name: Mapped[str | None] = mapped_column(String(200))
    external_ref: Mapped[str | None] = mapped_column(String(100))
    contact_name: Mapped[str | None] = mapped_column(String(200))
    contact_email: Mapped[str | None] = mapped_column(String(320))
    contact_phone: Mapped[str | None] = mapped_column(String(32))
    contact_updated_at: Mapped[datetime] = mapped_column(TS, server_default=func.now())
    status: Mapped[str] = mapped_column(String(20), default="active", server_default="active")
    created_at: Mapped[datetime] = mapped_column(TS, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TS, server_default=func.now())


class VendorBankAccount(Base):
    __tablename__ = "vendor_bank_accounts"
    __table_args__ = (Index("ix_vba_org_fp", "org_id", "account_fp"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    vendor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("vendors.id", ondelete="CASCADE"))
    routing_number: Mapped[str] = mapped_column(String(9))
    account_enc: Mapped[str] = mapped_column(Text)
    account_fp: Mapped[str] = mapped_column(String(64))
    account_last4: Mapped[str] = mapped_column(String(4))
    account_type: Mapped[str] = mapped_column(String(10), default="checking", server_default="checking")
    status: Mapped[str] = mapped_column(String(20))
    verified_at: Mapped[datetime | None] = mapped_column(TS)
    change_request_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(TS, server_default=func.now())
    retired_at: Mapped[datetime | None] = mapped_column(TS)


class ChangeRequest(Base):
    __tablename__ = "change_requests"
    __table_args__ = (Index("ix_cr_org_status", "org_id", "status"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    vendor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("vendors.id", ondelete="CASCADE"))
    kind: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(30))
    proposed_routing: Mapped[str | None] = mapped_column(String(9))
    proposed_account_enc: Mapped[str | None] = mapped_column(Text)
    proposed_account_fp: Mapped[str | None] = mapped_column(String(64))
    proposed_account_last4: Mapped[str | None] = mapped_column(String(4))
    proposed_account_type: Mapped[str | None] = mapped_column(String(10))
    proposed_contact: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    channel: Mapped[str] = mapped_column(String(20))
    request_notes: Mapped[str | None] = mapped_column(Text)
    untrusted_contact_in_request: Mapped[str | None] = mapped_column(String(300))
    known_phone_snapshot: Mapped[str | None] = mapped_column(String(32))
    known_email_snapshot: Mapped[str | None] = mapped_column(String(320))
    known_contact_age_days: Mapped[int | None] = mapped_column(Integer)
    risk_flags: Mapped[list[Any]] = mapped_column(JSONB, default=list, server_default="[]")
    created_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(TS, server_default=func.now())
    decided_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    decided_at: Mapped[datetime | None] = mapped_column(TS)
    decision_reason: Mapped[str | None] = mapped_column(Text)


class Verification(Base):
    __tablename__ = "verifications"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    change_request_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("change_requests.id", ondelete="CASCADE"))
    method: Mapped[str] = mapped_column(String(20))
    outcome: Mapped[str] = mapped_column(String(20))
    performed_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    details: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(TS, server_default=func.now())


class Attestation(Base):
    __tablename__ = "attestations"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    change_request_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("change_requests.id", ondelete="CASCADE"))
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    sent_to_email: Mapped[str] = mapped_column(String(320))
    expires_at: Mapped[datetime] = mapped_column(TS)
    used_at: Mapped[datetime | None] = mapped_column(TS)
    response: Mapped[str | None] = mapped_column(String(20))
    responder_name: Mapped[str | None] = mapped_column(String(200))
    responder_ip: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(TS, server_default=func.now())


class Approval(Base):
    __tablename__ = "approvals"
    __table_args__ = (UniqueConstraint("org_id", "subject_type", "subject_id", "user_id", name="uq_approval_once"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    subject_type: Mapped[str] = mapped_column(String(30))
    subject_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    decision: Mapped[str] = mapped_column(String(10))
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(TS, server_default=func.now())


class ScreeningRun(Base):
    __tablename__ = "screening_runs"
    __table_args__ = (Index("ix_runs_org_created", "org_id", "created_at"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    filename: Mapped[str] = mapped_column(String(255))
    file_sha256: Mapped[str] = mapped_column(String(64))
    source: Mapped[str] = mapped_column(String(10))
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    api_key_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(TS, server_default=func.now())
    entry_count: Mapped[int] = mapped_column(Integer)
    total_credit_cents: Mapped[int] = mapped_column(BigInteger)
    total_debit_cents: Mapped[int] = mapped_column(BigInteger)
    status: Mapped[str] = mapped_column(String(20))
    risk_level: Mapped[str] = mapped_column(String(10))
    rule_counts: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, server_default="{}")
    integrity_issues: Mapped[list[Any]] = mapped_column(JSONB, default=list, server_default="[]")
    required_approvals: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    released_at: Mapped[datetime | None] = mapped_column(TS)
    released_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    certificate_sha256: Mapped[str | None] = mapped_column(String(64))
    certificate: Mapped[dict[str, Any] | None] = mapped_column(JSONB)


class ScreeningEntry(Base):
    __tablename__ = "screening_entries"
    __table_args__ = (
        Index("ix_entries_run", "run_id", "entry_index"),
        Index("ix_entries_org_fp", "org_id", "account_fp"),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("screening_runs.id", ondelete="CASCADE"))
    entry_index: Mapped[int] = mapped_column(Integer)
    batch_number: Mapped[int] = mapped_column(Integer)
    sec_code: Mapped[str] = mapped_column(String(3))
    transaction_code: Mapped[str] = mapped_column(String(2))
    routing: Mapped[str] = mapped_column(String(9))
    account_fp: Mapped[str] = mapped_column(String(64))
    account_last4: Mapped[str] = mapped_column(String(4))
    amount_cents: Mapped[int] = mapped_column(BigInteger)
    receiver_name: Mapped[str] = mapped_column(String(64))
    individual_id: Mapped[str] = mapped_column(String(32))
    trace_number: Mapped[str] = mapped_column(String(15))
    vendor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    bank_account_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    severity: Mapped[str] = mapped_column(String(10))
    findings: Mapped[list[Any]] = mapped_column(JSONB, default=list, server_default="[]")


class FlaggedAccount(Base):
    __tablename__ = "flagged_accounts"
    __table_args__ = (Index("ix_flagged_org_fp", "org_id", "account_fp"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    account_fp: Mapped[str] = mapped_column(String(64))
    account_last4: Mapped[str] = mapped_column(String(4))
    routing_number: Mapped[str] = mapped_column(String(9))
    reason: Mapped[str] = mapped_column(Text)
    change_request_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(TS, server_default=func.now())


class NetworkReputation(Base):
    __tablename__ = "network_reputation"
    network_fp: Mapped[str] = mapped_column(String(64), primary_key=True)
    verified_orgs: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    flagged_orgs: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    first_seen: Mapped[datetime] = mapped_column(TS, server_default=func.now())
    last_updated: Mapped[datetime] = mapped_column(TS, server_default=func.now())


class NetworkContribution(Base):
    __tablename__ = "network_contributions"
    network_fp: Mapped[str] = mapped_column(String(64), primary_key=True)
    org_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    kind: Mapped[str] = mapped_column(String(10), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(TS, server_default=func.now())


class AuditEvent(Base):
    __tablename__ = "audit_events"
    __table_args__ = (UniqueConstraint("org_id", "seq", name="uq_audit_org_seq"),)
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="RESTRICT"))
    seq: Mapped[int] = mapped_column(BigInteger)
    occurred_at: Mapped[datetime] = mapped_column(TS)
    actor_type: Mapped[str] = mapped_column(String(10))
    actor_id: Mapped[str | None] = mapped_column(String(64))
    actor_label: Mapped[str | None] = mapped_column(String(320))
    action: Mapped[str] = mapped_column(String(60))
    subject_type: Mapped[str | None] = mapped_column(String(40))
    subject_id: Mapped[str | None] = mapped_column(String(64))
    ip: Mapped[str | None] = mapped_column(String(64))
    data: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, server_default="{}")
    prev_hash: Mapped[str] = mapped_column(String(64))
    hash: Mapped[str] = mapped_column(String(64))


class ControlReview(Base):
    __tablename__ = "control_reviews"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    reviewed_at: Mapped[datetime] = mapped_column(TS, server_default=func.now())
    notes: Mapped[str] = mapped_column(Text)
    settings_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB)
    next_due_at: Mapped[datetime] = mapped_column(TS)


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (Index("ix_jobs_status_run_at", "status", "run_at"),)
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    kind: Mapped[str] = mapped_column(String(40))
    org_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, server_default="{}")
    status: Mapped[str] = mapped_column(String(10), default="queued", server_default="queued")
    attempts: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    max_attempts: Mapped[int] = mapped_column(Integer, default=5, server_default="5")
    run_at: Mapped[datetime] = mapped_column(TS, server_default=func.now())
    locked_at: Mapped[datetime | None] = mapped_column(TS)
    locked_by: Mapped[str | None] = mapped_column(String(100))
    last_error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(TS, server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(TS)


class StripeEvent(Base):
    __tablename__ = "stripe_events"
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    type: Mapped[str] = mapped_column(String(100))
    received_at: Mapped[datetime] = mapped_column(TS, server_default=func.now())
    processed_at: Mapped[datetime | None] = mapped_column(TS)


class SecurityEvent(Base):
    __tablename__ = "security_events"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    occurred_at: Mapped[datetime] = mapped_column(TS, server_default=func.now())
    event: Mapped[str] = mapped_column(String(60))
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    ip: Mapped[str | None] = mapped_column(String(64))
    detail: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, server_default="{}")


TENANT_TABLES = [
    "memberships",
    "invitations",
    "api_keys",
    "vendors",
    "vendor_bank_accounts",
    "change_requests",
    "verifications",
    "attestations",
    "approvals",
    "screening_runs",
    "screening_entries",
    "flagged_accounts",
    "audit_events",
    "control_reviews",
]
