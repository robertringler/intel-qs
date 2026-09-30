# Falsification of the leading thesis

**Thesis under attack (#1):** A self-serve-to-assisted SaaS that gives lower-mid-market US businesses
(≈20–1,000 employees) payee assurance — verified vendor bank accounts, out-of-band change control,
dual approval, pre-release screening of ACH/wire batches — and produces the documented, risk-based
fraud-monitoring evidence that Nacha requires of **every** non-consumer ACH originator since
22 June 2026, can reach ≥$5M ARR within five years at ≥80% gross margin.

Method: for each question in the brief we state the strongest counter-evidence found, whether it
falsifies the thesis, and what changed in the model or product. Stress tests are reproducible
(`stress_test.py`, results in `stress_results.md`).

| # | Attack | Strongest counter-evidence | Verdict | Change made |
|---|---|---|---|---|
| 1 | Is the market large enough? | Enterprise vendors have only thousands of customers after a decade (Eftsure+Sis ID+Relish >4,000 combined, S014; Trustpair ~400, S012). | **Partially valid.** Market for this product is *not* all 607k firms (S057). Model uses 120k–275k reachable, 0.2–2% Y5 penetration. | Reach and penetration kept conservative. Expansion options (bank channel #2, TPSP API #100) excluded from base EV. |
| 2 | Will customers pay? | Sardine: the rule is "not a five-alarm fire" and can be met without overspending (S079). Kyriba: the rule does not prescribe a method (S059). A written policy plus manual callbacks may satisfy an ODFI. | **Valid for a compliance-only product.** | Positioning moved from "compliance" to "loss prevention with compliance evidence as a by-product". Price anchored to avoided loss: mean ~$123k per reported BEC complaint [D] and insurance sublimits of $100–250k (S049). Stress S1/S3 quantify the downside. |
| 3 | Is the pain severe? | 79% of orgs had payments-fraud attempts (95% CrI 75–82%) and 63% had BEC attempts (95% CrI 59–67%) [D from S006, Beta posterior]. Vendor impersonation hit 60% of BEC victims. Only 22% recovered ≥75% of losses (S007). | **Survives.** Caveat: AFP sample skews to larger organisations. | None. |
| 4 | Is the buyer identifiable? | Controller/CFO owns vendor master and payment release. The bank's treasury-management officer is the trigger (origination agreements, S076). | **Survives.** | GTM targets controllers via banks, insurance brokers and outsourced-accounting firms. |
| 5 | Is acquisition viable? | Mid-market CAC $4.2–6.8k (S040, secondary). The tornado shows CAC is a second-order driver ($3.4M swing vs $24.8M for ARPA). | **Survives with conditions.** | Product-led onboarding: a free file screen shows value before any sales call. |
| 6 | Can incumbents copy it? | BILL exposes vendor-bank verification status (S062). Ramp ships an AP fraud dashboard (S064). JPM sells account validation (S063). Eftsure is consolidating (S014). | **Valid for customers who pay only through one AP suite.** Not valid for firms that release ACH/wires from bank portals, several ERPs or several banks. | ICP narrowed to firms paying from ERP-generated NACHA files or bank portals. The product is rail-agnostic across banks and ERPs. P(compression) is modelled at 25–55%. |
| 7 | Can customers build it internally? | Spreadsheets and callback logs are today's substitute. | **Partially valid.** Internal builds lack account-validation data, tamper-evident evidence and file screening. | The tamper-evident audit chain and a NACHA pre-flight screen are core features. |
| 8 | Does AI commoditize it? | The core is deterministic workflow, verification and evidence, not generation. | **Survives.** An LLM does not create a verified-payee record or prove a callback happened. | AI is excluded from any decision path (see architecture). |
| 9 | Does regulation block deployment? | The product does not move money and is not a money transmitter. It handles bank account numbers, which triggers security and privacy duties (GLBA-adjacent customers, state breach laws). | **Survives** with security obligations. | Field-level encryption, SOC 2 roadmap, no fund movement. |
| 10 | Hidden liability? | Customers may treat a "verified" badge as a guarantee. Eftsure offers a $1M guarantee (S015). | **Valid risk.** | Terms and UI state "evidence of controls performed", not a guarantee. Guarantee products deferred until loss data exists. Liability insurance (E&O/cyber) is in the budget. |
| 11 | Sales cycle too long? | Mid-market finance tools: weeks to 3 months. Bank channel: 9–18 months (#2). | **Survives for direct.** Bank channel is an option, not the base plan. | Base plan relies on direct self-serve plus partners. |
| 12 | High churn? | SMB churn 3–7% per month (S041). | **Risk.** Annual contracts plus accumulated evidence history raise switching costs. | Annual billing is the default. Churn modelled at 8–25% per year. |
| 13 | Too much implementation? | ERP integrations are costly. | **Mitigated.** v1 needs no integration: CSV vendor import plus NACHA file upload. | ERP connectors moved to roadmap (NetSuite and Business Central first; >43k and >50k customers, S084/S085). |
| 14 | Platform dependency? | Account-validation APIs (EWS, GIACT/LSEG, JPM, Plaid) are third-party. | **Mitigated.** Several providers exist and prenote validation needs no vendor. | Provider interface plus a built-in prenote path. Stripe is replaceable for billing. |
| 15 | Can the moat survive feature replication? | Features copy easily. | **Partially valid.** Durable assets are the cross-customer verified-payee graph and evidence history. | Network features are designed in but will not show value until there are hundreds of customers. |
| 16 | Survive without huge funding? | Model capital requirement P50 $9.1M assumes opex grows 25%/yr regardless of traction (conservative). | **Uncertain.** A lean plan (financial/model.md) needs less. | Staged plan with a kill criterion at month 9. |
| 17 | TAM inflated by reports? | No third-party "TAM report" figures are used. Sizing is bottom-up from Census firm counts (S057). | **Survives.** | — |

## Stress-test result (from `stress_results.md`)

| Scenario | Mean NPV | P(NPV>0) |
|---|---|---|
| Base | $8.4M | 79% |
| ARPA ×0.6 | $1.6M | 49% |
| Bundling wins | $6.4M | 73% |
| Paper compliance (penetration ×0.5) | $1.4M | 49% |
| All adverse | −$2.6M | 14% |

**Conclusion.** The thesis survives each single attack but not the conjunction of low price, heavy
bundling and paper-only compliance. The two variables that decide the outcome are **ARPA** and
**Y5 penetration**: Spearman ρ of +0.57 and +0.52, and tornado swings of $24.8M and $23.7M.
Both depend on whether buyers see the product as loss prevention rather than paperwork. That is
testable within 90 days, and the roadmap's first milestone is designed to test it:
≥10 paying design partners at ≥$250/month.

## What would kill the thesis (pre-registered)
1. Fewer than 5 of 40 qualified controllers agree to a paid pilot at ≥$250/month within 90 days of launch.
2. ODFIs publicly accept a template policy as sufficient **and** insurers stop requiring documented callbacks.
3. A free, bank-network US Confirmation-of-Payee service (like EU VoP, S058) reaches mid-market banks before 2028.
