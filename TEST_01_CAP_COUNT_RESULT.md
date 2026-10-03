# Test 01 — Curtailment Cap Count
## Result: INCONCLUSIVE. Not completed. The test was also mis-specified.

**Run:** 3 October 2026
**Pre-registered question:** of the large-load tariffs filed in 2026, what share carry a **hard annual curtailment-hour cap**?
**Pre-registered kill line:** **>60% capped → the curtailment thesis fails**, because the unbounded tail it monetises is bounded by rule.
**Verdict:** **inconclusive on 23% coverage, from secondary sources only. Do not treat the thesis as validated. Do not treat it as killed.**

> ### ⚠ SUPERSEDED IN PART — read `TEST_01_CORRECTION_AND_STATUS.md` first
>
> Three things in this file are wrong:
> 1. **§6 concluded "the decision to build the curtailment opinion stands." It does not.** Inconclusive means the gate is not passed. **Nothing is being built.**
> 2. **Two of the six data points are wrong.** Montana-Dakota is Rate 38 — **100 hr/yr at ≥500 kW**, a conventional industrial interruptible rate, not 200 hr at ≥10 MW. Colorado Springs' large-load schedule is **cost allocation** (10-yr contract, minimum bill, 36 months collateral); the interruptible rate is a separate >500 kW schedule.
> 3. **The SPP CHILLS claim is over-stated.** It is non-firm conditional service with a supporting-resource trigger and a term countdown — ordinary non-firm priority, not a newly discovered unbounded liability. Customers are also **barred from market demand response**, which cuts against the model's flexibility revenue stream.
>
> **And Idaho Power Schedule 20, the one primary tariff reached, specifies the annual cap, the per-event cap, the seasonal and hourly window, the notice period and the price — which is the pre-stated fatal condition for this thesis.**

---

## 1. What stopped it

The test requires primary tariff terms. **Six of the sources that hold them are blocked by this environment's egress proxy:**

| Source | Holds | Status |
|---|---|---|
| LBNL, *Electricity Rate Designs for Large Loads*, Aug 2026 technical brief | 55-tariff design element analysis | `eta-publications.lbl.gov` **blocked** |
| SEPA, DELTa database / "Stretching the Possibilities" | The 104-tariff population and the flexibility share | `sepapower.org` **blocked** |
| DSIRE Insight, same analysis | Same | `dsireinsight.com` **blocked** |
| EEI, *Large Load Projects and Tariffs* (Sept 2026) | Utility-by-utility list | `eei.org` **blocked** |
| CoBank, DELTa analysis | Database statistics | `cobank.com` **blocked** |
| Halcyon Large Load Tariff Tracker | The underlying tracker LBNL sampled | `halcyon.io` **blocked** |

**So this is a partial count assembled from secondary summaries of those sources, not a reading of tariffs.** In a normal environment with browser access the full count is genuinely a two-to-three day job. Here it cannot be finished, and I am not going to present a 23%-coverage sample as a completed test.

---

## 2. The denominator was wrong

My test said "read all 25 tariffs." That number came from a count of tariffs *proposed in 2026 to date*. The actual population is larger, and the addressable subset is much smaller.

| Universe | Count | Source |
|---|---|---|
| Tariffs and service rules tracked in DELTa, July 2026 | **104** (69 approved + 35 proposed) | SEPA/DELTa, via CoBank summary `[FACT]` |
| Sample LBNL analysed, March 2026 | **55**, from Halcyon's tracker. Thresholds 0.3–150 MW, 75% between 5–100 MW, **median 25 MW** | LBNL Aug 2026 brief, via summary `[FACT]` |
| Proposed in 2026 to date | 25; 45% at ≥50 MW | SEPA/DSIRE `[FACT]` |
| **Carry a dispatchable-flexibility option or codified curtailment pathway, Q2 2026** | **~25% — roughly 26 constructions** | SEPA/DSIRE `[FACT]` |

