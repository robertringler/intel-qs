# Security: threat model and mitigations

**Assets:** vendor bank account numbers; the vendor master (the root of payment trust); verification and
approval records; payment files; credentials (passwords, TOTP secrets, API keys); billing state.

**Adversaries:**
- External BEC fraudster: impersonates a vendor, controls email, may use a deepfake voice.
- Credential thief.
- Malicious or compromised insider (clerk or approver).
- Other tenants.
- Network attacker.
- Attacker with database read or write access but without application secrets.
- Supply-chain attacker.

| Threat | Mitigation (implemented) | Test |
|---|---|---|
| Vendor impersonation changes bank details | Change requests; verification only via **pre-existing** contacts (snapshot); digit read-back; dialled number must equal known number; independent approval | test_workflow: known number, read-back, SoD |
| Insider approves own fraudulent change | Requester ≠ approver; sole verifier ≠ approver (default); uploader ≠ releaser; dual approval for high-risk or large runs | test_workflow, test_screening_service |
| Fraudster supplies "call me back" number | Stored as `untrusted_contact_in_request`, shown with a warning, never used | test_web end-to-end |
| Payment file altered after ERP generation | Parser recomputes entry hash and debit/credit totals; mismatch → R017 block | test_nacha tamper tests |
| Credential stuffing / brute force | argon2id (64 MiB, t=3); per-IP rate limit; account lockout (5 failures, 15 min) persisted even on failed requests; uniform errors and timing for unknown users | test_web lockout, unknown user |
| Stolen password | Mandatory TOTP MFA (cannot be disabled in production); replay-protected steps; one-time hashed recovery codes | test_security_units, test_web |
| Session fixation / hijack | 256-bit tokens stored as SHA-256; rotated after MFA; HttpOnly, Secure, SameSite=Lax cookies; 30-min idle and 12-h absolute expiry; revocation on logout, password change or reset | test_web login/logout |
| CSRF | Per-session synchroniser token on every state-changing form; Origin check; SameSite cookies | test_web CSRF |
| XSS | Jinja2 autoescape; CSP `script-src 'self'` with no inline script or style; `object-src 'none'`; `base-uri 'none'` | browser E2E asserts zero console/CSP errors |
| Clickjacking | `frame-ancestors 'none'`, `X-Frame-Options: DENY` | test_web headers |
| SQL injection | SQLAlchemy parameter binding; the few f-string SQL statements use fixed identifiers only (CLI, migration) | bandit clean |
| Cross-tenant data access (IDOR) | Services filter by org **and** PostgreSQL RLS; foreign IDs return 404 | test_rls (8 tests), test_web cross-tenant |
| Tenant context leak via pooled connections | GUCs are transaction-local and re-applied at every `BEGIN` | test_rls leak test |
| DB write attacker forges history | Audit table is append-only (trigger); keyed HMAC chain detects edits, deletions and forged entries | test_audit |
| DB read attacker steals account numbers | AES-256-GCM with tenant-bound AAD; keys held outside the DB; key rotation CLI | test_crypto, test_admin_ops rotation |
| API key theft | Keys shown once; SHA-256 stored; prefix lookup plus constant-time compare; scopes; revocation; per-key rate limit; plan gating | test_api |
| Webhook forgery / replay | Stripe signature with 300 s tolerance; idempotent by event ID | test_billing |
| Open redirect | `next` accepts only local paths | test_web |
| Email header injection | CR/LF rejected in subject and recipient | test_worker |
| Malicious uploads | Size limit (5 MB) at middleware and handler; strict ASCII NACHA parser; UTF-8 CSV with 5,000-row cap; files never executed or stored | test_nacha fuzz (700 cases), test_web |
| CSV formula injection in exports | Cells starting with `= + - @` are prefixed with a quote | code: `_csv_safe` |
| SSRF | No feature fetches user-supplied URLs | by design |
| Prompt injection / model risk | No LLM in v1 (architecture.md, AI decision record) | n/a |
| Secrets exposure | Env/secret-manager only; `.env` ignored; logs redact tokens and API keys; Sentry scrubs request data | config validation tests |
| Supply chain | Hash-pinned lock files (`--require-hashes`, binary-only); pip-audit clean; minimal non-root image, read-only FS, no apt packages | Docker build + pip-audit |
| Attestation link abuse | 256-bit single-use token, 72 h TTL, only to known email, rate-limited, `Referrer-Policy: no-referrer` | test_workflow, test_web |
| DoS | Rate limits (login, signup, MFA, API, attestation, uploads); upload caps; 100k-entry parse cap | test_web rate limit |

## Residual risks (accepted or roadmap)
- **Compromised vendor mailbox plus attestation.** If the vendor's own mailbox is compromised, an attestation can be
  confirmed by the fraudster. The UI recommends callbacks, and the default settings accept either method. Roadmap:
  an org option to require a callback for bank changes.
- **Deepfake voice on callback.** Mitigated by calling the known number and by digit read-back, which the verifier
  must not read aloud. It is not eliminated.
- **In-memory rate limiting is per instance.** Set `PP_REDIS_URL` for multi-replica deployments.
- **No SSO/SAML yet.** SOC 2 Type I is planned for month 9. An external penetration test is required before GA.
