# Requirements

## Minimum economically viable product (MEVP) — the smallest thing someone pays ≥$250/month for
| ID | Requirement | Rationale |
|---|---|---|
| R1 | Multi-tenant orgs, users, roles (owner, admin, approver, clerk, auditor) | Segregation of duties is a named control (S076) |
| R2 | Email/password auth with argon2id, mandatory TOTP MFA, lockout, session management | Target of attackers; bank-grade expectation |
| R3 | Vendor master with contacts ("known" phone/email) and bank accounts (encrypted); CSV import | Baseline for verification |
| R4 | Change requests for new/changed accounts; nothing is "verified" without verification + independent approval | Core control (S076, S077) |
| R5 | Verification methods: callback with digit read-back to previously known number; vendor attestation link to previously known email; prenote file generation | Named bank-guidance methods (S076), no third-party contract needed |
| R6 | NACHA file parser and pre-release screening rules (unknown/unverified/recent change/first payment/amount anomaly/name mismatch/duplicate/invalid routing/rejected account/round amount/debit entries/large payment) | High-risk events (S059, S077) |
| R7 | Run release with approval, dual approval above threshold, override-with-reason, screening certificate | Approval & release control (S076) |
| R8 | Append-only hash-chained audit log with verification | Evidence |
| R9 | Annual control review and evidence pack export (JSON + printable HTML) | "Reviewed at least annually" (S059) |
| R10 | Billing (Stripe Checkout, Customer Portal, webhooks), plan limits | Revenue |
| R11 | REST API with scoped API keys (screen files, manage vendors) | ERP/TPSP integrations |

## Production product (beyond MEVP)
- ERP connectors (NetSuite, Business Central) and SFTP drop-folder screening.
- Commercial account-owner validation adapters (EWS, LSEG-GIACT, JPM AVS) once contracts exist.
- SSO (SAML/OIDC), SCIM.
- Opt-in cross-customer account reputation network.
- Partner dashboard for accounting firms and banks; white-label bank edition.
- Multi-entity orgs; positive-pay file generation; wire-instruction screening via CSV.

## Non-functional requirements
| Area | Requirement |
|---|---|
| Security | OWASP ASVS L2 target; tenant isolation by RLS; encryption at rest for account numbers; secrets from environment/secret manager only |
| Availability | 99.9% monthly target; stateless app, managed Postgres with PITR |
| Performance | Screen a 10,000-entry NACHA file in < 2 s server time (measured in tests/perf) |
| Privacy | Account numbers never logged; masked (last 4) in UI and exports |
| Auditability | Every state change emits an audit event in the same DB transaction |
| Operability | Health/readiness endpoints, JSON logs with request IDs, Prometheus metrics, optional Sentry |
