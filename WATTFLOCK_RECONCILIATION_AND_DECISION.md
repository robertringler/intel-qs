# WATTFLOCK — Reconciliation and Decision

**Date:** 3 October 2026
**Question:** the repository held two incompatible companies under one name. Which one is WATTFLOCK?
**Status:** decided. The reasoning, the sequencing, and the condition that would reverse it are below.

---

## The decision

**WATTFLOCK is the curtailment opinion: the independent quantifier and certifier of curtailment risk for flexible large loads, with parametric risk transfer as its earned second act.**

**The origination desk is not WATTFLOCK. It is a possible adjacency, entered later, only if the curtailment business's own customers pull it there.** It is not a parallel bet and not a plan.

| | Decided |
|---|---|
| **The company** | Curtailment risk quantification → certification → parametric risk transfer. `WATTFLOCK_BUSINESS_MODEL_DOSSIER.md` |
| **Demoted to adjacency** | One-ISO load origination desk. `WATTFLOCK_ORIGINATION_DESK_DOSSIER.md` — retained as the reference for that option, not as the plan |
| **First action, 3 days, $0** | ~~Count hard curtailment caps across the 25 large-load tariffs filed in 2026~~ **RUN 3 Oct 2026 — INCONCLUSIVE at 23% coverage. See `TEST_01_CAP_COUNT_RESULT.md`.** Denominator was wrong (104 tracked, ~26 flexibility-bearing, not 25) and six primary sources are egress-blocked. Thesis neither killed nor validated |
| **Next action, ~2 weeks, $0** | **The ERCOT single-node backtest** (dossier §26 test 2). It has overtaken the cap count in importance: the cap count asks whether there is a market, the backtest asks whether the product can be made at all — and it is answerable to primary-source standard here |
| **First artifact, parallel, $0** | The Texas freeze-status map: who is paused, under which audit, what must clear on 10 December |
| **Deferred indefinitely** | The originator-throughput experiment. 45–50 hours spent answering a question about a business we are not building |
| **Reverses this decision** | >60% of flexibility-bearing tariffs carry hard annual curtailment-hour caps **and** the caps sit at or below the ~80 hr central expectation → thesis degrades to ~$3.5M and the origination desk becomes live again, in PJM. **Not triggered on 3 Oct evidence:** the caps found (100/200/225 hr) sit *above* the central case and *below* the 300–400 hr extreme, so they bound the tail and leave the decision range open |

---

## 1. What the Texas freeze changed, and why it decided this

The comparison was close on economics and open on sequencing. One fact closed it.

**The freeze does not merely delay the origination desk's launch market. It closes the market for the specific good that business sells, and it closes the fallback that document proposed.**

| Instrument | Date | Scope |
|---|---|---|
| Abbott directive → ERCOT | **3 Aug 2026** | Energization of new large-load data centers and crypto ≥75 MW paused. 6,608 MW provisionally in Batch Zero now under audit `[FACT]` |
| Abbott directive → TWDB | **14 Sep 2026** | Compel water-use reporting from major users including data centers; legal consequences for non-compliance; partner with ERCOT on the audit `[FACT]` |
| Abbott directive → TCEQ | **21 Sep 2026** | Halt **all** data center permit issuance pending the ERCOT and TWDB audits. **No state agency** to proceed with related approvals. Applies **regardless of whether the project uses ERCOT grid power, including fully islanded facilities relying on behind-the-meter generation** `[FACT]` |
| TCEQ compliance report → Governor | **19 Oct 2026** | Due `[FACT]` |
| ERCOT **Batch Zero Eligibility Verification Report** | **10 Dec 2026** | Loads provisionally in Batch Zero `[FACT]` |
| ERCOT **Community Impact Review Report** | **10 Dec 2026** | Medium loads 25–75 MW and large data center/crypto facilities, from RFIs to interconnecting TSPs and DSPs `[FACT]` |
| PUCT open meeting | **17 Dec 2026** | Both reports discussed `[FACT]` |

**The origination desk's product is "which parcels can be energized, on what date, blocked by what."** In Texas that answer is now *"none, pending audit"* — for grid energization at ≥75 MW, for environmental permitting at any size, for islanded and behind-the-meter projects by name, and for any other state approval.

**The fallback is closed too, and this is the part the earlier refactor log got wrong.** That document proposed redefining the Texas product as *queue eligibility and behind-the-meter pathing*. Both are inside the freeze: any real project needs an air permit, a water authorisation or a local entitlement; behind-the-meter gas needs a TCEQ air permit; islanded facilities are named explicitly. There is no adjacent approval to route around.

**What the origination desk can still honestly sell in Texas in Q4 2026 is a freeze-status map, not a path.** That is a real, urgent, short-dated engagement — and it is a credibility artifact, not a business.

