# Test 01 — Correction, and corrected status

**3 October 2026.** Supersedes the status line in `TEST_01_CAP_COUNT_RESULT.md`.

---

## 1. The error that matters most

That file concluded *"the decision to build the curtailment opinion stands."* **That was wrong.** The gate test returned inconclusive, and inconclusive means the gate is not passed. Carrying "build" forward is precisely what a pre-registered gate exists to prevent, and I did it in the same document that praised the discipline of not moving the kill line.

**Corrected status: GATE NOT PASSED. Nothing is being built. No company is being formed.**

---

## 2. Data-quality findings — and the error direction is consistent

Four of six data points were checked against better sources. **Two were wrong, one was over-claimed, and the one confirmed turned out to argue against the thesis.**

| # | What the test claimed | What the better source says | Verdict |
|---|---|---|---|
| 1 | **Colorado Springs Utilities** — 100 hr/yr interruptible cap, in the large-load tariff | **Electric Large Load (ELL) schedule, >10 MW: minimum 10-year initial contract; Minimum Monthly Bill on the higher of actual, contracted, or 100% of maximum 12-month demand; collateral of cash or LoC equal to 36 months of estimated minimum bills; auto-renews 36 months; 1.5%/month late fee.** The interruptible rate is a *separate* schedule for industrial loads >500 kW | **WRONG.** Two different schedules conflated. The large-load tariff is pure cost allocation |
| 2 | **Montana-Dakota** — 200 hr/yr at ≥10 MW, "High-Density Contracted Demand Response Rate" | **Rate 38, Interruptible Large Power Demand Response: available at 500 kW or more, interruptible for up to 100 hours annually.** Effective 1 April 2026 (WY). $2.55/interruptible kW credit; interruption within 30 minutes of notice | **WRONG** on hours, threshold and name. It is a conventional industrial interruptible rate, **not a data center tariff** |
| 3 | **Idaho Power** — 225 hr during summer peaks | **Schedule 20, Speculative High-Density Load**, effective 1 Jan 2026. Mandatory at ≥1,000 kW for 3+ of the last 12 billing periods. **Interruption window June 15 – September 15, 1:00–11:00 pm, Mon–Fri excluding holidays. Maximum 10 hours per event. Up to 225 hours annually. Not less than 2 hours' notice. Compensation $0.0453/kW per event hour** (Large General Service) | **CONFIRMED — and far more specified than the summary implied.** See §3 |
| 4 | **SPP CHILLS** — "RTO-wide, no cap on frequency or duration, no planning obligation … the strongest evidence for the thesis" | Non-firm **conditional** service for the conditional portion of a high-impact large load; shed before firm service; 1–7 year term that expires regardless; **"SPP will curtail the CHILLS if the supporting Resource is not available"**; customers **"should not be eligible to participate in the market for demand response because they are receiving a reduced level of transmission service … and a different curtailment priority"**; classified as non-market registered demand response for resource adequacy | **OVER-CLAIMED.** This is ordinary non-firm priority with a supporting-resource trigger and a term countdown. Non-firm service being curtailable by design and unplanned-for is the *definition* of non-firm, not a discovery |
| 5 | Evergy Missouri — annual event-hour limits | Not checked | unverified |
| 6 | AEP Ohio — 10–20 events/yr, no hour limit | Not checked against primary | unverified |

**The error direction is the finding.** Every time I got closer to a primary source, the tariff turned out to be *more* specified and the risk *more* bounded — never less. Two points dissolved entirely, one became a cost-allocation instrument, and the confirmed one specified more than I assumed was missing. **The thesis was partly an artifact of source quality: secondary trade summaries understate tariff specificity.**

---

## 3. Idaho Power Schedule 20 contradicts the thesis's core premise

My §5 argument was that even capped tariffs leave the decision-relevant quantity unspecified — the expected hours and *when* they land. Schedule 20 specifies all of it:

| Quantity I claimed was missing | Schedule 20 |
|---|---|
| Hard annual cap | **225 hours** |
| Per-event duration | **Maximum 10 hours** |
| **Seasonal window** | **June 15 – September 15** |
| **Hourly window** | **1:00–11:00 pm** |
| **Day-of-week** | **Mon–Fri, excluding holidays** |
| Notice | Not less than 2 hours |
| **Price of the hours** | **$0.0453/kW per event hour, published** |

The available window is roughly 13 weeks × 5 days × 10 hours ≈ **650 hours**, capped at **225**, in events of at most 10 hours, at a published credit rate.

