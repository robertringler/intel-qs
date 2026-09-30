# Product thesis — PayeeProof

**For** controllers at US companies with 20–1,000 employees that pay vendors by ACH or wire from their bank portal,
**who** must stop vendor-impersonation fraud and prove to their bank, auditor and insurer that they run risk-based
fraud monitoring (Nacha 2026),
**PayeeProof** is a payee-assurance workspace that
1. **locks the vendor master**: bank-detail changes cannot take effect until verified out-of-band and approved by a second person;
2. **screens every payment file before release** against verified payees and history;
3. **produces tamper-evident evidence** of every control performed.

**Unlike** enterprise verification networks it is self-serve and priced for 1–8-person finance teams. **Unlike** AP
suites it works whichever bank or ERP releases the payment.

| Role | Who |
|---|---|
| Buyer | Controller / CFO |
| Users | AP specialists (clerk), approvers, auditors (read-only) |
| Influencers | Bank treasury officer, crime-insurance broker, external auditor |

**Core workflow**
1. Import vendors and their current bank accounts (CSV). Accounts start as "unverified".
2. Any new or changed bank detail creates a *change request*.
3. The change is verified by one or more methods: callback to the **previously known** phone number with digit read-back;
   vendor attestation via single-use link to the **previously known** email; prenote.
4. A second person approves (segregation of duties is enforced). Only then does the account become "verified".
5. Before releasing a payment run, AP uploads the NACHA file. The screen flags unknown, unverified, recently changed,
   first-time, anomalous, duplicate and invalid entries.
6. An approver releases the run, with overrides and dual approval above a threshold. The run gets a screening certificate.
7. Everything lands in a hash-chained audit log. The annual Nacha review and evidence pack are generated from it.

**Value proposition**: fewer successful redirections of vendor payments; minutes instead of ad-hoc callbacks and email
archaeology; evidence that satisfies bank, auditor and insurer requests.

**Security model** (summary): per-tenant Postgres row-level security, field-level AES-256-GCM encryption of account
numbers, TOTP MFA, CSRF-protected sessions, scoped API keys and an append-only audit chain. See architecture/security.md.