**Moving to PJM is available and costly.** The origination dossier chose ERCOT at §7 for named reasons: the large-load queue, retail choice, and the best public data. PJM reintroduces the capacity-market complication that choice was meant to avoid, and discards the data advantage that justified it. A solo founder relocating to a harder market loses the thing that made the $0 start plausible.

**The curtailment business is not geographically gated in the same way.** Its product is the distribution of curtailment hours under a named set of tariff terms. That question is answerable in PJM, MISO, the Southeast or ERCOT, and it does not require anyone to be permitted to energize. A frozen Texas reduces the *national flow* of flexible-load agreements — which is one of its two top sensitivity drivers, and a genuine cost — but it does not remove the product.

---

## 2. Are they one company or two?

The honest answer is **mostly two, with a one-directional overlap** — and the direction matters more than the overlap.

### What they share

| | Both |
|---|---|
| Customer | 50–300 MW mid-market data center or neocloud developer |
| Buyer persona | VP Energy / Chief Development Officer; the lender's independent engineer as second reader |
| Data foundation | ISO/RTO filings, tariffs, PUC dockets, utility planning documents — all free |
| Delivery model | Fixed-fee analytical opinion, manual, weeks, no software |
| Go-to-market | A free, checkable public artifact buying inbound credibility |
| Moat logic | Independence from the operational vendor, plus a realized-outcome track record that only accrues in calendar time |
| Capital | No balance sheet, no ISO collateral at launch |

That is a substantial overlap, and it is why both emerged from the same research.

### What they do not share — and the asymmetry

| | Origination desk | Curtailment opinion |
|---|---|---|
| Revenue event | A **signed land or interconnection milestone**, 12–18 months out | A **delivered assessment**, 3–4 weeks out |
| Required asset | **Land control** — exclusive landowner marketing agreements | None beyond the method and the dataset |
| Scarce input | Originators who can close MW | Trusted share of a small market |
| Depends on | A grid that can energize | A tariff that exists |

**The overlap runs one way.** Doing curtailment assessments produces, as a by-product: utility planner relationships (you call them on every engagement), tariff fluency, site-level deliverability judgement, and the realized-outcome dataset. Those are the *knowledge* half of the origination desk's moat, and the harder half to buy.

**It produces none of the land half.** Entering origination later still means building a landowner book from zero. So the sequencing claim is real but partial, and I will not inflate it into a unified strategy.

**The reverse sequence does not work.** Origination cannot be entered first and extended into curtailment, because its launch market is frozen and it consumes $441k of capital (or five unpaid years) before its residual streams mature. There is no version where the origination desk funds the curtailment business.

**Conclusion:** one company, curtailment-first, with origination as an adjacency the first company might earn. Not two companies, and not a merger.

---

## 3. The comparison that decided it

Both figures sets are model outputs from `model/wattflock.py` and `model/final.py`, base case.

| | **Curtailment opinion** | Origination desk |
|---|---|---|
| Year-5 revenue | **$7.25M** | $5.81M |
| Year-5 EBITDA (margin) | **$2.80M (38.6%)** | $0.99M (17.0%) |
| Year-5 FTE | **12** | 19 |
| Revenue / FTE | $605k | $307k |
| Recurring share of revenue | **65%** | ~35% |
| **Peak capital required** | **$0** | **$441k** (prudent $650–750k) |
| Year-5 implied EV | **$22–40M** | $8–20M |
| Binding constraint | **Demand** — market formation × trusted share | **Capacity** — 110 MW per originator-year |
| MW touched per FTE-year | **~1,100** | ~110 |
| Cycle to a revenue event | **3–4 weeks** | 12–18 months |
| Kill test | Count tariff caps | Measure originator closings |
| **Kill test cost** | **$0, 3 days** | $0–400, **45–50 hours** |
| Launch market in Q4 2026 | **Open** | **Texas closed; PJM is a harder substitute** |
| Licensing for main revenue line | P&C producer + surplus lines (Phase 3) | PUCT broker (T3), ISO collateral (T4) |
| Name coherence | A pooled risk book is a flock | An origination desk is not |

### Four arguments, in order of weight

**1. One business sells the frozen good; the other does not.** This is not a tie-breaker, it is the decision. The origination desk's entire deliverable is an energization date and the blocking item in front of it. Texas has suspended the issuance of that answer at every agency, for every project size, including the off-grid configuration. The curtailment opinion sells a probability distribution over contract terms, which no permitting freeze suspends.