**That is a spreadsheet, not a distribution problem.** A developer's energy lead can bound the worst case, the shape, and the net compensation in an afternoon. This is exactly the condition stated in advance as fatal: *a hard cap low enough that the residual is a spreadsheet.* It is one tariff, and it is a mandatory schedule aimed at speculative load rather than a negotiated flexible-service agreement — so it is not dispositive on its own. **But it is the only primary tariff this test actually reached, and it goes the wrong way.**

I should also drop the revaluation I attached to the residual spread. I priced a 40-vs-200-hour spread at roughly $1.1M vs $5.6M a year using **$2.45M/MW-yr of colocation revenue** — the same inflated value anchor flagged in the earlier financial memo, applied to a developer whose actual exposure is its own margin, not gross colocation revenue. The spread is real; **my sizing of it was overstated.**

---

## 4. A new adverse finding the test produced and I did not record

**CHILLS customers are barred from market demand-response participation.** The WATTFLOCK financial model's flexibility stream — $10,000/MW-year, 20% attach, **22% of Year-5 base revenue** — assumes a load owner has flexibility value to concede. On the one service that is genuinely curtailable by design, the customer cannot monetise flexibility in the market at all.

If that pattern holds for other non-firm large-load services, **stream 5 of the model is weaker than built**, and the model's Year-5 base of $7.25M is overstated by something approaching the flexibility line. I have not re-run it, because re-running a model whose gate test failed would be the same error as carrying "build" forward.

---

## 5. What the evidence actually points at

The market finding is the durable output of this test, and it points away from both theses as specified.

**About three-quarters of tracked large-load tariffs contain no curtailment pathway.** What they contain is financial protection: minimum bills, deposits and collateral, exit fees, ramp schedules, 10-to-15-year terms. Colorado Springs ELL is the clean example — 10-year initial contract, minimum monthly bill on the higher of three measures, **36 months of collateral**, 36-month auto-renewal.

**That is a stranded-cost and exit-exposure problem, not an hour-distribution problem.** A developer signing an ELL-type tariff is accepting a decade of minimum-bill liability and three years of posted collateral against a load forecast it cannot be sure of. The question is *"what does this tariff cost me if I under-build, ramp late, or exit,"* and it sits at the same deal moment, with the same customer, as the origination desk.

**I am not turning that into a third thesis.** This conversation has produced two companies already, and inventing a third off an inconclusive count — on the day the count's own data proved unreliable — would repeat the pattern rather than correct it. It is recorded as the most-supported *problem* found, entirely untested for willingness to pay.

---

## 6. Corrected status of both theses

| | Status |
|---|---|
| **Curtailment opinion** | **Gate not passed.** Count inconclusive at 23% coverage; 2 of 6 data points wrong; the one primary tariff reached specifies cap, event duration, seasonal and hourly window, and price, which is the pre-stated fatal condition; one revenue stream newly doubted. **Not killed — one adverse tariff is not a population. Actively doubted rather than merely unvalidated.** |
| **Origination desk** | **Still closed on market grounds.** The Texas freeze is unchanged: all data center permits, every state agency, islanded and behind-the-meter included |
| **Being built** | **Nothing** |
| **Texas freeze map** | **Dropped.** It was the demoted desk's artifact and should not have survived the demotion |

---

## 7. Next — primary reads only, no publishing, no building

| # | Action | Note |
|---|---|---|
| **1** | **SPP CHILLS order and tariff in full** — FERC docket ER26-1323, 195 FERC ¶ 61,196, 5 June 2026 order; the 10 Feb 2026 tariff revisions; the 6 July 2026 compliance filing | `spp.org` is egress-blocked here. Needs an unblocked browser or FERC eLibrary. **Read before any claim about CHILLS is repeated** |
| **2** | **The flexibility-bearing filings themselves** — the ~26 constructions, from Halcyon's tracker, the LBNL August brief, the EEI September list and state dockets | Primary only. Record for each: hard annual cap, per-event cap, seasonal and hourly window, notice, published compensation, and whether any expected-hours figure is given |
| **3** | **Pre-register the pass condition before reading** | Proposed: **kill if >40% of flexibility-bearing constructions publish either an expected-hours figure or a seasonal/hourly window.** Idaho Power Schedule 20 already satisfies that condition. Write this down before test 2 begins, not after |
| 4 | Nothing else | No artifact published, no entity formed, no customer approached |

**The reason to stop here rather than proceed:** the test designed to prevent a premature build returned inconclusive, its own inputs then proved unreliable in a consistent direction, and the single primary source reached pointed the wrong way. That is three independent reasons to read before acting, and none to act before reading.
