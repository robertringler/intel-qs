# Candidate elimination report

100 candidates were screened through six sequential gates (first failure eliminates).
Candidates eliminated at a gate carry abbreviated fields; survivors are fully specified.
Machine-readable data: `candidates.csv`, `candidates.json`; definitions in `candidates.py`.

| Gate | Definition | Eliminated |
|---|---|---|
| G1 | No measurable economic loss with a traceable source or clear mechanism | 15 |
| G2 | No identifiable buyer with budget authority / recurring trigger | 8 |
| G3 | Target segment already dominated by well-funded incumbents | 47 |
| G4 | Infeasible for a seed-stage team (licensing, data access, procurement cycle) | 6 |
| G5 | Timing window closed or deferred beyond 2027 | 10 |
| G6 | Fails AI-commoditization or platform-dependency test | 8 |
| - | Survived to quantitative model | 6 |

## Survivors (sent to Monte Carlo EV model)

- **#1 Payee assurance & Nacha fraud-monitoring controls for lower mid-market ACH/wire originators** — Survives all gates -> quant model
- **#2 Community-bank white-label originator-monitoring portal** — Survives -> modelled as channel of #1 and standalone
- **#12 No Surprises Act IDR automation for independent provider groups** — Survives -> quant model
- **#26 SMB duty drawback automation (Sec 301 duties)** — Survives -> quant model
- **#48 EU CRA vulnerability reporting workflow for SMB device makers** — Survives -> quant model
- **#100 Nacha-compliant ACH file pre-flight screening API for payroll/AP platforms (TPSP channel)** — Survives -> modelled as API expansion of #1