**Three-quarters of large-load tariffs contain no curtailment pathway at all.** The dominant design response to large loads is financial protection, not flexibility — minimum demand charges, 15-year contracts, collateral, exit fees, ramp schedules `[FACT — LBNL/Brattle, via Utility Dive]`. Dominion's GS-5, Georgia Power's 100 MW+ rules, We Energies' "very large customer" tariff and Portland General's Oregon framework are all cost-allocation instruments with no flexibility pathway found.

**This shrinks WATTFLOCK's Phase-1 market below what the dossier assumed.** The assessable universe is ~26 tariff constructions, not 104 and not 25.

---

## 3. What I could actually determine

### A — Flexibility-bearing, curtailment terms determinable (n = 6)

| # | Utility / service | Threshold | Limit | Type |
|---|---|---|---|---|
| 1 | **Colorado Springs Utilities**, Interruptible Service Rate | — | Full interruption up to **100 hr/yr**, extensible by customer agreement | **Hard cap** (soft ceiling) |
| 2 | **Montana-Dakota Utilities**, High-Density Contracted DR Rate | ≥10 MW/month | Up to **200 hr/yr** | **Hard cap** |
| 3 | **Idaho Power**, large load / high capacity | — | Remote disconnection up to **225 hr annually**, summer peaks | **Hard cap** (seasonal) |
| 4 | **Evergy Missouri**, Large Load Power Service + DR & Local Generation Rider | — | Limits on event timing, duration and **total annual event hours** — value not published in any accessible source | **Hard cap**, value unknown |
| 5 | **AEP Ohio**, Data Center Tariff | — | **10–20 events/yr** depending on notice time. **No hour limit found** | **Event cap only** |
| 6 | **SPP CHILLS** — RTO-wide, FERC-approved 5 Jun 2026, effective 1 Jul 2026, ≤7-year non-firm service | large loads | **No cap on how often or how long SPP curtails.** Transmission provider "undertakes no obligation … to plan the transmission system to have sufficient capacity." Shed first in curtailment | **Uncapped** |

### B — Flexibility-bearing, terms not determinable (n = 2)

| # | Utility / service | Threshold | Note |
|---|---|---|---|
| 7 | **Xcel Energy**, Large Peak Controlled Time of Day Service | ≥100 MW with ≥3 MW controllable | Curtail during peaks or high-price events. No cap found |
| 8 | **Pennsylvania PUC Model Large Load Tariff**, final order 12 May 2026 | ≥50 MW / 100 MW aggregate | Interruptible options tied to **PJM's Emergency Load Response Program**. No cap in published summaries. ELRP is emergency-driven with no annual hour cap by design, and historical dispatch averages 3–4 hours per event `[FACT]` — so the hour exposure is a function of event count, which is not capped |

### The ratio, stated with its weakness

```
Determinable flexibility-bearing cases          6
  hard annual hour cap                          4   (CSU, MDU, Idaho, Evergy)
  event cap only, hours unbounded               1   (AEP Ohio)
  explicitly uncapped                           1   (SPP CHILLS)

Share hard-capped = 4/6 = 67%        ← above the 60% kill line
Coverage          = 6 of ~26 = 23%
Primary filings read = 0
```

**67% is above the kill line and I am not acting on it, for a specific reason: the sample is biased in exactly the direction that would produce a false kill.** A tariff with a quotable hour number ("200 hours per year") gets cited in trade summaries *because* the number is quotable. The absence of a cap is not newsworthy and goes unreported. Every one of my six data points came from such summaries. **A sample drawn from "tariffs whose caps got written about" will over-represent caps.** The one uncapped case I found (SPP CHILLS) surfaced only because FERC approval made it news in its own right.

---

## 4. Four structural findings, which are worth more than the ratio

**4.1 The caps that exist sit above the central expectation and below the extreme — so they bound the tail and leave the decision range open.**

| | Hours/yr |
|---|---|
| ICF central expectation for flexible large loads | **~80** `[ESTIMATE]` |
| Colorado Springs cap | 100 |
| Montana-Dakota cap | 200 |
| Idaho Power cap | 225 |
| ICF extreme condition | **300–400** `[ESTIMATE]` |

