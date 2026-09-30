# Investment memorandum — PayeeProof

*Prepared 30 September 2026. Evidence tags: [F] fact, [D] dataset-derived, [E] estimate, [M] model assumption,
[I] inference, [S] speculation. Source IDs refer to `research/sources.csv`.*

## 1. Executive thesis
Build **PayeeProof**, a self-serve payee-assurance and fraud-monitoring-evidence SaaS for US companies with
20–1,000 employees that release vendor payments from bank portals. Of 100 screened opportunities and 8 modelled with
Monte Carlo, it has the highest probability-weighted value: mean NPV $8.4M, P(NPV>0) 79%, Y5 ARR P50 $9.3M [M].
It rests on a structural regulatory trigger (Nacha Phase 2, June 2026) [F] and a measured, growing loss pool [F].
The thesis is fragile to low pricing combined with paper-only compliance. That risk is pre-registered and tested within 90 days.

## 2. Problem
Attackers impersonate vendors and ask AP to change bank details. Payments then go to mule accounts. Vendor
impersonation was cited by 60% of BEC-hit organisations (S007). Only 22% of fraud victims recovered ≥75% of funds (S007).

## 3. Economic mechanism
Irreversible credit-push payments (ACH, wire) plus a mutable vendor master plus email as the change channel create
an arbitrage for fraudsters. The loss falls on the payer, and insurance covers it only if documented verification happened (S048, S049).
Software converts an unverifiable email request into a verified, dual-controlled, evidenced change, and screens each
payment against that verified state before release.

## 4. Customer
Controllers and CFOs (buyers) and AP staff (users) at US firms with 20–1,000 employees. Core universe: 607,038 firms
with 20–499 employees [F, S057]. Reachable subset that releases from bank portals or ERP files: 120k–275k [M].

## 5. Market
Bottom-up [M]: TAM ≈ $3.6B, SAM ≈ $1.2B at a $6k ARPA mode. Loss pool: BEC reported losses $3.046B in 2025, a floor [F, S001].
Mean loss per reported complaint ≈ $123k [D]. No syndicated TAM reports are used (research/market/market-sizing.md).

## 6. Market growth
B2B ACH volume grew 10% in 2025 to 8.1B payments. Same Day ACH volume grew 16.7% [F, S046]. BEC losses rose, and total
cyber-enabled losses grew 26% YoY [F, S001]. AI-enabled BEC is now reported by the FBI [F, S002]. Structural, not cyclical (research/trends).

## 7. Existing alternatives
- Enterprise payee assurance: Trustpair, Eftsure/Sis ID/Relish, PaymentWorks, Trustmi.
- AP suites: BILL, Ramp, Stampli, Tipalti.
- Bank APIs: JPM AVS, EWS.
- Status quo: email, phone and spreadsheets.
Details in research/competitors/landscape.md.

## 8. Competitive structure
The enterprise tier is consolidating: the Eftsure–Relish acquisition closed September 2026 and the group has >4,000
customers [F, S014]. AP suites bundle verification on their own rails [F, S062, S064]. The lower mid-market that releases
from bank portals has no self-serve, evidence-centric product priced for it [I].

## 9. Unsolved problem
A 1–8-person finance team cannot get vendor-change control, pre-release file screening and bank/auditor/insurer-grade
evidence without enterprise procurement. Nor can it get one control that spans several banks and ERPs.

## 10. Product solution
Encrypted vendor master; change requests requiring out-of-band verification (callback to the *previously known* number
with digit read-back, vendor attestation to the *previously known* email, prenote) and independent approval; NACHA
pre-release screening with 13 rules; release approval with dual control; hash-chained audit log; annual review and
evidence pack; Stripe billing; REST API.

## 11. Why now
- Nacha Phase 2 (22 June 2026) covers every originator [F, S004].
- Insurers condition social-engineering cover on documented verification [F, S049].
- AI lowers the cost of impersonation [F, S002].
- Account-validation data is API-accessible [F, S044, S063].
- Bank origination agreements now push obligations to clients [F, S076].

## 12. Why incumbents haven't solved it
Sales-led enterprise economics do not work at a $3–10k ACV [I]. AP suites cannot protect rails they do not run [I].
Banks sell data, not workflow. Before June 2026 no rule forced small originators to act [F]. Incumbents *are* moving
(S014), so the window is contested, not empty.

