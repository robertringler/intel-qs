# Competitive landscape — payee assurance / payment-fraud controls

| Player | Type | Segment | Model | Strengths | Weaknesses vs PayeeProof ICP | Source |
|---|---|---|---|---|---|---|
| Trustpair | Vendor verification SaaS | Enterprise (~400 customers) | Quote-based, usage tiers | Coupa/SAP connectors, 20+ connectors | Sales-led, enterprise pricing, EU origin | S012, S013, S065 |
| Eftsure (+Sis ID, +Relish) | Verification network + guarantee | Enterprise/upper mid-market, AU/EU/US | Quote-based, by spend & vendor volume | Network data, $1M guarantee, >4,000 customers | Pricing opaque; enterprise focus; integrating 3 acquisitions | S014, S015 |
| PaymentWorks | Vendor onboarding portal | Higher-ed, public sector, enterprise | Subscription | Indemnification, onboarding | Onboarding-centric, not batch screening | Nacha 2026 page (S060-adjacent) |
| Trustmi | Payment-process security | Enterprise | Subscription | $21M raised, behavioural | Enterprise | S061 |
| BILL / Ramp / Stampli / Tipalti | AP suites | SMB–mid-market | Subscription + payments revenue | Own the payment rail they process | Protect only payments routed through them; many firms release ACH from bank portals | S062, S064 |
| J.P. Morgan AVS / EWS Verify Account / LSEG-GIACT | Bank/data validation APIs | Banks' corporate clients | Per-inquiry | Authoritative account-ownership data | API only; no workflow or evidence; bank-specific | S044, S063 |
| Kyriba, Bottomline | Treasury/payment hubs | Enterprise | Enterprise licence | Payment hub, fraud rules | Price and implementation weight | S059 |
| Sardine, NICE Actimize, Abrigo | Bank-side fraud monitoring | ODFIs/RDFIs | Enterprise | Behavioural analytics | Sold to banks, not originators | S079 |
| Status quo | Email + phone + spreadsheet | All | Free | Zero cost | No evidence; fails under deepfake and urgency pressure | S076 |

## Why hasn't this been solved for the lower mid-market? (mandatory question)
1. **Economics were unfavourable** [I]. Enterprise vendors sell through quotes and connector integrations, which
   do not pay back at $3–10k ACV. That is why Trustpair and Eftsure sit at enterprise scale (S012, S014).
2. **Regulation changed** [F]. Until 22 June 2026 only high-volume originators faced Nacha fraud-monitoring duties
   (S004, S005). Phase 2 extended them to every non-consumer originator, whatever its size.
3. **Rail fragmentation** [I]. AP suites solve payee assurance only on their own rails (S062, S064). Firms that pay
   from ERP files and several banks fall between products.
4. **Insurance tightened** [F]. Social-engineering cover is increasingly conditioned on documented out-of-band
   verification, and sublimits are low (S048, S049). This creates a demand for *evidence*, not just controls.
5. **Validation data became API-accessible** [F]. EWS, JPM and GIACT now sell per-inquiry account validation (S044,
   S063), so a small vendor can orchestrate it without being a bank.

"Nobody thought of it" is **not** the explanation. The segment is visible to incumbents, and they are
moving toward it (the Eftsure–Relish consolidation, S014). The window is contested, which the model reflects
as a 25–55% chance of competitive compression.