A 200-hour cap removes the 400-hour catastrophe. It does not tell a load whether it will see 40 hours or 200 — and on a 100 MW site at ~$2.45M/MW-yr of revenue, that spread is roughly **$1.1M versus $5.6M a year, a 5× range** `[INFERENCE]`. **A cap is a ceiling, not a distribution.** The quantity a credit committee needs — expected hours, P90 hours, and when in the year they land — is published by none of the four capped tariffs.

**4.2 Event caps are not hour caps, and the distinction is the whole exposure.** AEP Ohio bounds frequency at 10–20 events and says nothing about duration. At 4 hours per event that is 40–80 hours; at 12 hours, 120–240. **The tariff bounds the dimension that does not determine cost and leaves open the one that does.**

**4.3 The most consequential new service is RTO-wide and explicitly uncapped.** SPP's CHILLS is not one utility's rate schedule — it is a FERC-approved transmission service, live since 1 July 2026, offering up to seven years of non-firm service with **no limit on curtailment frequency or duration** and an explicit disclaimer of any obligation to plan capacity for it. Loads taking it are shed first. **This post-dates the WATTFLOCK dossier and is the strongest single piece of evidence for the thesis found anywhere in this test.** It is also the clearest possible case of an unpriced, unbounded curtailment liability being created by regulation.

**4.4 The active dispute is itself evidence that caps are not yet settled.** Data center companies are *asking for* caps to bound their risk; utilities and consumer advocates are resisting on the grounds that caps shift reliability risk to households `[FACT — SEPA/DSIRE]`. **Parties do not lobby for what they already have.** An open, contested question about whether caps should exist is inconsistent with caps being standard.

---

## 5. The test was mis-specified, and saying so after seeing the data is a problem

The pre-registered question was *"are the risks capped?"* The question that actually determines whether anyone buys a curtailment assessment is *"is the residual uncertainty inside the terms large enough that a lender or board requires a distribution?"*

On the evidence, **all six determinable cases leave both the expected hours and their timing unspecified — including all four hard-capped ones.** By that reading the thesis passes 6/6.

**I am not claiming that as the result, and the reason matters.** Proposing a new test after seeing the data is precisely what pre-registration exists to prevent, and the decision memo made a point of fixing the thresholds in code so they could not be moved. Redefining the pass condition now would be the exact failure mode that document warned about. So:

- The pre-registered test stands as **inconclusive**, on coverage grounds.
- The corrected test is **recorded for the future and does not count until run on the full ~26** flexibility-bearing constructions, from primary filings.
- If the corrected test is adopted, it must be written down **before** the next tranche of tariffs is read.

**Corrected test, for the record:** of the ~26 flexibility-bearing constructions, what share publishes (a) an expected or typical annual curtailment-hour figure, and (b) any seasonal or hourly distribution of when curtailment occurs? **Kill line: >40% publish both** — because that is the condition under which the quantity WATTFLOCK sells is already a free public input.

---

## 6. What this does to the decision

**The curtailment thesis is not killed, and it is not validated.** Three things changed:

| | Direction |
|---|---|
| Addressable Phase-1 universe: ~26 flexibility-bearing constructions, not 104 or 25 | **Worse.** Tightens §19's market sizing |
| Three-quarters of large-load tariffs are cost-allocation instruments with no flexibility pathway | **Worse.** The "25 tariffs filed in 2026" framing overstated the market |
| The caps found are 100–225 hr/yr against an ~80 hr expectation and a 300–400 hr extreme | **Neutral-to-good.** Caps bound the tail, not the decision range |
| SPP CHILLS: RTO-wide, uncapped, no planning obligation, live 1 July 2026 | **Good, and material.** A formally unbounded exposure created by FERC order |
| Caps are contested rather than settled | **Good.** Parties lobby for what they lack |

**Corrected:** the gate is **not passed**, so nothing is being built. Nothing here favours the origination desk either, whose market remains closed by the Texas freeze. See `TEST_01_CORRECTION_AND_STATUS.md` for the corrected status and the primary reads that come next.

---