**2. The constraint types respond differently to effort, and only one of them responds at all.** The origination desk is capacity-constrained: its output is bounded by megawatts one originator closes per year, a property of the market's 12-to-18-month transaction cycle. Working harder does not change it, and capital does not either — $3.0M bought **+9%** of Year-5 revenue in the same model, and turned the downside into a $4M hole. The curtailment opinion is demand-constrained: bounded by market formation and by how much of a small market trusts it. **Share responds to published evidence and a scored track record, which is precisely what a solo founder with no money can manufacture.** A demand constraint is a problem you can work on. A capacity constraint is a ceiling.

**3. The kill test is 15× cheaper in time and cannot be frozen.** Three days reading 25 national tariffs against 45–50 hours of originator interviews. More importantly, the cap count resolves the *thesis*, whereas the throughput experiment resolves only one of three gates — and the origination desk's third gate (can a date be promised?) has just been answered *no* in its chosen market. Spending 45 hours to open a business whose market is shut is the wrong order.

**4. It dominates financially at a lower capital requirement.** 25% more revenue, 2.3× the EBITDA margin, 37% fewer people, nearly 2× the recurring share, 2–3× the enterprise value — and **$0 of capital against $441k.** The $441k matters more than the revenue gap: it is the difference between a business a founder owns outright and one that needs a receivable line or five unpaid years.

---

## 4. The honest case against the decision

Three objections survive, and the first is serious.

**4.1 The peril may already be capped — this is the real risk.**
Montana-Dakota permits up to 200 curtailment hours per year `[FACT]`. Pennsylvania's model large-load tariff ties interruptible service to PJM's Emergency Load Response Program `[FACT]`. If most of the 25 tariffs filed in 2026 carry hard annual caps, the unbounded tail the thesis monetises is bounded by rule.

**But a cap is not the same as a measurement, and the distinction decides how much damage it does.** A 200-hour cap supplies the maximum. It does not supply the expected hours, the P90 inside the cap, whether those hours land during peak compute value, or the revenue at risk given a tenant's SLAs. **So a capped world damages the insurance phase — less tail to transfer — while leaving the assessment question intact.**

The arithmetic of a capped world: assessment plus subscription only, against a national assessment market of **$2.3–13.3M/yr at 100% share** `[INFERENCE]`, gives roughly a **$3.5M** business. That is worse than the origination desk's $5.81M base — but it reaches it **with $0 of capital and 12 people rather than $441k and 19.** Even the degraded case is capital-light and founder-owned. **The downside shapes are not symmetric**, and that asymmetry survives the objection.

**4.2 The flock does not diversify early.** Curtailment follows system peak, peak follows weather, weather is regionally correlated. A book inside one ISO behaves as one risk. Pooling needs 4–6 independent regions and is a Year 5+ condition; reinsurers will load early books heavily for correlation. **Unchanged by this decision, and it is why the risk-transfer phase is the second act and not the plan.**

**4.3 The independence moat is positional, not structural.** Emerald AI already ships verification and compliance reporting, one product step from ex-ante risk quantification. If it spins out or white-labels an independent arm, the conflict argument that protects WATTFLOCK weakens considerably. **A large consultancy could replicate the method in 6–12 months; the protection is that the mid-market fee level is unattractive to them, not that they cannot do it.**

None of the three is a reason to prefer the origination desk, whose own moat section concludes "it might not" survive a funded entrant and whose market is currently shut.

---

## 5. Sequencing

```
NOW ──► Cap count (3 days, $0)                    ──► decides the thesis
     ├► Texas freeze-status map (free artifact)    ──► credibility + relationships
     │
     ├─ PASS (<60% hard caps) ──► Build the curtailment opinion.
     │                            DO NOT run the throughput experiment.
     │                            Origination stays an adjacency, revisited
     │                            only if customers ask for it.
     │
     └─ FAIL (>60% capped)   ──► Curtailment degrades to ~$3.5M, assessment
                                 and subscription only, $0 capital.
                                 THEN run the throughput experiment (45-50 h).
                                 ├─ clears 60 MW ──► origination desk, in PJM,
                                 │                   accepting the capacity-market
                                 │                   complication and $441k
                                 └─ fails       ──► build neither
```

**Why the Texas map runs in parallel and not instead.** It is the honest artifact for Q4 2026, it costs nothing, and it builds exactly the asset both businesses need — relationships with people who have a frozen project and a dated decision coming. It is also sellable as a short engagement: 6,608 MW is under Batch Zero audit, TCEQ reports on 19 October, two ERCOT reports land 10 December, and the PUCT discusses them on 17 December. Anyone with Texas exposure needs that mapped. **It is a door, not a company**, and it must not be confused with one.

---

## 6. Next 30 days

