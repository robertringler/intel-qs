# WATTFLOCK — Business Model & Economic Viability Dossier
### Origination-desk thesis · refactored edition

> ## ⛔ STATUS: NOT THE PLAN — retained as the reference for a deferred adjacency
>
> **Decided 3 October 2026.** WATTFLOCK is the **curtailment opinion**
> (`WATTFLOCK_BUSINESS_MODEL_DOSSIER.md`). This document describes an
> origination desk that is **not** being built, for two reasons recorded in
> `WATTFLOCK_RECONCILIATION_AND_DECISION.md`:
>
> 1. **Its launch market is closed.** KC-1 and KC-2 below suspend the exact
>    good it sells — an energization date — across every Texas agency, at
>    every project size, including islanded behind-the-meter configurations
>    by name. The fallback this document proposes is inside the freeze.
> 2. **It is capacity-constrained** at ~110 MW per originator-year, a ceiling
>    that neither effort nor capital moves ($3.0M bought +9% of Year-5
>    revenue). The curtailment business is demand-constrained, which is a
>    problem that responds to evidence.
>
> **This file remains accurate and is worth keeping.** It is the reference
> for the adjacency, revisited only if (a) the cap count kills the curtailment
> thesis, or (b) the Texas freeze lifts with a dated eligibility path *and*
> originator throughput clears 60 MW. Do **not** run the 45–50 hour throughput
> experiment until one of those holds.

**Date:** 3 October 2026 · refactored 3 October 2026
**Posture:** adversarial. The name is not a thesis. The question is whether a new entrant with about $0–$1,000 can sell a measurable economic outcome in this market, and what that sale actually is.
**Scope:** United States, one market first. Not a pitch.

**Refactor note.** This edition preserves the source document's thesis, numbers, conclusions and recommendation unchanged. It reorganises them: repeated anchor figures are consolidated into a single source of truth (§KF), the regulatory blockers that gate each product are consolidated into §KC and §GL, and one internal inconsistency is fixed in place rather than left buried. Three factual corrections and one addition are marked **[R]** and listed in the refactor log at the end. Nothing in the analysis was softened.

**Evidence labels:** `[FACT]` primary or authoritative · `[ESTIMATE]` sourced third-party calculation · `[FORECAST]` sourced projection · `[INFERENCE]` arithmetic on sourced inputs · `[ASSUMPTION]` · `[HYPOTHESIS]` · `[VERIFY]` not read in the primary file.

---

## Contents