## 7. Next

| # | Action | Cost | Why now |
|---|---|---|---|
| **1** | **Finish this count properly** — the ~26 flexibility-bearing constructions, from primary filings via Halcyon's tracker, the LBNL brief, the EEI list and state dockets. Needs an unblocked browser | $0, 2–3 days | 23% coverage from secondary sources is not a result |
| **2** | **Run the backtest feasibility test** (dossier §26 test 2) — reconstruct curtailment hours for one ERCOT node 2008–2026 under one named construction; validate against Uri (Feb 2021) and summer 2023 | $0, ~2 weeks | **This is now the more decisive test.** If public data cannot reproduce known events within ±25%, the product cannot be built regardless of what the tariffs say |
| 3 | **Read the SPP CHILLS tariff and FERC order ER26-1323 in full** | $0, 1 day | The clearest uncapped exposure found. If a CHILLS taker will pay for a distribution, that is the first customer |
| ~~4~~ | ~~Publish the Texas freeze-status map~~ **DROPPED** | — | It was the demoted origination desk's artifact and should not have survived the demotion |
| 5 | **Do not** run the originator-throughput experiment | — | Still answering a question about a business that is not being built |

**Test 2 has overtaken test 1 in importance.** The cap count asks whether there is a market; the backtest asks whether the product can be made at all. The second is answerable to primary-source standard in this environment, and a failure there kills the thesis more cleanly than any tariff survey.

---

## Sources

| Claim | Source | Access |
|---|---|---|
| 104 tariffs tracked in DELTa, July 2026 (69 approved, 35 proposed) | SEPA/DELTa via CoBank, *The state of large load rate design* | secondary |
| ~25% include a dispatchable-flexibility option or codified curtailment pathway, Q2 2026 | SEPA, *Stretching the Possibilities* / DSIRE Insight, 1 Sept 2026 | secondary |
| 55-tariff sample; 0.3–150 MW; 75% between 5–100 MW; median 25 MW | LBNL, *Electricity Rate Designs for Large Loads*, Aug 2026 | secondary |
| 25 tariffs proposed in 2026; 45% at ≥50 MW | SEPA / DSIRE Insight | secondary |
| Montana-Dakota 200 hr/yr; ≥10 MW/month | SEPA / DSIRE Insight | secondary |
| Idaho Power 225 hr annually, summer peaks | SEPA / DSIRE Insight | secondary |
| Colorado Springs Utilities 100 hr/yr, extensible by agreement | SEPA / DSIRE Insight | secondary |
| Evergy Missouri DR & Local Generation Rider — limits on total annual event hours | SEPA / DSIRE Insight | secondary |
| AEP Ohio 10–20 events/yr by notice time | AEP Ohio data center tariff coverage; PUCO authorisation | secondary |
| SPP CHILLS: no cap on frequency or duration; no planning obligation; ≤7 years; effective 1 July 2026 | FERC order ER26-1323, 195 FERC ¶ 61,196, 5 June 2026, via Utility Dive and SPP filings | secondary, primary available |
| PJM ELRP dispatch averages 3–4 hours per event | PJM ELRP programme guidelines | secondary |
| Pennsylvania model tariff ≥50 MW / 100 MW aggregate, final order 12 May 2026 | PA PUC press release and K&L Gates summary | secondary |
| Curtailment ~80 hr/yr central, 300–400 hr extreme | ICF, via Utility Dive | secondary `[ESTIMATE]` |
| Caps contested: data centers seek them, utilities and consumer groups resist | SEPA / DSIRE Insight | secondary |
| Large-load tariffs increasingly rely on upfront payments, exit fees, ramp schedules | LBNL/Brattle via Utility Dive | secondary |
| Dominion GS-5 ≥25 MW at >75% load factor; Georgia Power >100 MW, 15-yr; We Energies very large customer tariff 24 Apr 2026; PGE Oregon >20 MW framework, order 26-154 | state commission coverage | secondary |

**Every figure above is from a secondary summary of a primary source. No tariff filing was read. Treat all of it as `[VERIFY]`.**