Two eliminated candidates (#25 IEEPA refunds, #34 CPG deductions) were also modelled as controls, to test whether gate elimination hid a higher-EV option. Both scored below every survivor (see `../statistics/ev_results.md`).

## Eliminated candidates

| # | Candidate | Sector | Gate | Reason |
|---|---|---|---|---|
| 3 | Payroll-diversion (direct deposit change) fraud controls for HR/payroll | payments-fraud | G3 | Payroll platforms own the workflow; better as a module of #1 |
| 4 | Check-fraud prevention for mid-market payers (payee positive pay + vendor address change control) | payments-fraud | G3 | Bank-owned product; include address-change control inside #1 |
| 5 | SMB wire-transfer out-of-band confirmation service | payments-fraud | G2 | Not a distinct buyer/workflow; subsumed by #1 |
| 6 | Real-estate closing wire fraud protection for title/escrow | payments-fraud | G3 | CertifID dominant in segment |
| 7 | Merchant processing fee audit & repricing for SMB merchants | payments | G6 | Low retention after one-time savings; commoditized advice |
| 8 | Chargeback management for e-commerce | payments | G3 | Crowded, funded incumbents |
| 9 | AI agent payment authorization/spend controls | ai-payments | G1 | No measurable loss yet; platform-dependent |
| 10 | Treasury cash forecasting for mid-market | fintech | G1 | Loss is opportunity-cost, weakly measurable; crowded |
| 11 | Denial prevention & appeals for independent physician groups | healthcare-rcm | G3 | Heavily funded incumbents and AI startups |
| 13 | Prior authorization automation for specialty practices | healthcare-rcm | G3 | Crowded; payer API mandate favours incumbents |
| 14 | Payer contract underpayment detection for mid-size practices | healthcare-rcm | G1 | Loss estimate not sourced; HIPAA + integration burden |
| 15 | Home-care EVV claim reconciliation | healthcare | G3 | EVV vendors own the data flow |
| 16 | Dental insurance verification automation | healthcare | G3 | Crowded with funded startups |
| 17 | PBM/claims audit for self-funded employers | benefits | G4 | Claims-data access is the bottleneck; broker gatekeeping |
| 18 | Medicaid work-requirement verification for states | govtech | G4 | Govt procurement too slow for seed team |
| 19 | Hospital price transparency compliance | healthcare | G1 | Weak measurable loss |
| 20 | Clinical trial site payments reconciliation | life-sciences | G3 | Incumbents |
| 21 | Ambulance/air-ambulance OON billing recovery | healthcare | G5 | GAPB advisory policy in flux |
| 22 | Behavioral-health credentialing automation | healthcare | G3 | Medallion/Verifiable funded |
| 23 | 340B contract pharmacy reconciliation for covered entities | healthcare | G4 | Regulatory/litigation churn; incumbents |
| 24 | Veterinary practice insurance/claims | healthcare-vet | G1 | Weak loss |
| 25 | IEEPA tariff refund (CAPE) filing software for SMB importers | trade | G5 | One-time window largely consumed by Sep 2026 |
| 27 | Post-de-minimis customs entry for small e-commerce sellers | trade | G3 | Carriers/brokers own the flow; AI HTS tools free |
| 28 | AI HTS classification | trade | G6 | AI-commoditized |
| 29 | Parcel invoice audit | logistics | G3 | Mature, crowded |
| 30 | Freight broker carrier identity verification | logistics | G3 | Highway dominant |
| 31 | Detention & accessorial dispute automation for carriers | logistics | G2 | Low WTP in freight downturn |
| 32 | Cargo insurance claims automation for brokers | logistics | G1 | Weak evidence |
| 33 | Warehouse labour scheduling | logistics | G3 | Crowded |
| 34 | Retail compliance chargebacks for CPG (deductions) | cpg | G3 | Heavily funded incumbents (Glimpse, Carbon6) |
| 35 | Amazon FBA reimbursement recovery | ecommerce | G6 | Platform-dependent & crowded |
| 36 | Restaurant delivery dispute recovery | restaurants | G6 | Platform-dependent (DoorDash/Uber portals) and crowded |
| 37 | Utility bill audit for multi-site operators | energy | G3 | Mature incumbents |
| 38 | Telecom expense management | it | G3 | Mature |
| 39 | Commercial property tax appeal automation | real-estate | G4 | Jurisdiction fragmentation; relationship-driven sales |
| 40 | Residential property tax appeal (consumer) | real-estate | G3 | Ownwell |
| 41 | Subcontractor pay-app & lien waiver compliance | construction | G3 | Procore/Levelset |
| 42 | Construction COI/insurance compliance | construction | G3 | Crowded |
| 43 | Change-order leakage tracking for specialty contractors | construction | G1 | Unsourced loss |
| 44 | Equipment rental utilization for contractors | construction | G1 | Weak evidence |
| 45 | Construction draw inspection for lenders | construction | G3 | Built Technologies |
| 46 | CMMC Level 2 readiness for SMB defense suppliers | compliance | G5 | Phase 2 suspended Jul 13 2026 |
| 47 | EU AI Act high-risk conformity tooling | compliance | G5 | Deferred to Dec 2027/Aug 2028 |
| 49 | France e-invoicing PA/connector | compliance | G3 | 101 approved platforms; commoditized |
| 50 | California DROP data-broker deletion compliance | privacy | G2 | Market too small (~hundreds of buyers) |
| 51 | Multi-state privacy DSAR automation for mid-market | privacy | G3 | Crowded |
| 52 | SOC 2 automation | compliance | G3 | Saturated |
| 53 | Sales-tax nexus compliance for SMB e-commerce | tax | G3 | Crowded |
| 54 | Unclaimed property (escheat) compliance for mid-market | tax | G3 | Sovos/Keane |
| 55 | 1099/TIN matching & information-return compliance | tax | G3 | Crowded |
| 56 | Sec 174A retroactive amended-return tooling | tax | G5 | Window closed Jul 6 2026 |
| 57 | Federal grant subrecipient monitoring for pass-through entities | govtech | G5 | Federal grant contraction lowers budgets |
| 58 | Nonprofit restricted-fund accounting | nonprofit | G2 | Low WTP |
| 59 | Cannabis 280E/inventory compliance | cannabis | G5 | Rescheduling uncertainty |
| 60 | Franchise compliance/royalty audit | franchise | G1 | Weak evidence |
| 61 | Subrogation opportunity detection for mid-size carriers/TPAs | insurance | G4 | Carrier procurement 12-24 months; data access |
| 62 | Insurance agency back-office automation | insurance | G3 | Crowded |
| 63 | Crime/social-engineering insurance underwriting data | insurtech | G2 | Better as distribution channel for #1 |
| 64 | Workers' comp premium audit | insurance | G1 | Weak evidence |
| 65 | Life insurance lapse/claims locating | insurance | G2 | No budgeted buyer |
| 66 | Hiring-fraud / candidate identity verification | security | G3 | Persona/Socure entered |
| 67 | Secure code review for AI-generated code (SMB) | devsec | G6 | Commoditized by platforms |
| 68 | Passkey/phishing-resistant MFA rollout for SMB | identity | G6 | Platform-owned |
| 69 | Third-party vendor risk questionnaires (TPRM) | security | G3 | Crowded |
| 70 | Email security for SMB (BEC detection) | security | G3 | Crowded; also misses vendor-account compromise |
| 71 | Deepfake voice defense for finance callbacks | security | G1 | Loss not yet measurable separately; fold procedural defence into #1 |
| 72 | OT/ICS asset inventory for mid-size manufacturers | security | G3 | Funded incumbents |
| 73 | Observability cost control (telemetry pipelines) | devtools | G3 | Crowded |
| 74 | LLM evaluation/observability | ai-infra | G6 | Commoditized |
| 75 | AI data licensing/provenance marketplace | ai-data | G1 | Speculative |
| 76 | GPU cost allocation/FinOps for AI | ai-infra | G3 | Crowded |
| 77 | Agent identity & permissions (non-human identity) | ai-security | G3 | Funded incumbents |
| 78 | SaaS spend management | it | G3 | Crowded |
| 79 | SBOM management | devsec | G3 | Crowded (see #48 for CRA-specific angle) |
| 80 | Internal developer portals | devtools | G1 | Weak measurable loss |
| 81 | AI month-end close for mid-market | accounting | G3 | Crowded |
| 82 | Duplicate/erroneous vendor payment recovery audit | accounting | G3 | PRGX/apexanalytix; fold detection into #1 |
| 83 | Vendor onboarding (W-9/COI/bank) portal | accounting | G2 | Component of #1 rather than standalone |
| 84 | Intercompany reconciliation for multi-entity SMBs | accounting | G1 | Weak evidence |
| 85 | Expense audit for T&E fraud | accounting | G3 | Crowded |
| 86 | Payroll tax notice resolution | tax | G2 | Payroll providers absorb |
| 87 | Auto dealer warranty retail-rate uplift | auto | G3 | Armatus dominant |
| 88 | HOA/community association accounting | real-estate | G3 | Crowded |
| 89 | Childcare subsidy billing | vertical | G3 | Incumbents |
| 90 | Solar/storage interconnection application management | energy | G5 | Tax-credit phase-downs shrink developer budgets |
| 91 | EV fleet charging cost optimization | energy | G5 | EV fleet adoption slowdown |
| 92 | Agriculture input price transparency | agriculture | G3 | FBN |
| 93 | Legal intake & conflict checks for small firms | legal | G3 | Crowded |
| 94 | Contract obligation tracking for mid-market | legal | G6 | AI-commoditized |
| 95 | K-12 ESSER/federal funds compliance | education | G5 | ESSER ended |
| 96 | Senior-living occupancy/revenue management | healthcare-realestate | G1 | Weak evidence |
| 97 | Field-service quoting for trades | home-services | G3 | Crowded |
| 98 | Municipal permitting workflow | govtech | G4 | Govt procurement |
| 99 | Medicare Advantage risk-adjustment coding audits | healthcare | G3 | Large incumbents |
