# Architecture

## System overview

```
                 ┌───────────────────────── browser (server-rendered HTML, strict CSP, no inline JS)
 users ──HTTPS──▶│  reverse proxy / LB (TLS)  ──▶  web (FastAPI + Jinja2, uvicorn, N replicas, stateless)
 ERP/API ──HTTPS─┘                                   │  sessions in DB · CSRF · rate limit (Redis optional)
 Stripe ──webhook──────────────────────────────────▶ │
                                                     ▼
                                   PostgreSQL 16 (row-level security per tenant, append-only audit)
                                                     ▲
                                   worker (same image; jobs via SELECT … FOR UPDATE SKIP LOCKED)
                                        └──▶ SMTP (attestation / reset / invite / alert email)
```

| Concern | Choice | Why |
|---|---|---|
| Language/runtime | Python 3.11 | Mature ecosystem for finance tooling and a large hiring pool |
| Web | FastAPI + Jinja2 server-side rendering | One codebase for UI and API; no SPA supply chain; enables a strict CSP |
| DB | PostgreSQL 16 | Row-level security, transactional job queue, JSONB, advisory locks |
| ORM/migrations | SQLAlchemy 2 + Alembic | Typed models; migrations own RLS policies, triggers and functions |
| Jobs | Postgres table queue | No broker to run; jobs commit atomically with the business transaction |
| Cache/rate limit | In-memory, or Redis when `PP_REDIS_URL` is set | Redis only needed for multi-instance rate limits |
| Billing | Stripe Checkout, Customer Portal and webhooks | PCI scope stays with Stripe |
| Email | SMTP (any provider) | Provider-neutral |
| Observability | JSON logs with request IDs, Prometheus `/metrics` (token), optional Sentry | Standard and cheap |
| Packaging | Single container image; web, worker and migrate are commands | Simple deployment |

## Code layout (`src/payeeproof`)

| Module | Responsibility |
|---|---|
| `config.py` | Settings; refuses unsafe production configuration |
| `db.py` | Engine; tenant GUCs re-applied at every transaction begin |
| `models.py` | ORM mirror of the migrated schema (drift is tested) |
| `nacha/` | Strict NACHA parser (with control-total integrity checks) and file builder (prenotes) |
| `screening/` | Pure rules engine (13 active rule codes + integrity/IAT/prenote/network signals) |
| `security/` | AES-GCM field encryption, HMAC fingerprints, argon2id, TOTP, tokens, rate limiter |
| `services/` | Domain logic: auth, vendors, change requests, screening, audit chain, evidence, orgs, API keys, jobs, email, network |
| `billing/` | Plans and limits; Stripe integration |
| `web/` | App factory and middleware, auth/CSRF dependencies, routes (app, auth, public, API v1) |
| `worker.py`, `cli.py` | Background worker and operator CLI |

## Request lifecycle
1. Middleware assigns a request ID and opens a DB session.
2. The auth dependency loads the session by token hash, enforces MFA, resolves the org membership and sets
   `app.org_id`/`app.user_id`.
3. The route calls a service. Services check permissions (`Ctx.require`) and write audit events in the same transaction.
4. Middleware **commits only if the response status is < 400** (or `force_commit` is set for failed-login bookkeeping).
   A failed commit returns 500, never a false success. It then adds security headers and records metrics.

## Key design decisions
- **Tenant isolation is enforced by the database**, not only by application `WHERE` clauses. The app connects as
  `payeeproof_app` (no superuser, no BYPASSRLS). Every tenant table has an RLS policy on `org_id = app.org_id`.
  Cross-tenant lookups that are needed before a tenant is known go through five narrow `SECURITY DEFINER`
  functions: API-key prefix, invitation token, attestation token, Stripe customer, and stale-change counts.
  The org-exists check is a sixth.
- **Known contacts are snapshotted when a change request is created.** Verification can only use contacts that existed
  before the request, which defeats the "call me at this new number" attack.
- **Account numbers are never stored in plaintext.** They are encrypted with AES-256-GCM, with ciphertext bound to
  table and tenant through associated data. Matching uses per-tenant HMAC fingerprints, and display uses the last 4 digits.
- **Audit log** is append-only through a DB trigger, even for the schema owner. It is a keyed HMAC hash chain,
  serialised per org with an advisory lock, and verifiable in the UI, API and CLI.
- **No money movement.** PayeeProof screens files but never transmits them to banks (see research/regulation).

## AI decision record (Part XV)
AI was evaluated for (a) parsing vendor change-request emails and (b) explaining findings. It was **excluded from
v1**:
- The inputs are attacker-controlled emails, so an LLM parser is a prompt-injection target placed directly in the
  control path.
- Every decision the product makes (verified or not, release or block) must be deterministic and explainable to
  auditors. The 13 rules cover the high-risk events named in bank guidance (S076, S077).
- The product's value survives the AI-commoditization test without AI (strategy/moat.md).

Re-evaluation criterion: summarisation of evidence packs, which is read-only and has no decision authority. It would be
built with model-output validation, and with no raw vendor email ever entering a prompt.