| Day | Action | Cost |
|---|---|---|
| 1–3 | **Cap count.** Pull all 25 large-load tariffs and service rules filed in 2026 from PUC dockets. Record: threshold MW, annual curtailment-hour cap (hard / soft / none), notice period, compensation or rate discount, non-compliance penalty. **Compute the share with hard caps.** | $0 |
| 4–5 | Apply the kill line. Write the answer down before interpreting it | $0 |
| 6–12 | **Texas freeze-status map.** Who is in Batch Zero provisionally (6,608 MW), who sits in the 25–75 MW medium-load bucket, what each 10 December report covers, what the 19 October TCEQ report means for air and water permits on a given project. Publish free | $0 |
| 13–20 | **Backtest feasibility, one node.** Reconstruct curtailment hours for one ERCOT node 2008–2026 under one named tariff construction. Validate against Uri (Feb 2021) and summer 2023. If public data cannot reproduce known events within ±25%, the product cannot be made | $0 |
| 21–30 | Approach 20 named targets with the map and a **priced, scoped, signable** curtailment assessment offer. Count signatures, not compliments | <$100 |

**Entity formation waits until an invoice is due.** Under $200 all in.

---

## 7. What would reverse this

| Condition | Action |
|---|---|
| >60% of flexibility-bearing tariffs carry hard caps **set at or below ~80 hr/yr** | Curtailment degrades to ~$3.5M. Run the throughput experiment; origination becomes the live candidate, in PJM. **Status 3 Oct: inconclusive, 23% coverage. Caps found are 100–225 hr, i.e. above the central case** |
| **New, from Test 01:** the addressable Phase-1 universe is ~26 flexibility-bearing tariff constructions, not 104 or 25; three-quarters of large-load tariffs are cost-allocation instruments with no curtailment pathway | Tightens §19 market sizing. Does not reverse the decision — it reduces the size of the thing chosen |
| **New, from Test 01:** SPP CHILLS (FERC ER26-1323, live 1 Jul 2026) offers ≤7 years of non-firm service with **no cap on curtailment frequency or duration** and no planning obligation | Strengthens the thesis. An RTO-wide, formally unbounded exposure created by FERC order. First-customer candidate |
| ERCOT backtest cannot reproduce Uri or summer 2023 within ±25% | The curtailment product cannot be built from public data. Stop; the method was the premise |
| 0 of 20 targets sign a priced assessment in 60 days | Willingness to pay is absent. Re-price once, then stop |
| No carrier will engage on the index, or loads the correlation at >40% of expected loss | The risk-transfer phase is unreachable. Business caps at assessment plus subscription, ~$3.5M, still at $0 capital |
| Texas freeze lifts **with** a dated, workable eligibility path, **and** throughput clears 60 MW | Origination becomes viable again in its intended market. Reopen the comparison — it was close on economics |
| Emerald AI or a major consultancy launches an independent curtailment-certification arm | The independence moat is gone. Reassess immediately; this is the fastest-moving threat |

---

## 8. What did not change

Both models stand as built. Curtailment: $7.25M Year-5 base, $2.80M EBITDA, 12 FTE, $0 capital, 65% recurring, $22–40M EV, demand-constrained, correlation problem unresolved until national scale. Origination: $5.81M, $0.99M EBITDA, 19 FTE, ~$441k peak deficit, 60 MW per originator-year kill line, no venture capital. **The economics of neither business moved. The availability of one market did, and that was enough to order them.**

Neither business is large. The curtailment opinion captures roughly **0.04% of the economic value it unlocks** — a toll on a large decision is still a small toll. The decision here is which small, capital-light, founder-owned business is worth five years, not which one is a venture outcome. **Neither is.**

---

## Appendix — corrections carried into the origination dossier

Two errors in the previous refactor are fixed in `WATTFLOCK_ORIGINATION_DESK_DOSSIER.md`:

**[R3, corrected]** The refactor claimed the 10 December filing "is the Community Impact Review Report, not an eligibility verification report." **Backwards — it deleted a filing ERCOT named.** The 11 September 2026 Batch Zero update schedules **two** reports for 10 December: the **Batch Zero Eligibility Verification Report** (loads provisionally in Batch Zero) and the **Community Impact Review Report** (medium loads 25–75 MW and large data center/crypto facilities, from RFIs to interconnecting TSPs and DSPs). Both restored. Docket 59220 stands.

**[R6, new]** The refactor log claimed the TCEQ freeze "reinforces the document's existing conclusion … it does not change the thesis." **Wrong.** The freeze covers environmental permits at any size, every state agency, and islanded behind-the-meter facilities by name — which is the fallback the document proposed. The operating conclusion is changed in place: paid delivery moves outside Texas, PJM is the alternate, and PJM reintroduces the capacity-market complication §7 chose ERCOT to avoid.