**Front matter** — [Decision summary](#decision-summary) · [KF: key figures](#kf--key-figures) · [KC: key constraints](#kc--key-constraints) · [GL: product gating ladder](#gl--product-gating-ladder)

**Body** — [1 Executive finding](#1-executive-finding) · [2 Problem](#2-problem) · [3 Economic mechanism](#3-economic-mechanism) · [4 Definition](#4-wattflock-definition) · [5 Customer](#5-customer) · [6 Transaction](#6-transaction) · [7 Initial wedge](#7-initial-wedge) · [8 MVP](#8-mvp) · [9 Revenue model](#9-revenue-model) · [10 Unit economics](#10-unit-economics) · [11 $0 launch strategy](#11-0-launch-strategy) · [12 Competitive landscape](#12-competitive-landscape) · [13 Moat](#13-moat) · [14 Regulatory environment](#14-regulatory-environment) · [15 Technical architecture](#15-technical-architecture) · [16 Five-year operating model](#16-five-year-operating-model) · [17 TAM/SAM/SOM](#17-tam--sam--som) · [18 Financial model](#18-financial-model) · [19 Downside / base / upside](#19-downside--base--upside) · [20 Failure analysis](#20-failure-analysis) · [21 Customer validation plan](#21-customer-validation-plan) · [22 Path to first $100,000](#22-path-to-first-100000) · [23 Strategic position](#23-strategic-position) · [24 Critical assumptions](#24-critical-assumptions) · [25 Falsification tests](#25-falsification-tests) · [Decision](#decision) · [Refactor log](#refactor-log)

---

## Decision summary

| | |
|---|---|
| **What WATTFLOCK is** | A one-ISO origination desk selling a dated, evidence-backed deliverability opinion, paid again when that opinion becomes a signed land or interconnection milestone |
| **What it is not** | A data company, a flexibility platform, a VPP, or a software product |
| **First sellable product** | A $12,000 fixed-fee site screen (T1). No licence required. See [GL](#gl--product-gating-ladder) |
| **Cash to first invoice** | Under $200 if entity formation waits until an invoice is due |
| **Five-year base case** | $5.81M revenue · 19 FTE · $0.99M EBITDA · $8–20M enterprise value |
| **Peak cash deficit, base** | ~$441k (prudent $650–750k), or $0 in strict-$0 mode at $4.5M Year-5 revenue and five unpaid years |
| **The one unknown that decides everything** | MW a single originator can close per year. Unmeasured. $7.62M of Year-5 swing |
| **Kill line** | Planning-adjusted median below **60 MW per originator-year** → do not build |
| **Cost to find out** | $0–$400 and 45–50 hours, before any company is formed |
| **Do not raise venture capital** | $3M bought ~9% more Year-5 revenue in the same model and turned the downside into a $4M hole |

**Act in this order:** run falsification tests [1 and 7](#25-falsification-tests) → publish the free artifact → sell one screen → only then consider software.

---

## KF — Key figures

Single source of truth. Cited by ID throughout rather than restated. Changing a figure here changes it everywhere it is used.

| ID | Figure | Value | Source | Label |
|---|---|---|---|---|
| **KF-1** | Powered land, primary US markets, 2026 YTD | **$584,000/MW**, +51% year over year, +35% vs five-year average | Cushman & Wakefield, *2026 Data Center Development Cost Guide* **[R1]** | `[FACT]` |
| **KF-2** | All-in greenfield development cost | ~$17.6M/MW excluding chips | Cushman & Wakefield, same guide | `[FACT]` |
| **KF-3** | Primary-market colocation | ~$204/kW/month ⇒ **$2.45M per MW-year** of revenue at risk from delay | CBRE mid-2026, via trade restatement | `[FACT]` `[VERIFY]` against the CBRE PDF |
| **KF-4** | ERCOT large-load interconnection queue | **~474 GW** seeking, ~90% data centers, against **~9.5 GW** approved to energize | ERCOT Senate presentation 29 July 2026; ERCOT August 2026 operational overview, as aggregated | `[FACT]` |
| **KF-5** | Generation **and storage** queue | 2,061 GW active · **61-month** median request-to-COD for 2025 completions · **13% completion / 75% withdrawal** on 2000–2020 requests | LBNL *Queued Up 2026* | `[FACT]`, **with the caveat below** |
| **KF-6** | PJM capacity price | $325/MW-day = **$118,625/MW-year**, third consecutive year at the cap, $16.4B auction cost, 6.8 GW short of requirement | PJM 2028/29 Base Residual Auction, 14 July 2026 | `[FACT]` |
| **KF-7** | 2026 hyperscaler capex | ~$700–800B | J.P. Morgan ~$697B; trackers $775–800B | `[ESTIMATE]` |
| **KF-8** | Brokerage residual arithmetic | 8,760 h × 0.85 load factor × 1,000 × $0.0005/kWh = **$3,723 per MW-year** at 0.50 mils | — | `[INFERENCE]` |
| **KF-9** | Delay arithmetic | 100 MW delayed 12 months ⇒ ~**$245M** of forgone revenue (KF-3 × 100) | — | `[INFERENCE]` |

> ### ⚠ Caveat attached to KF-5, applied wherever KF-5 appears
> **These are generation-and-storage queue statistics. They are not the load-queue base rate.** No comparable published completion rate exists for large-load interconnection. KF-5 establishes that *queue-based allocation produces high failure rates in general*; it does **not** establish the failure rate WATTFLOCK's customers face. Every use of KF-5 in this document is motivational, not predictive. KF-4 is the load-side figure, and it has no completion-rate denominator. **[R2 — this caveat was previously buried at §24.9, after KF-5 had already been used as problem evidence in §1 and §2.]**

---

## KC — Key constraints

The regulatory and market facts that gate products. Cited by ID throughout.

| ID | Constraint | Detail | Gates | Label |
|---|---|---|---|---|
| **KC-1** | **ERCOT ≥75 MW energization pause** | ERCOT paused energization of new large-load data centers and crypto facilities of 75 MW or greater, pursuant to Governor Abbott's **3 August 2026** directive. Still in force at ERCOT's 11 September 2026 Batch Zero update, which covers **6,608 MW** of provisionally-included load. **Two** reports are due to the Commission by **10 December 2026**, both discussed at the PUCT's 17 December open meeting: the **Batch Zero Eligibility Verification Report** (loads provisionally in Batch Zero) and the **Community Impact Review Report** (medium loads 25–75 MW and large data center/crypto facilities, built from RFIs to the interconnecting TSPs and DSPs). PUCT Docket 59220 **[R3 — corrected]** | Honest promises of near-term ERCOT energization | `[FACT]` |
| **KC-2** | **Texas statewide data center permitting freeze** | **21 September 2026:** Governor Abbott directed TCEQ to halt **all** permit issuance for data center projects until the ERCOT and TWDB audits complete, and directed that **no state agency** proceed with regulatory approvals related to data center development in the interim. The pause applies **regardless of whether the project uses ERCOT grid power, including fully islanded facilities relying on behind-the-meter generation**. TCEQ owes the Governor a compliance report by **19 October 2026**. Predecessor: **14 September 2026**, TWDB directed to compel water-use reporting from major users including data centers, with legal consequences for non-compliance, and to partner with ERCOT on the audit **[R4 — addition; the source document predates this]** | **Closes the Texas market for the product this document sells, including the fallback it proposes.** See the consequence note below | `[FACT]` |
| **KC-3** | **PUCT broker registration** | PURA §39.3555; 16 TAC §25.112. A broker may not take title to energy. REPs may not bid to an unregistered broker. Registration fee reported as $0; foreign qualification and registered agent are not `[ESTIMATE — practitioner guide; confirm on the PUCT form]` | **T3** (supply residual) | `[FACT]` |
| **KC-4** | **ISO collateral and Order 2222 dates** | PJM accepts minimum capitalization **or** posted collateral. Order 2222: region-specific registration, telemetry, 100 kW minimum aggregation; PJM energy and ancillary services not until February 2028 on the prior compliance schedule `[re-check before relying]` | **T4** (flexibility share) | `[FACT]` |
| **KC-5** | **FERC large-load show-cause** | 18 June 2026. Six jurisdictional RTOs ordered to justify or reform large-load tariffs. >50 MW on transmission >69 kV. Five reform categories including flexible large loads and co-location. Filings due ~17 August 2026 | Changes the product definition. Licenses nothing | `[FACT]` |
| **KC-6** | **FERC Order 2023 site control** | Site-control requirement pushed speculators out of generation queues | Makes landowner control the scarce input | `[FACT]` |

### The consequence of KC-1 and KC-2 together — this changes the operating conclusion

A company whose product is *"where 100 MW energizes"* cannot honestly sell ERCOT energization dates in Q4 2026. **And the fallback this document originally proposed — redefining the Texas product as "queue eligibility and behind-the-meter pathing" — is also closed**, because:

- KC-2 covers **environmental permits at any size**, not only ≥75 MW energization. Any real project needs an air permit, a water authorisation, or a local entitlement, and those are inside the freeze.
- KC-2 covers **islanded and behind-the-meter facilities explicitly**. Behind-the-meter gas does not sit outside TCEQ — a turbine needs an air permit.
- KC-2 extends to **every state agency**, so there is no adjacent approval to route around it.

**The honest Texas artifact in Q4 2026 is therefore a map of who is paused, under which audit, and what would have to clear on 10 December — not a path to energization, and not a path around one.** That is a real, urgent, time-boxed product (see §11), but it is a credibility artifact and a short-dated engagement, not the business.

**Operational conclusion, changed:** the first paid screen should be sold **outside Texas** until the two 10 December reports and the TCEQ freeze have a recorded end. PJM is the obvious alternate, and it reintroduces the capacity-market complication that the ERCOT choice at §7 was specifically meant to avoid. **[R6 — the earlier refactor log claimed KC-2 only reinforced the existing conclusion. That was wrong. It invalidates the stated fallback and forces a market change.]**

---

## GL — Product gating ladder

The four transactions, what each requires, and when each is permitted. Referenced throughout instead of re-derived.

| | Product | Price | Legal gate | Competitive gate | Earliest realistic |
|---|---|---|---|---|---|
| **T1** | Fixed-fee site screen — the opinion | $12,000 standard; $2,500 single-site | **None** | Boutiques already charge $50–195k for studies (§12) | **Days 31–60** |
| **T2** | Milestone success fee | $3,500/MW on a *binding signed* milestone | None. The risk is contract definition, not licensing | — | 12–18 months |
| **T3** | Retail supply residual | ~0.50 mils ⇒ KF-8 | **KC-3** — PUCT registration | Loads >150 MW exit retail; crowded below | After registration |
| **T4** | Flexibility share | — | **KC-4** — collateral and Order 2222 dates | Voltus, CPower, Enel X hold portfolios; Emerald AI capitalised for the software share | Year 3+, **probably never** |

**Milestone definition for T2 — the whole fee depends on it.** Counts: executed land purchase or assigned option; executed large-load or co-location agreement; closed site sale. **Does not count:** an interconnection *request*; a non-binding LOI. Loose definition is listed at §24.3 as a company-voiding assumption, and it is the one failure mode entirely within the founder's control.

---

## 1. Executive finding

**WATTFLOCK should exist only as a one-market origination desk that sells a dated, evidence-backed deliverability opinion, and is paid when that opinion becomes a signed land or interconnection milestone. It should not exist as a data company, a flexibility platform, a virtual power plant, or a software product.**

**The inefficiency is real.** Located permission to consume electricity is scarce, priced (KF-1), and not traded. The load-side queue is enormous against what has been approved to energize (KF-4). FERC reopened all six jurisdictional RTO large-load rulesets on 18 June 2026 (KC-5). Queue-based allocation produces high failure rates where it has been measured, on the generation side (KF-5, with its caveat).

**The company that inefficiency supports is small.** A formula-driven five-year model of this exact business, forced to respect originator headcount, produces **Year-5 base revenue of $5.81M, 19 people, $0.99M of EBITDA, and $8–20M of enterprise value**, and cannot reach the $55M a prior strategy memo claimed inside 20,000 draws `[INFERENCE — prior model on these unit rates]`. Capital does not relieve the constraint. The binding unknown is megawatts one originator can close in a year, and it has not been measured.

**Start condition.** T1 can be sold with $0–$1,000 and no licence. T2 follows it. T3 and T4 are gated — see [GL](#gl--product-gating-ladder). Do not build T4 first.

**The timing fact that changes the launch market** is KC-1, now compounded by KC-2. Both are detailed in [KC](#kc--key-constraints); the operational consequence is stated there.

**Decision.** Spend the next 45–50 hours and ≤$400 on the originator-throughput experiment (§21 Track 1, §25 test 1) before any company is formed. If the planning-adjusted median is below 60 MW per originator-year, do not build WATTFLOCK. If it clears, build the screen, not the platform.

---

## 2. Problem

The scarce good is not a kilowatt-hour. **It is the enforceable right to take a stated number of megawatts at a stated place, from a stated date, at a stated firmness.**

Four observed facts make that right scarce now:

1. **Demand inflected after a flat decade.** US consumption was roughly flat from the mid-2000s through about 2020 and is rising, with commercial load the growth driver `[FACT — EIA, as cited in prior primary-source checks]`.
2. **Permission did not.** Generation queues hold ~2,061 GW active at a 13% historical completion rate (KF-5, **and read its caveat — load queues are separate and have no published completion rate**). The load-side figure is KF-4: ~474 GW seeking against ~9.5 GW approved to energize.
3. **The right is already priced.** KF-1, KF-2, KF-3.
4. **The rules are being rewritten.** KC-5 and KC-1.

### Problems considered and rejected as the founding problem

| Problem | Why not founding |
|---|---|
| kWh procurement | Retail brokers already clear 1–5 mils on smaller C&I. Loads above ~150 MW exit retail. Crowded, licensed, low edge |
| Demand-response aggregation | Voltus, CPower, Enel X hold the portfolios and the ISO registrations, retaining 20–50% of market revenue `[ESTIMATE — industry descriptions]`. Emerald AI raised $150M at a $1.05B valuation on 25 August 2026 to do flexibility *inside* the data center `[FACT]` |
| Hosting-capacity data subscription | LandGate, the closest pure-play, was acquired by Wood Mackenzie in June 2026 after roughly a decade; a prior estimate put revenue near $12M `[ESTIMATE — ZoomInfo, pre-acquisition]`. Data vendors cannot take transaction positions without poisoning subscribers |
| Emissions certificates, power quality, backup generation | Real markets, already owned, or capital-intensive. Fail the $0 test |
| Generation interconnection advisory | Same skills, wrong customer. Generation developers already staff this. The open seat is the **load** side at firms too small to staff it |

The problem that survives all six filters — value, urgency, willingness to pay, persistence, entrant access, ~$0 start — is **deliverability uncertainty for a mid-market load that has a compute or offtake commitment and no energized site.**

**Measurable loss, as arithmetic not rhetoric:** KF-3 and KF-9. Even a small improvement in the probability that a chosen site energizes is worth more than a five-figure screen. **That is the willingness-to-pay argument. It is not yet a demonstrated purchase** — §25 test 2 is what would make it one.

---

## 3. Economic mechanism

Capital is long. Permission is short. KF-7 is the demand signal. The coordinating institutions — roughly 3,000 utilities, 7 RTOs, 50 commissions — allocate the scarce right by engineering study and phone call. There is no standard contract, no price screen, and no clearing venue for *"50–300 MW, this county, energized before month 30."*

**Intermediary rent appears where three conditions hold:** the right is priced, the failure rate of trying to obtain it is high, and no incumbent can hold both sides. All three hold here:

| Condition | Evidence |
|---|---|
| The right is priced | KF-1 |
| Trying to obtain it fails often | KF-4 (474 GW seeking vs 9.5 GW approved); KF-5 by analogy, with caveat |
| No incumbent holds both sides | Data platforms cannot take a success fee without destroying subscriptions. Developers originate only for themselves. Speculators were pushed out of generation queues by KC-6. Utilities cannot sell across territories |

WATTFLOCK's mechanism is to **cut the failure rate on a small number of load-side site decisions**, and to be paid on the decision (T1) and then on the signed milestone (T2). It does not create electrons. It does not own wires. **It sells a reduction in the probability of choosing a site that will not energize.**

---

## 4. WATTFLOCK definition

> **WATTFLOCK is a one-ISO origination desk that tells a 50–300 MW load developer which parcels can actually be energized, on what date, blocked by what — and is paid a fixed fee for the opinion and a per-MW fee when a signed milestone results.**

**Not:** a grid-optimization company, an AI energy platform, a VPP, a data subscription, a broker of retail electricity (until KC-3 is satisfied), or an owner of generation.

---

## 5. Customer

| Role | Who | Why this person |
|---|---|---|
| **Customer** | Mid-market data-center developer or neocloud operator, 50–300 MW requirement | Hyperscalers staff power teams and will not pay. Sub-10 MW sites do not carry the fee |
| **User** | VP Infrastructure, development manager, or the land originator at that firm | They have to produce a site. They cannot |
| **Payer** | CEO or Chief Development Officer; pre-development budget | Site-selection spend already exists and is being spent on land brokers |
| **Beneficiary** | The developer (time), the landowner (a parcel that clears), later a supplier (a load) | Only the developer pays in the first transaction |
| **Trigger** | A GPU allocation, a tenant LOI, or an interconnection study returning an unusable date or cost | Without a trigger there is no budget release |
| **Deliverable** | A ranked shortlist: parcel, substation, MW headroom, earliest credible date, named blocking item, named utility contact, flexibility or behind-the-meter path that would move it | A memo and a spreadsheet. **Not a login** |
| **Economic outcome** | A higher probability that the site the customer options can energize inside the commitment window — measured later by whether the stated blocking item and date were right | "Optimized energy" is not an outcome. **A date that held is** |

**Explicit non-customers for the first two years:** hyperscalers; residential; sub-10 MW edge; utilities as a paid customer (they are the counterparty, not the buyer); anyone who wants a national dashboard.

---

## 6. Transaction

WATTFLOCK is a **broker of a milestone**, preceded by a **fixed-fee opinion**. It is not a marketplace until it holds both a book of exclusive landowner marketing rights and a book of developer mandates — a Year-3 condition, not a launch design.

The four transactions, their prices and their gates, are consolidated in [GL](#gl--product-gating-ladder). What matters at launch:

**T1 — the opinion.** Customer pays $12,000 to screen ~40 parcels in one ISO region and receive 5 with a named blocking item and a named utility contact, in 10 business days.

**T2 — the milestone.** Customer pays $3,500 per MW when a WATTFLOCK-originated transaction reaches a binding signed milestone. The definition that counts — and the two things that explicitly do not — is in [GL](#gl--product-gating-ladder).

**T3 — supply residual.** Paid by the retail supplier, not the customer. Arithmetic at KF-8. Gated by KC-3. **Not available on day one in Texas.**

**T4 — flexibility share.** **Rejected as a launch transaction.** Incumbents retain 20–50% of demand-response market revenue `[ESTIMATE]`. PJM capacity is worth KF-6, but the load owner holds the curtailment risk and the leverage, and Emerald AI is already capitalized to take the software share. **A startup planning on 25% of PJM capacity value is planning on someone else's business.**

---

## 7. Initial wedge

**A 50–300 MW data-center or neocloud developer who has a compute or tenant commitment, is looking outside Northern Virginia, and does not have an interconnection engineer on staff.**

Tradeoffs, not a ranking table:

- **Data centers vs industrial load.** Data centers have the higher cost of delay — KF-3 is a published price, whereas a factory's cost of delay is plant-specific and slower to underwrite. Industrial load is less competed for by CBRE and JLL. **Start with data centers because the loss is priced; add industrial when a referral appears.**
- **ERCOT vs PJM.** ERCOT has the large-load queue (KF-4), retail choice, and the best public data — but also KC-1 and KC-2. PJM has the capacity price (KF-6) and the co-location docket, and no retail-choice simplicity; a founder in Ohio is already in PJM-ATSI, which cleared at the same cap. **Practical resolution, revised for KC-2: build the public artifact on ERCOT because the data is better and the freeze is the most urgent question in the market — but sell the first paid screen outside Texas.** PJM is the alternate, accepting the capacity-market complication. **Do not open both for paid delivery.**
- **Developer vs landowner as first payer.** Developers have budget and urgency. Landowners hold the asset KC-6 made scarce and often do not know it; exclusive marketing agreements cost a signature and are the supply side. **They are not the first revenue.**
- **Utility account teams.** Useful interviewees, bad customers. They do not buy origination.

**Sales accessibility is the hidden constraint.** The knowable universe is a few hundred firms — an advantage for a solo founder and a ceiling for a venture model.

---

## 8. MVP

**Minimum deliverable.** A 15-page memo and a workbook. Forty parcels scored, five recommended. For each: substation, estimated MW of headroom, earliest credible energization date, the specific blocking item, whether a flexibility commitment or behind-the-meter configuration would remove it, and the named person at the utility or transmission provider who decides. **One non-obvious claim the customer can check against a study they already have.**

**Input.** Public only, at $0: ERCOT GIS and planning reports, large-load working-group decks, EIA 860/861, FERC Form 715, utility hosting-capacity maps where published, county assessor parcels, PUC dockets.

> **ERCOT does not publish a project-level large-load list** `[FACT — ERCOT publication practice]`. Any artifact implying otherwise is false and will be caught by the first serious reader. This is a data hole to disclose, not a prompt to scrape non-public portals.

**Process.** Manual. Cross-reference hosting-capacity and queue postings against parcels. **Call the utility planner on the five finalists and write down what they actually said. That call is the product. The map is the bait.**

**Output.** The memo, plus a one-page dated record of what the utility said, so the customer can see the work.

**Verification.** The customer checks one claim against their own study or a planner they already know. If it is wrong, they do not pay for a second screen. **That is the only verification that matters at this stage** — and it is §25 test 7.

**Pricing.** $12,000 fixed for the standard screen. $2,500 for a single-site opinion, used to get a first yes. Success fee quoted at engagement but not expected inside 90 days: $3,000–$4,000/MW, exclusive for 120 days on the shortlisted parcels.

**Delivery.** Entirely manual. No software.

**Automation, later.** Ingest queue files and EIA forms into Postgres only after ~$100,000 of manual revenue. **The failure mode in this category is building the platform at the screen stage and becoming a sub-scale data company** — the comparable is in §2's rejection table.

---

## 9. Revenue model

Aligned to value, in the order they are allowed to exist. Gates are in [GL](#gl--product-gating-ladder).

| Mechanism | When | Why this one |
|---|---|---|
| **Fixed fee** | First dollar | The customer can buy an opinion before a deal exists. Aligns poorly — paid whether the date holds — but is the only mechanism that clears inside 60 days |
| **Success fee per MW** | First repeatable profit | Aligns revenue to the milestone. 1% of KF-1 is $5,840; the model uses $3,500 because a new entrant's sites will not be primary-market prints `[ASSUMPTION]` |
| **Retainer** | After three screens for one buyer | $8,000–$15,000/month for a development program. Converts a project fee into a relationship |
| **Brokerage residual** | After KC-3, and only on loads that have not gone wholesale | Paid by the supplier. **Do not quote it before registration** |
| **Performance share of flexibility** | Year 3+, after KC-4 | Not a launch mechanism |
| **Subscription / data licence** | **Never as the company** | The comparable ceiling is a low-eight-figure data business that just got acquired |

**The mechanism that aligns WATTFLOCK's revenue to value created is the success fee. The mechanism that produces the first $1 is the fixed fee. Using the second to pretend to be the first is how the model gets lied to.**

---

## 10. Unit economics

Fundamental unit: **one originated megawatt that reaches a signed milestone.**

```
Lifetime revenue / MW
  = success fee
  + P(brokerage attaches) × mil rate × annuity
  + P(flexibility attaches) × $/MW-yr × annuity

Base, haircut from the strategy memo's rates:
  success fee                           $3,500
  brokerage   35% × $3,723 × ~4.5 yr    $4,000  NPV @ 15%     (rate = KF-8)
  flexibility 20% × $10,000 × ~6 yr     $8,000  NPV @ 15%
  = lifetime revenue / MW              ~$15,500
  − carrying, account, commission       ~$5,000
  = lifetime gross profit / MW         ~$10,500   (~68%)
  share of KF-1                           2.7%
```

`[INFERENCE / ASSUMPTION]`. The 2.7% take sits inside the 1–5% band of real-estate and M&A success fees `[ESTIMATE]`. **The flexibility term is the suspicious one** and should be treated as upside, not base, until a load owner concedes a share in writing — §25 test 4.

**Value required per $1 of revenue.** On the success fee alone, WATTFLOCK must be associated with ~$167 of powered-land value per $1 of fee (KF-1 ÷ $3,500). On a delay-cost basis, a $3,500 fee is 0.14% of one year of KF-3 `[INFERENCE]`. **The fee is small relative to the loss. That does not mean they will pay it to an unknown.**

Customer-level, base, **inherited from the prior model and not re-proven here:**

| Metric | Base | Label |
|---|---|---|
| Screen price | $12,000 | `[ASSUMPTION]` |
| CAC | ~$26,000 | `[INFERENCE]` — cumulative S&M ÷ new logos |
| ARPU, Year 5 | ~$90,000 | `[INFERENCE]` — distorted, because revenue is MW-driven |
| Gross margin | ~71% | `[INFERENCE]` |
| Logo churn | 30% | `[ASSUMPTION]` — no history |
| LTV / CAC | ~8× | `[INFERENCE]` — dies if churn is 45% |
| CAC payback | ~5 months | `[INFERENCE]` |

**By Year 5, ~78% of revenue is MW-driven. Customer count is the wrong dashboard.**

---

## 11. $0 launch strategy

Cash available: $0–$1,000. No ads, no employees, no software build, no ISO collateral, no broker registration required for T1.

**Day 1.** Pick ERCOT as the *map* market and one Texas or Oklahoma transmission-provider territory as the depth. Download the ERCOT GIS file, the latest large-load working-group deck, and one utility hosting-capacity or planning report. **Form nothing yet.**

**Days 1–7.** Produce one public artifact: *twenty substations with apparent headroom and no generation project on top of them, the parcel geometry next to each, and the reason a 75 MW load still might not energize — including KC-1 and KC-2.* Publish free. Cost: $0, hosted on a free static site or as a PDF. **The pause disclosure is what makes the artifact credible rather than promotional.**

**Days 8–30.** Build a 120-name list from 7x24 Exchange, Data Center World, Infocast, ERCOT TAC and large-load working-group attendance, and PUCT docket service lists. Send the artifact. **Ask for nothing in the first note except whether one claim is wrong.** In parallel, run the originator-throughput interviews (§21 Track 1). **Do not form the company** until one person asks for a screen or the experiment clears the kill line.

**Days 31–60.** Sell one single-site opinion at $2,500 or one screen at $12,000. Delivery is the founder, 10 business days, spreadsheet and memo. Entity formation only when an invoice is about to be sent: Ohio LLC filing on the order of $99 `[VERIFY — current Ohio fee]`; domain ~$12. **Total cash to first invoice stays under $200 if formation waits.**

**Days 61–90.** Deliver. Ask for the utility planner's name and for a second screen. Open exclusive marketing conversations with landowners on the two parcels the customer did not reject. **No success fee will have closed. That is normal.** A signed marketing agreement is the asset, not the cash.

**What $1,000 does not buy:** PUCT broker registration's foreign-qualification path, E&O insurance at a useful limit, or ISO collateral. **None of those are required to sell T1.**

---

## 12. Competitive landscape

### Direct — same product (power-first site opinion for large load)

| Player | What they sell | Position | Weakness against a solo desk |
|---|---|---|---|
| CBRE, JLL, Cushman & Wakefield | Site and lease brokerage; Cushman has Athena screening | National, trusted, already in the fee | Land-and-lease competence; the power date is not what they are measured on |
| GE Vernova Consulting | Power-first feasibility | Engineering brand | Priced and staffed for hyperscalers, not a $12k screen |
| Boutique site consultants (e.g. Metro Colo Advisory) | Fixed-fee studies, stated range **$50,000–$195,000** `[ESTIMATE — firm site]` | Already charge more than WATTFLOCK's screen | **Proof that willingness to pay exists — and that WATTFLOCK is underpricing a delivered study** |
| LandGate (Wood Mackenzie, acquired June 2026) | Grid and parcel intelligence, marketplace | Data incumbent, now inside a major research house | Cannot take a success fee without a role conflict; no origination book |

### Indirect — different product, same budget

| Player | Product | Why they matter |
|---|---|---|
| Emerald AI | In-data-center flexibility software. $150M Series A at $1.05B, 25 August 2026 `[FACT]` | Owns the "make the load flexible" budget at the operator. **Not origination** |
| Voltus | DER aggregation; Google BYOC up to 100 MW in PJM `[FACT — company announcement, 2026]` | Capacity packaging for hyperscalers. A partner or a wall, not a first competitor |
| CPower, Enel X | VPP / demand response. CPower reports >$1.4B returned to customers since 2015 `[ESTIMATE — company]` | 20–50% share of DR revenue is their model `[ESTIMATE]`. Switching costs are registrations and telemetry |
| Enverus (owns Pearl Street) | Interconnection analytics; 272 GW of mapped Lower-48 potential `[FACT — company, March 2026]` | Sells to every side. **Will not originate** |

**Substitutes.** The customer's own VP calling the utility account manager. A $300/hour interconnection engineer on contract. Doing nothing and taking the queue.

**Incumbent infrastructure.** Utilities and ERCOT are the gate, not the competitor. **They do not sell a comparative shortlist across landowners.** That is the opening, and it is narrow.

**Customer complaints worth using:** site brokers bring land without a power path; queue data describes generation, not load (KF-5 caveat); ERCOT will not publish a project-level large-load list (§8). **The artifact has to be honest about the last point or the first planner who reads it will dismiss it.**

---

## 13. Moat

Most candidate moats are theoretical inside five years.

| Candidate | Status |
|---|---|
| Realized-outcome notes — what the utility quoted vs what it did | Real, but only after transactions. **Not protective before Year 5.** A funded entrant can still copy the screen |
| Exclusive landowner marketing agreements | **Real and cheap to start.** KC-6 made site control load-bearing on the generation side; on the load side, control of the parcel is what a developer needs in order to file. Replication cost rises only after dozens of agreements |
| Two-sided book | Late. Does not bind at $5M of revenue |
| ISO registration and collateral | A wall, and also a cost. Not a launch moat |
| Public-data synthesis | **Not a moat.** FERC's transparency push and the LandGate acquisition both attack it |
| Brand — "their dates held" | The only reputation that matters, and it requires closed milestones, which take 12–18 months |

**Why WATTFLOCK would still exist after a better-funded company noticed it: it might not.** At Year-5 revenue of ~$6M there is no network effect, no switching cost, and no data asset a strategic buyer cannot rebuild. The structural protection is **the role conflict at data vendors, not anything WATTFLOCK owns.** A utility affiliate or a hyperscaler offering origination free to win the load compresses this to a boutique. **That scenario should be treated as likely enough to refuse venture capital, not as a tail risk.**

---

## 14. Regulatory environment

Not legal advice. Issues requiring counsel before the relevant product is sold. Constraint detail is in [KC](#kc--key-constraints); this section classifies them.

| Activity | Requirement | Class |
|---|---|---|
| Sell a site-deliverability memo for a fixed fee (T1) | No energy-broker registration, **if** the memo does not select or procure a retail electric provider | Commercially a contract and E&O question; not, on its face, brokerage `[INFERENCE from PURA §39.3555 definition]` |
| Paid advice on choosing a REP, or a fee from a REP, in Texas (T3) | **KC-3** | **Legally required** before T3 |
| ISO market participant / aggregator (T4) | **KC-4** | **Legally required** before T4. Not required for T1 |
| Order 2222 aggregation | **KC-4** | Irrelevant until T4 |
| FERC show-cause, large load | **KC-5** | Changes the product definition. Does not license WATTFLOCK |
| ERCOT ≥75 MW energization | **KC-1** | Does not ban advisory. **Does ban honest promises of near-term energization** |
| Texas environmental permitting, all data centers | **KC-2** | Same class as KC-1, broader scope |
| Securities treatment of a tradable capacity right | Counsel before any instrument is offered | Not a Year-1 issue. **Do not create the instrument** |

**Commercially prudent from the first paid invoice:** a written engagement limiting reliance, and E&O once the fee exceeds what the founder can refund. **Prudent is not the same as required.**

---

## 15. Technical architecture

**Phase 0 — now.** Spreadsheet, QGIS or a free GIS, browser, phone. One memo template. Cost $0.

**Phase 1 — after ~10 screens.** A folder convention and a single table: inquiry, utility, quoted cost, quoted date, what actually happened. **This is the realized-outcome file. It is the only data asset. Do not put it behind a login.**

**Phase 2 — after ~$100k revenue.** Scripted ingest of ERCOT GIS, EIA 860, and docket metadata into Postgres/PostGIS. Generates the first draft of a screen. **A human still makes the call and writes the date.**

**Phase 3 — after two ISOs and a retainer book.** Parcel/landowner CRM, engagement tracker, document assembly for marketing agreements. **Still not a customer-facing platform.**

**Phase 4 — only if T4 is real.** ISO telemetry and settlement. **This is a different company**, with collateral and a registration. Do not design it now.

Free and sufficient sources: ERCOT public files and board decks, EIA, FERC eLibrary, county assessors, utility hosting-capacity portals. No paid satellite, no private queue feed. ERCOT's non-publication of a project-level large-load list (§8) is a data hole to disclose.

---

## 16. Five-year operating model

**Formulas and inputs are at §18; this section reports outputs.** Figures are base-case `[HYPOTHESIS]`, conditional on ~110 MW closed per experienced originator-year by Year 5 and on the founder closing a handful of screens in Year 1. **If §25 test 1 returns a planning figure under 60, this table is void.** Scenario range is at §19.

| | Y1 Prove | Y2 Repeat | Y3 Standardize | Y4 Scale | Y5 Defend |
|---|---|---|---|---|---|
| Customers (end) | 3 | 10 | 24 | 46 | 83 |
| Screens sold | 3 | 9 | 6 | 8 | 14 |
| MW closed | 0 | 38 | 127 | 294 | 573 |
| Revenue | $34k | $0.39M | $1.08M | $2.69M | **$5.81M** |
| Gross margin | ~86% | ~65% | ~68% | ~70% | ~71% |
| EBITDA | −$4k | −$4k | $56k | $225k | **$989k** |
| FTE | 1 | 2.6 | 5 | 11 | **19** |
| Peak cumulative cash deficit | — | — | — | **~$441k** | — |
| Milestone | 1 paid screen; public artifact live | 1 retainer; first success fee | KC-3 registration if T3 is real; second originator | Engineering hire, **not before** | Residual mix ~35%; still no moat that binds |

> **The screens row is not an error.** Screens fall from 9 to 6 in Year 3 because retainers earn more per unit of delivery capacity and are served first, so retainer growth crowds out screens until analyst headcount catches up. It is an output of the delivery-capacity constraint at §18, not a typo. **[R5 — flagged; previously unexplained]**

**Year-1 revenue of $34,000 is the honest solo-founder number.** A prior strategy memo's $800,000 Year-1 figure was about 24× too high `[INFERENCE]`.

**Employees.** Founder unpaid or nearly unpaid in Years 1–4 if the business is strict-$0. First hire is an analyst, from revenue, around $150–250k cumulative. First originator is commission-heavy and produces at ~40% in year one `[ASSUMPTION]`.

---

## 17. TAM / SAM / SOM

**Do not use $2.2 trillion of electricity investment as WATTFLOCK revenue.**

| Layer | Definition | Size | Label |
|---|---|---|---|
| TAM | US retail electricity revenue | $515B (2024) | `[FACT — EIA/Statista]` — **not addressable** |
| TAM | Powered-land value on new large load | Hundreds of GW in queues × a fraction that is real × KF-1 | `[INFERENCE]` — **a stock, not a fee pool** |
| SAM | US large-load origination fees if every real site paid 1% of powered-land value | Order of $1–5B/year if ~10–20 GW/year of load actually reaches a milestone | `[INFERENCE, wide]` — speculative |
| **SOM, Year 5** | This firm | **$5.81M revenue; 573 MW closed; ~0.6% of a 100 GW paper flow, ~0.01–0.04% of a $15–60B rhetorical pool** | `[INFERENCE]` |

**Customers required for the base case: 83 logos, not thousands.** Transactions required: a few hundred screens and a few dozen milestone closings over five years. **The market-size slide is irrelevant to the decision. Originator throughput is the decision.**

---

## 18. Financial model

```
Revenue_t    = Screens_t      × price_t
             + Retainers_t    × fee_t
             + MW_closed_t    × success_fee_t
             + MW_brokered_t  × 7,446,000 kWh × mil_rate      (KF-8)
             + MW_flex_t      × flex_rate

MW_closed_t  = originator_FTE_t × productivity_t × ramp
Screens_t    = min(demand, delivery_FTE × screens_per_FTE)     ← the §16 crowd-out
FCF_t        = Revenue − COGS − OpEx − tax − ΔAR − capex − Δcollateral
Ending cash  = beginning cash + FCF
```

**COGS** is delivery labour, subcontracted engineering review (~10–20% of screen and retainer fees), residual carrying cost, and account management. **It is not a flat percentage of revenue.**

**Base inputs `[ASSUMPTION]`:** screen $12k → $16k; success fee $3.0k → $4.25k/MW; brokerage attach 35% at 0.50 mils; flexibility attach 20% at $10k/MW-year from Year 3; originator productivity 48 → 110 MW/year; logo churn 30%; DSO 48 days.

**Stress test.** These inputs were run 20,000 times across the downside-to-upside range. Year-5 revenue **P10 $2.6M, P50 $5.5M, P90 $8.8M**. Probability of Year-5 revenue ≥ $25M: **0%**. Probability of peak capital under $50k: **0%** in disciplined-hire mode `[INFERENCE — prior model; re-run when final.py is present]`.

---

## 19. Downside / base / upside

| | Downside | Base | Upside |
|---|---|---|---|
| Year-5 revenue | $179k | **$5.81M** | $27.1M |
| Year-5 EBITDA | $3k | **$989k** | $17.0M |
| Year-5 FTE | 1.1 | **19** | 34 |
| Cumulative MW | 118 | **1,033** | 2,735 |
| Capital required | ~$30k | **$441k** (prudent $650–750k) | ~$0 |
| Founder cash pay, 5 years, strict $0 | $0 | **$0** | n/a |
| What it is | A hobby that did not die | A good small firm | A services firm with a residual book; **63% EBITDA margin is not to be believed** |

**Break-even** on the Year-5 base cost structure is ~**$4.3M of revenue** (fixed opex ~$2.8M, contribution margin ~65%) `[INFERENCE]`. **Coverage of 1.35× is thin — a 26% revenue miss wipes Year-5 EBITDA.**

**Strict $0** (cash never below zero) reaches ~**$4.5M** in Year 5 and pays the founder nothing for five years `[INFERENCE]`. That is **$750k–$1.25M of forgone salary** at a $150–250k opportunity cost `[ASSUMPTION]`. **The entry price is that time, not the $99 filing fee.**

**Venture capital:** $3M bought ~9% more Year-5 revenue in the same model and made the downside a $4M hole. **Do not raise it.**

---

## 20. Failure analysis

| # | Failure mode | Assessment |
|---|---|---|
| 1 | **Customers will not buy** an opinion from an unknown | Land brokers and $50–195k consultants already occupy the budget (§12). A correct free artifact is the only counter. **Untested** — §25 test 2 |
| 2 | **They build it internally** | True for anyone past ~200 MW of program scale, once they hire one interconnection engineer. **The wedge is the firm that has not hired that person yet** |
| 3 | **Utilities will not provide the shortlist** | They do not market landowners against each other. They will answer a planner call — a substitute for one fact, not for the comparison |
| 4 | **Aggregators copy origination** | Voltus and CPower want flexible megawatts, not parcels. They copy T4, which WATTFLOCK should not be selling |
| 5 | **Software companies add a screen** | Enverus can. It will be a feature on a subscription, not a success-fee desk, for the role-conflict reason. **Good enough to cap price** |
| 6 | **Regulatory kill — now partly realised** | KC-1 and KC-2 have already removed the energization product in Texas, and KC-2 closes the eligibility-and-BTM fallback with it. **The screen survives only by changing market, not by changing framing.** Watch the 19 October TCEQ compliance report and the two 10 December filings |
| 7 | **Problem disappears** | Inference efficiency cutting data-center energy per unit of compute 10–100×, or transformer lead times normalising. Both plausible inside the decade. Electrification of other loads is the hedge, and it is slower |
| 8 | **Commodification** | Mandated machine-readable hosting capacity kills a data product. **Does not kill a signed-milestone fee** — another reason not to be a data product |
| 9 | **Downturn** | Origination fees fall. A firm with no balance sheet shrinks to the founder and survives. **That is the attractive property** |
| 10 | **Power prices collapse** | The screen is about permission, not spark spread. Lower energy prices do not remove a long queue. **They do shrink T3** |
| 11 | **Constraints disappear** | If queues clear and powered-land stops appreciating, the fee pool shrinks. **Watch KF-1 quarterly and ERCOT approved-to-energize GW (KF-4), not narratives** |
| 12 | **AI load growth slows** | The largest demand shock goes away; industrial and manufacturing load remains. **The business gets smaller; it does not change species** |

**Assumptions whose failure voids the company:** originator throughput below ~60 MW/year; fewer than two paid screens from the first fifty qualified conversations; **success-fee milestones defined so loosely that nothing ever "closes"** (the definition is at [GL](#gl--product-gating-ladder) and the risk is entirely within the founder's control).

---

## 21. Customer validation plan

**Do not ask "would you use this?"**

### Track 1 — throughput
*Decides whether the company can be larger than a consultancy.*

Fifteen originators across developer land teams, ex-originators now at funds, and utility large-load account executives. **Read the milestone definition aloud** ([GL](#gl--product-gating-ladder)). Ask for **three years** of personal closings. **Exclude team numbers.** Apply a **0.50–0.70 haircut** for no-brand. **Kill below 60 MW planning-adjusted.** Cost $0–$400. Already specified separately; **run it before formation.**

### Track 2 — the purchase test
*Decides whether T1 exists.*

After the free artifact is public, approach 30 development leads. The ask is a dated offer, not a reaction:

> *"I will screen 40 parcels in [territory] and deliver five with a named blocking item and a named planner, in 10 business days, for $12,000, payable on delivery. If the first claim I make about a substation you already know is wrong, do not pay. Will you sign that?"*

**Count signatures and paid invoices. Compliments are not data.** Failure: fewer than 2 paid engagements from 50 qualified conversations.

### Track 3 — piggyback on the same calls
Zero marginal cost. What mil rate, if any, is paid on loads above 50 MW, and at what MW it stops. What share of flexibility value a load owner would concede — **expect a low number; believe it.** What DSO they impose on a new vendor. **A median cutoff below 100 MW deletes T3 from the model. A conceded flexibility share below 8% deletes T4.**

**Sourcing — twenty names to start, all public-role, not a private list:** origination and site-acquisition leads who spoke at Data Center World, 7x24 Exchange, Infocast Transmission Summit, and the ERCOT Large Load Working Group in 2025–2026; PUCT and FERC large-load docket service-list contacts at mid-market developers; two ex-originators now at infrastructure funds. **Reach the person who signs the land option, not the marketing contact.**

**Pilot structure:** one $2,500 single-site opinion, credited against a $12,000 screen if they continue. **No free pilot. A free pilot tests politeness.**

---

## 22. Path to first $100,000

| Stage | Offer | Price | Sales | Gross margin | How acquired |
|---|---|---|---|---|---|
| **$1** | Single-site opinion, paid on delivery | $2,500 | 1 | ~90% (founder labour unpaid) | Free artifact → one inbound or one reply |
| **$1,000** | Same | $2,500 | 1 invoice collected | ~90% | Net-15, founder delivers |
| **$10,000** | One standard screen, or four single-site opinions | $12,000 | 1 | ~80% after a $1–2k engineer read if needed | Outbound to the 30-name list |
| **$50,000** | 4 screens | $12,000 | 4 | ~75% | Referrals from the first buyer and two landowners |
| **$100,000** | 6 screens + 1 retainer quarter | $12,000 × 6 + ~$28,000 | 4–5 logos | ~70% | Same buyers' second sites |

**$100,000 is about eight screens, or five screens and one retainer. It is not a hundred customers.** It is also a **Year-2 event** in the base model, not a Month-4 event. **Treating it as a quarter-one target recreates the false Year-1 number** corrected at §16.

---

## 23. Strategic position

**What WATTFLOCK is actually a company for:** getting a mid-market load to a signed site milestone that has a credible power path, in one market, and keeping the notes on what the utility did.

**Inefficiency being monetized:** a high failure rate in converting capital and land into energized load, in a market that prices the successful right at KF-1 and **does not price the attempt.**

**Why it exists today:** demand moved in three years; wires and transformers move in five to ten; the allocation mechanism is a study queue, not a market.

**Why it has not been closed:** the firms with the data cannot take the fee; the firms that take sites do it for themselves; the pause (KC-1) and the queue make the work look like consulting, **which does not attract the capital that would industrialize it.**

**What stops an incumbent from removing WATTFLOCK:** **nothing structural, after they decide to.** Data vendors are deterred by role conflict. Operators are not. The defence is to stay a fee-on-milestone practice and **not to pretend to be infrastructure.**

**Smallest transaction that proves it deserves to exist:** one $12,000 screen, delivered in 10 days, whose blocking item the customer confirms with the utility, **followed by a second screen from a referral.** A single polite invoice does not prove it. A repeated one does.

---

## 24. Critical assumptions

Ranked by the damage their failure does.

| # | Assumption | Label | Tested by |
|---|---|---|---|
| 1 | Steady-state closings per originator reach well above 60 MW/year | `[HYPOTHESIS]` — **no evidence** | §25 test 1 |
| 2 | A stranger will pay $12,000 for a deliverability memo before any date has been proven | `[HYPOTHESIS]` | §25 test 2 |
| 3 | The signed milestone can be defined tightly enough that the fee is not argued away | `[ASSUMPTION]` | [GL](#gl--product-gating-ladder) — within the founder's control |
| 4 | KC-1 and KC-2 end, **or** the launch market moves outside Texas. The eligibility-and-BTM fallback is **closed**, not an alternative | `[FACT that the fallback is closed]`; `[HYPOTHESIS]` that a non-Texas market works for a solo founder | §25 test 6 |
| 5 | KF-1 is the right anchor for a fee on secondary sites. **Likely overstates** | `[ASSUMPTION]` | §25 test 2 implicitly |
| 6 | Retail brokerage at 0.50 mils attaches to 35% of originated MW. **Likely overstates for >150 MW** | `[ASSUMPTION]` | §25 test 3 |
| 7 | Flexibility revenue is shareable at $10,000/MW-year from Year 3. **Weakest revenue assumption** | `[HYPOTHESIS]` | §25 test 4 |
| 8 | The founder will work essentially unpaid for several years, or will bring ~$450–750k of working capital | `[ASSUMPTION]` | §19 |

**Methodological caveat, not an assumption:** KF-5's generation-queue statistics are motivational only and are **not** the load-queue base rate. This is stated at [KF](#kf--key-figures) where the figure is introduced, so that it governs every use. **[R2]**

---

## 25. Falsification tests

| # | Test | Kill line | Cost |
|---|---|---|---|
| **1** | MW personally closed per originator-year — three-year, individual, haircut 0.50–0.70 | **Planning figure < 60** | $0–$400 |
| 2 | Paid screens from first 50 qualified conversations, offer in writing at $12,000 | Fewer than 2 | $0 plus delivery labour |
| 3 | Supplier mils on >50 MW, and the MW cutoff | Cutoff median < 100 MW, or rate < 0.15 mil | $0, same calls |
| 4 | Flexibility share a load owner will concede | Median < 8% | $0, same calls |
| 5 | DSO imposed on a new vendor | Median > 75 days | $0 |
| 6 | **Three dated filings:** TCEQ compliance report to the Governor, **19 Oct 2026**; ERCOT **Batch Zero Eligibility Verification Report** and **Community Impact Review Report**, both **10 Dec 2026**, PUCT open meeting 17 Dec **[R3 corrected, R4]** | Freeze extended with no dated end, or no eligibility path a third party can advise on → Texas stays closed and the launch market must be PJM | $0, read the filings |
| **7** | One non-obvious substation claim, checked by a practitioner | Wrong on the first check | The artifact itself |

**Run 1 and 7 before formation. Run 2 before any software.** If 1 fails, stop. If 2 fails and 1 holds, the business is a land-agent practice paid only on milestones, and the screen price or the buyer is wrong — **re-quote once, then stop.**

---

## Decision

**Three gates, in order. Do not pass one by assuming the next.**

| Gate | Question | Cost to answer | If it fails |
|---|---|---|---|
| **1** | Can an originator close ~100 MW/year? (§25 test 1) | $0–$400, ~45 hours | **Stop.** Below 60 MW the company cannot exceed a consultancy |
| **2** | Will a stranger pay $12,000 for the memo? (§25 tests 2, 7) | $0 plus delivery labour | Re-quote once. Then stop. The business is a land-agent practice paid only on milestones |
| **3** | Is there a market where an energization date can be sold honestly? (KC-1, KC-2, §25 test 6) | $0, read the filings | Redefine the product as queue eligibility and behind-the-meter pathing, or launch outside Texas |

**What passing all three buys:** a manual, one-market, fee-for-opinion-then-fee-for-milestone practice. $5.81M of revenue, 19 people, $8–20M of enterprise value in Year 5. No platform, no data company, no aggregator, and no venture capital.

**What it is not:** a $0 business in any economic sense. The cash outlay can be under $1,000; **the unpaid labour cannot** — $750k–$1.25M of forgone salary over five years in strict-$0 mode.

**The asymmetry that should decide this.** Gate 1 and Gate 2 together cost a few hundred dollars and a month. Forming the company costs five years of unpaid work. **Forming the company is the expensive way to run the experiment.**

---

## Refactor log

Thesis, numbers, conclusions and recommendation are unchanged. What changed:

### Structural
- **Added front matter:** Contents, Decision summary, [KF](#kf--key-figures) key figures, [KC](#kc--key-constraints) key constraints, [GL](#gl--product-gating-ladder) product gating ladder.
- **De-duplicated nine repeated anchors** into KF, cited by ID thereafter. KF-1 appeared six times, KF-5 four times, the T1–T4 gating logic was spread across §6, §9, §11 and §14, and the 60 MW kill line appeared six times. Changing a figure in KF now changes it everywhere.
- **Consolidated the regulatory blockers** into KC. §14 now classifies them rather than restating detail; §20.6 and §25.6 reference them.
- **Replaced the "Bottom line"**, which restated §1 almost entirely, with a **Decision** section that adds the three-gate sequence and the asymmetry argument instead of repeating.
- **§16 now points to §18** for formulas, since the brief's section order puts outputs three sections ahead of the formulas that produce them.
- **§19 no longer re-derives the base column** already in §16.
- **§20 and §24 converted to tables** with explicit pointers to the test that falsifies each row, so no assumption sits without a linked test.
- **§25 test IDs are now referenced from §§16, 20, 21, 24** and the Decision section.

### Corrections
- **[R1] Source corrected.** KF-1 ($584,000/MW, +51%) is **Cushman & Wakefield's 2026 Data Center Development Cost Guide** — verified, and the source document had it right. **Note for the wider repository:** `WATTFLOCK_BUSINESS_MODEL_DOSSIER.md` and `FIVE_YEAR_FINANCIAL_MODEL.md` both attribute this figure to CBRE. That attribution is wrong and should be corrected in both. The C&W guide also adds "+35% above the five-year average," now in KF-1.
- **[R2] Internal inconsistency fixed in place.** The source document used the LBNL 61-month / 13% / 75% statistics as problem evidence in §1 and §2, then disclosed at §24.9 that they are generation-and-storage figures and "not the load-queue base rate." The caveat is now attached to KF-5 where the figure is introduced, so it governs every use. §24 retains it as a methodological note rather than an assumption.
- **[R3] Characterisation corrected, then corrected again.** The first refactor claimed the 10 December filing "is the Community Impact Review Report, not an eligibility verification report." **That was backwards and deleted a filing ERCOT named.** ERCOT's 11 September 2026 Batch Zero update schedules **two** reports for 10 December: the **Batch Zero Eligibility Verification Report** (loads provisionally in Batch Zero, 6,608 MW) and the **Community Impact Review Report** (medium loads 25–75 MW and large data center/crypto facilities, from RFIs to TSPs and DSPs). Both are discussed at the PUCT's 17 December open meeting. Both are restored at KC-1 and §25 test 6. Docket 59220 stands.
- **[R5] Artifact explained.** The §16 screens row falling from 9 to 6 in Year 3 is the delivery-capacity crowd-out at §18, not a typo. Previously unexplained and readable as an error.

### Addition
- **[R4] KC-2 added, and [R6] its significance corrected.** On 21 September 2026 Governor Abbott directed TCEQ to halt **all** data center permit issuance pending the ERCOT and TWDB audits, directed that **no state agency** proceed with related approvals, and made the pause apply **regardless of grid use, including fully islanded behind-the-meter facilities**. TCEQ owes a compliance report on 19 October 2026. A 14 September 2026 TWDB directive on water-use reporting precedes it.

  **[R6] The first refactor log said this "reinforces the existing conclusion … it does not change the thesis." That was wrong.** The document's stated fallback — redefine the Texas product as queue eligibility and behind-the-meter pathing — is **inside** the freeze: environmental permits at any size, islanded facilities named explicitly, every state agency. The operating conclusion changes: the first paid screen must be sold outside Texas, PJM is the alternate, and PJM reintroduces the capacity-market complication §7 chose ERCOT to avoid. Carried into KC-2, the consequence note, §7, §14, §20.6, §24.4 and §25.6.

### Not changed
Every figure, scenario, price, kill line, rejection and recommendation. The **market** changed (Texas → outside Texas for paid delivery); the **economics** did not. The $12,000 screen, the $3,500/MW success fee, the $5.81M / 19 FTE / $8–20M Year-5 base case, the ~$441k peak deficit, the 60 MW kill line, the refusal of venture capital, and the conclusion that WATTFLOCK is not defensible as a platform, data company, or aggregator.

### Unresolved — needs a decision, not a refactor
This repository now holds **two different WATTFLOCK theses**: this origination desk, and the curtailment-risk quantification and certification business in `WATTFLOCK_BUSINESS_MODEL_DOSSIER.md` ($7.25M Year-5 base, $0 capital, demand-constrained). They are not variants of one another — different customer, different product, different gating. Reconciling them, or picking one, is a substantive decision outside the scope of a refactor. **It has since been made: see `WATTFLOCK_RECONCILIATION_AND_DECISION.md`.**