## 13. Revenue model
Tiered subscription by payment-volume band (Free/Starter $249/Growth $599/Scale $1,499 per month), annual by default.
Metered validation pass-through later (strategy/pricing.md).

## 14. Unit economics
Base [M]: ARPA $500/month, gross margin 84%, CAC $5,000, churn 1.2%/month → LTV ≈ $35k, LTV/CAC ≈ 7, payback ≈ 12 months.
Pessimistic: LTV/CAC 1.5, which is not viable. The kill gate applies.

## 15. Distribution
Free NACHA-file screen (product-led growth). Community-bank treasury officers and crime-insurance brokers hold the trigger
event. Outsourced accounting firms. Content on the rule. Channel CAC is unmeasured, so the blended benchmark $4.2–6.8k is used [E, S040].

## 16. Moat
Workflow ownership, accumulated evidence (switching cost), opt-in cross-customer account-reputation network, and
distribution partnerships. It passes the AI-commoditization test, because value is verification and evidence, not
generation. Feature copying is easy, so the moat compounds only with customer count (strategy/moat.md).

## 17. Technical feasibility
High. The MEVP is fully implemented in this repository (§26, `docs/`). NACHA parsing and screening are deterministic.
No third-party contract is required to operate, because the callback, attestation and prenote methods are built in.

## 18. Regulatory risk
Low-to-medium. PayeeProof never moves money, so it is not a money transmitter, TPSP or TPS [I]. It holds sensitive
financial data, so security obligations are high (research/regulation). It makes no "certified" or guarantee claims.

## 19. Security risk
Concentrated in the vendor bank-data store. Mitigations: AES-256-GCM field encryption, HMAC fingerprints for matching,
Postgres RLS tenant isolation, TOTP MFA, CSRF, rate limiting and a tamper-evident audit chain (architecture/security.md).

## 20. Development requirements
MEVP built (this repo). The next 12 months need ~4–5 engineers for connectors, SSO, network and SOC 2, plus 1 security/
compliance lead and founder-led sales (financial/assumptions.md).

## 21. Capital requirements
Seed $3.0M. Base case needs a Series A ≈ month 20–24. Peak cash need: base $5.7M, capital-efficient variant $4.0M,
Monte Carlo P50 $6.8M / P90 $11.4M [M]. Maximum at risk before the kill gate ≈ $1.3M.

## 22. Five-year scenarios
| | Y1 ARR | Y2 ARR | Y3 ARR | Y4 ARR | Y5 ARR | Break-even |
|---|---|---|---|---|---|---|
| Pessimistic | $0.09M | $0.25M | $0.45M | $0.68M | $0.90M | never (kill) |
| Base | $0.44M | $1.62M | $3.64M | $6.66M | $10.63M | month 53 |
| Aggressive | $0.89M | $3.67M | $9.31M | $18.86M | $32.81M | month 30 |
Monte Carlo Y5 ARR P10 $6.0M / P50 $10.5M / P90 $18.7M (financial/scenarios.md).

## 23. Sensitivity analysis
Spearman ρ with NPV: ARPA +0.57, Y5 penetration +0.52, exit multiple +0.27, reach +0.19, expansion +0.13.
Tornado swings: ARPA $24.8M, penetration $23.7M, exit multiple $10.9M. CAC and churn are second-order
(research/statistics/ev_results.md).

## 24. Falsification evidence
Strongest attacks:
- "Paper compliance suffices" (S059, S079).
- "AP suites and banks bundle it" (S062, S063, S064).
- "Enterprise players move down-market" (S014).
Single-factor stresses leave NPV positive. The conjunction of all three yields a mean NPV of −$2.6M and P(NPV>0) of 14%
(research/falsification/stress_results.md). Pre-registered kill criteria: fewer than 5 of 40 qualified controllers paying ≥$250/month
within 90 days; or ODFIs accept template policies *and* insurers drop verification conditions; or a free US
Confirmation-of-Payee network reaches mid-market banks.

## 25. Residual uncertainty
- True free-to-paid conversion and channel CAC are unmeasured.
- P(successful loss | attempt) for the ICP has insufficient evidence for inference.
- Enterprise pricing is not public.
- Primary documents were read through search summaries because of sandbox egress limits.
- No customer interviews have been conducted.

## 26. Product specification
See product/thesis.md and product/requirements.md (MEVP R1–R11 implemented), architecture/*.md and docs/*.md.
