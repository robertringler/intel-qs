# Data model

Authoritative DDL: `src/payeeproof/migrations/versions/0001_initial_schema.py`. ORM: `src/payeeproof/models.py`.
The two are kept identical by `tests/test_migrations.py`.

| Table | Tenant (RLS) | Purpose / notable columns |
|---|---|---|
| organizations | own row + memberships | plan, subscription_status, stripe ids, `settings` (control thresholds), `nacha_settings`, network_participation |
| users | global | email (unique), argon2id hash, encrypted TOTP secret, hashed recovery codes, lockout counters |
| memberships | org or own user | role ∈ owner/admin/approver/clerk/auditor |
| invitations | org | token_hash, role, expiry |
| sessions | global | token_hash, csrf_token, mfa_verified, org_id (active), expiry, revocation |
| password_resets | global | token_hash, expiry, used_at |
| api_keys | org | prefix (lookup), key_hash, scopes[], revoked_at |
| vendors | org | name, legal name, ERP ref, **known** contact name/phone/email, contact_updated_at |
| vendor_bank_accounts | org | routing, `account_enc` (AES-GCM), `account_fp` (HMAC), last4, status ∈ unverified/verified/retired/rejected |
| change_requests | org | kind (bank_account/contact), status machine, proposed account (encrypted + fp + last4), channel, known-contact snapshots, untrusted contact, risk_flags |
| verifications | org | method ∈ callback/attestation/prenote/external, outcome, performer, details (dialled vs known number, read-back match) |
| attestations | org | token_hash, sent_to (known email), expiry, response, responder |
| approvals | org | subject (change_request/screening_run), user, decision, comment; unique per user and subject |
| screening_runs | org | file sha256, totals, status ∈ clear/needs_review/blocked/released/rejected, risk, rule_counts, integrity issues, required approvals, certificate JSON and digest |
| screening_entries | org | per-entry routing, account fp, last4, amount, receiver, matched vendor and account, severity, findings |
| flagged_accounts | org | accounts rejected as suspected fraud |
| network_reputation / network_contributions | global | opt-in keyed fingerprints; verified/flagged org counts; contributor = HMAC(org) |
| audit_events | org (append-only) | seq, actor, action, subject, data, prev_hash, hash (HMAC chain) |
| control_reviews | org | annual review sign-off, settings snapshot, next due |
| jobs | global | durable queue (kind, payload, attempts, backoff, locks) |
| stripe_events | global | webhook idempotency |
| security_events | global (append-only) | login failures, lockouts, MFA events |

**Retention.** Audit events block deletion of their organisation (`ON DELETE RESTRICT`). Deleting a tenant for a legal
or contractual reason is an operator procedure (docs/operations.md), because evidence retention is the product's purpose.
