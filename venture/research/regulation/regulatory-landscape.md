# Regulatory landscape

## Nacha Operating Rules — 2026 risk-management amendments
- [F] Phase 1 (20 Mar 2026): ODFIs, plus originators, TPSPs and TPSs with >6M entries in 2023 (S005).
- [F] Phase 2 (19 Jun 2026, practical 22 Jun): **all** non-consumer originators, TPSPs and TPSs regardless of volume.
  They must establish and implement risk-based processes and procedures reasonably intended to identify ACH entries
  initiated due to fraud, including **False Pretenses** (BEC, vendor/payroll impersonation) (S004).
- [F] The "commercially reasonable" standard was replaced by "risk-based". No specific method is prescribed and
  pre-origination monitoring is not required. Processes must be documented and reviewed at least annually (S059).
- [F] Enforcement: Nacha fines financial institutions, which may pass them to originators by contract. Class 3
  violations can reach $500k per occurrence plus a directive to suspend the originator (S078).
- [F] Bank guidance to originators (Zions/Amegy) organises controls by lifecycle: onboarding (callback to a previously
  known number, prenote, secure collection with MFA), approval and release, post-release monitoring, and change
  management (MFA, out-of-band authentication, account validation, dual approval, prenote) (S076).
- High-risk events named in guidance (S059, S077): new vendor, bank-detail change, first payment, large or unusual
  amount, off-cycle run, payroll redirection, urgency.
→ These map one-to-one onto PayeeProof's control library and screening rules (product/requirements.md).

## Insurance conditions
- [F] Crime and cyber social-engineering cover is often conditioned on documented, independent verification of
  payment-instruction changes. Sublimits are commonly $100–250k (S048, S049).

## Duties PayeeProof itself takes on
- PayeeProof **does not move money**. It is not a money transmitter, TPSP or TPS, because it never transmits entries to an
  ODFI. It screens files that customers upload. [I] Product and legal design must keep it that way: no forwarding of
  files to banks in v1.
- It stores vendor bank account numbers and routing numbers, which is sensitive financial data. State breach-notification
  laws apply. Customers subject to the GLBA Safeguards Rule will impose vendor-security requirements on us [I].
  → Field-level AES-256-GCM encryption, least-privilege access, audit logging, and SOC 2 Type I then Type II on the
  roadmap (architecture/security.md).
- Consumer data is minimal: individuals appear only as sole-proprietor vendors or employees in payroll files.
  State privacy laws may apply to that data, so a data-processing addendum is part of the contract templates.
- Marketing claims: no guarantee of fraud prevention; no "Nacha certified" claim (no such certification exists [I]).
