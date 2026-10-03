# Experiment 01 — Originator Throughput
## Concrete outreach plan for the $0–$400 test identified in §19.1 of the financial model

**Question under test:** how many megawatts of located firm capacity can one originator actually close in a year?

**Why it is first:** it carries a **$7.62M swing on a $5.81M Year-5 base** — the only variable in the model that can independently move the outcome by more than ±50% — and it has **zero empirical support**. Every other number in the five-year model is conditional on it.

**Kill threshold (pre-registered):** below **60 MW/originator-year**, planning-adjusted, the business cannot exceed roughly $2M of Year-5 revenue. It is a consultancy, not a platform.

---

## 1. Why the one-line version of this experiment is too weak

The memo said: *"Interview 12–15 originators. Ask how many MW you closed last year."* That design would produce the weakest evidence type available — **self-reported productivity data from people whose profession is selling.** Four biases attack it, and three are fatal if unaddressed.

| Bias | Mechanism | Fix |
|---|---|---|
| **Definitional drift** | "Closed" means different things: a land option, an ESA, an executed interconnection agreement, an energized site. A respondent naming the loosest milestone inflates by 3–5× | Pin the milestone explicitly, per deal, and record which one (§4) |
| **Attribution inflation** | Originators describe team or firm production as personal. "We closed 400 MW" becomes a data point of 400 | A mandatory `is_individual` flag; answers that fail it are **excluded**, not adjusted |
| **Lumpiness** | Deals are 50–300 MW on 12–18-month cycles. One year is pure noise: the same originator can show 0 MW or 250 MW | **Ask for three years, not one.** Divide by the period |
| **Selection / brand confound** | Respondents will skew toward originators at *established* firms with brand, inbound flow and existing landowner books. A solo startup hire has none of that | Treat the result as an **upper bound** and apply an explicit haircut (§4.3) |

**The selection/brand confound is the one most likely to produce a false "proceed,"** and it is handled by naming the discount rather than hoping it is small.

### The design fix: three tracks, not one

| Track | Evidence type | Cost | Beats interviews because |
|---|---|---|---|
| **A — Public-record deal census** | Hard, observed | $0 | No response bias, no recall error, no inflation. Counts what actually happened |
| **B — Structured interviews** | Soft, self-reported | $0–$400 | Only source for cycle time, close rate, and *why* deals fail |
| **C — Quota and job-ad evidence** | Semi-hard | $0 | Employers state MW targets in origination job specs. Reveals what firms *expect*, which is the planning number |

Run A and C first. They are free, require no one's cooperation, and they **calibrate** the interviews — walking into Track B already knowing the public-record answer is what stops a respondent's confident round number from becoming your plan.

---

## 2. Pre-registration — do this before collecting anything

Motivated reasoning is the live risk: the founder wants this number to be high. **Write the thresholds down and commit them before the first conversation.** They are already hard-coded at the top of `model/analyze_experiment.py`:

```python
KILL_BELOW    = 60            # MW/originator-yr, planning-adjusted
CAUTION_BAND  = (60, 90)
MODEL_BASE_MW = 110           # the assumption under test
HAIRCUT_RANGE = (0.50, 0.70)  # no-brand startup vs established-firm originator
MIN_VALID_N   = 10
```

**Do not edit those constants after data collection begins.** If you later believe a threshold was wrong, say so in writing, record why, and re-derive the model — do not quietly move the line.

**The decision statistic is the MEDIAN, not the mean.** MW/originator-year is expected to be right-skewed: a few originators land one enormous deal, most land one or two modest ones. The mean imports tail outcomes a single new hire cannot rely on. The analysis script flags skew automatically when mean/median > 1.4.

---

## 3. What a "unit" is — the measurement definition

Ambiguity here invalidates everything downstream, so the definition is read aloud to each respondent.

> **One MW counts when you were the originating lead on a transaction that reached a binding, signed milestone in the period — and the milestone is one of:**
> 1. executed land purchase, or an option assigned to a developer
> 2. executed energy supply agreement or PPA
> 3. executed interconnection agreement (LGIA, or a co-location/large-load agreement)
> 4. closed site sale
>
> **It does not count if:** it is still in the pipeline; the LOI is non-binding; you supported someone else's deal; or it is your firm's total rather than your personal production.

Record **which milestone** per respondent. This matters commercially, not just statistically: the fee event in the model attaches to milestones 1 and 4. A respondent whose 200 MW is all milestone 3 is describing a different business.

### 3.1 The haircut, stated plainly

The estimand the model needs is **not** "MW per experienced originator at an established firm." It is **"MW per originator hired by an unknown firm in its first three years."** The gap comes from brand, inbound deal flow, an existing landowner book, balance-sheet credibility and legal support — none of which a startup has.

`HAIRCUT_RANGE = 0.50–0.70` is an `[ASSUMPTION]`, not a measurement. The `brand_help` field (1–5: how much did your firm's name and inbound flow do the work?) lets you tighten it empirically — if respondents consistently answer 4–5, use the bottom of the range.

**A consequence worth seeing before you start:** if interviews return a median of 160 MW — a *favourable* result — the haircut yields a planning figure of 96 MW, and re-running the model gives **Year-5 revenue of $4.75M, below the $5.81M base case.** The base case was already at the optimistic edge of this parameter. The realistic range of outcomes from this experiment runs from "modestly worse than base" to "kill."

---

## 4. Sample frame

Target **n ≥ 10 valid** for a directional read, **n = 15–18** for the decision. Spread across segments; a sample concentrated in one segment is a failed sample, which the script reports.

| # | Segment | Why them | Target n | Inflation risk |
|---|---|---|---|---|
| 1 | Land/power origination at data center developers | The exact role being modelled | 4 | **High** — quota-carrying |
| 2 | **Ex-originators now at funds, OEMs or advisory** | **No quota to defend, no employer to flatter. The most candid segment** | **3** | **Low** |
| 3 | Renewable/IPP origination leads | Same land + interconnection work, far more numerous, decades of base rates | 3 | Medium |
| 4 | Utility large-load / economic-development account executives | See the other side: how many inbound projects actually energize | 2 | **Low** — no sales quota on this metric |
| 5 | Site-selection consultants and data center brokers | Know fee structures and who really closes | 2 | Medium |
| 6 | Land agents / ROW firms | Count parcels and options for a living | 1 | Low |
| 7 | Retail energy brokers serving large C&I | Primary source for §19.3 | 2 | Medium |

Segments 2 and 4 are the **calibration anchors**. When segment 1 says 150 and segments 2 and 4 say 45, the honest answer is nearer 45, and you have learned something more valuable than an average: you have learned the size of the inflation.

---

## 5. Sourcing names at $0

No purchased lists. Every source below is public and free, and several name individuals with titles directly.

**Best-value sources, in order:**

1. **Past conference speaker lists and agendas.** Data Center World, 7x24 Exchange, Infocast Transmission Summit, DistribuTECH, RE+, Bisnow DICE events. Agendas are archived and name person, title, firm — precisely the people on this list. *This is the single richest free source.*
2. **ISO/RTO stakeholder committee rosters.** PJM (MRC/MIC), ERCOT (TAC and subcommittees), MISO, ISO-NE, NYISO publish participant lists and meeting attendance. These are the people who show up to interconnection rulemaking.
3. **FERC eLibrary and state PUC docket service lists.** Filings in the large-load and co-location dockets name company representatives and counsel. The dossier's §3.3 dockets are the right ones.
4. **Interconnection queue files.** Public per-ISO, and they name the developer entity for all ~8,200 active projects. Entity → LinkedIn → the origination lead.
5. **Economic-development announcements.** State and county press releases on data center and manufacturing siting name the developer and often the utility account manager.
6. **LinkedIn search** on `("origination" OR "land acquisition" OR "site acquisition" OR "interconnection") AND (data center OR renewable OR "large load")`. Free search is workable; Sales Navigator for one month makes filtering faster.
7. **Job postings** — see Track C; these also name the hiring manager.

**Build a 120-name list.** At three minutes per name that is six hours, and it is the same artifact the business needs anyway: the beginnings of the relationship book the dossier identified as one of two uncopiable assets.

---

## 6. Outreach volume mathematics

Be realistic about response rates to a cold approach from an unknown person.

| Channel | Approaches | Response | Convert to call | Interviews |
|---|---|---|---|---|
| LinkedIn connect + note | 120 | ~25% | ~20% | **6** |
| Cold email (findable address) | 70 | ~8% | ~50% | **3** |
| **Referral / snowball** | 25 asks | ~50% | ~70% | **8** |
| **Total** | **~215 approaches** | | | **~17** |

**The snowball is the whole campaign.** Cold outreach alone converts at ~5% and would require 300+ approaches for 15 interviews. Every completed interview must end with the referral ask (§8.3) — it converts at 10× cold and is the difference between a three-week experiment and a three-month one.

**Honest time cost:** ~215 approaches at 3 min = 11 hours; 17 interviews at 20 min plus 15 min of notes = 10 hours; name-building 6 hours; Track A 15–20 hours; analysis 3 hours. **Total ≈ 45–50 hours over three weeks.** The memo's point stands: founder time is the real currency, and this experiment costs about $400 and a quarter of a month.

---

## 7. The reciprocity offer — why anyone replies

Nobody owes a stranger 20 minutes. The offer that makes this work costs **$0** and is the artifact the dossier's Day-7 plan already calls for:

> *"I'm building a free, public, parcel-level map of substations in ERCOT with apparent headroom and no queued project. Happy to send it over — I'd value 15 minutes on how origination actually works in practice."*

This is genuine reciprocity rather than a favour request, it signals competence before asking for anything, it is specific enough to be checkable, and it is the same free artifact that generates inbound leads later. **Build v0 of the map before the outreach begins.** Approaching with it halves the ask.

---

## 8. Outreach copy

Short, specific, no flattery, one question, easy to decline. Adapt but keep the structure.

### 8.1 LinkedIn connection note (300-character limit)

```
Researching how large-load/power origination actually works — specifically how
many MW one originator realistically closes per year. Building a free public map
of ERCOT substation headroom; happy to share it. Would 15 minutes be possible?
```

### 8.2 Cold email

```
Subject: 15 minutes on origination throughput — and a free dataset for you

<Name> —

I'm researching how located power capacity actually gets originated, and one
number I can't find anywhere: how many MW a single originator closes in a year.
Published sources cover queue volumes and interconnection timelines but nothing
on per-person throughput.

I saw your <panel at X / filing in docket Y / role at Z>, so you'd know.

Two things:

1. I'm building a free parcel-level map of ERCOT substations with apparent
   headroom and no queued project, from EIA, FERC and ERCOT data. Happy to send
   it whether or not we speak.

2. If you have 15 minutes, I'd ask about five things: MW you've personally
   closed over the last three years, what counted as "closed," typical cycle
   length, close rate on live opportunities, and what actually kills deals.

No pitch — I'm not selling anything and have nothing to sell yet. I'll share
the aggregated, anonymised findings with everyone who takes part.

<Name>
<phone> · <calendar link>
```

**Why this works:** names a specific gap, proves you did the work, gives before asking, states the questions so the time cost is knowable, and disclaims a sales motive truthfully.

**Do not** claim to be a student, a journalist, or a consultant if you are not. Misrepresentation taints the data and is unnecessary — "I'm researching whether to start a business in this" is a better door-opener than a cover story.

### 8.3 The referral ask — the highest-value sentence in the campaign

Delivered at the end of every interview, without exception:

```
"Two more things. First — who are the two best originators you know, including
competitors? Second — would you be willing to introduce me, or may I mention
your name?"
```

A named introduction converts at ~50% against ~5% cold. Log it in `referred_by`.

---

## 9. Interview guide (20 minutes)

Open-to-closed ordering so you do not anchor the number. **Never say "we assumed 110 MW"** — that contaminates the response irreversibly.

**Framing (60 seconds).** "Researching how origination really works. No pitch. Nothing attributed — I'll report ranges, never names or clients. If anything is confidential, skip it; I only need counts and ranges, not counterparties or prices."

**A. Role and base rates (4 min)** — open, un-anchored
1. Walk me through your last completed origination, start to finish. *(Listen for the milestone they treat as the finish line — this is the definitional-drift check, and it works best before you define anything.)*
2. How long did it take from first contact to signature?
3. How many live opportunities do you carry at once?

**B. The primary measurement (6 min)** — now read the §3 definition aloud
4. Using that definition — **over the last three years, how many MW did you personally originate to a signed milestone?** *(Then: how many separate deals? which milestone each?)*
5. Of the live opportunities you worked in that period, what share reached signature?
6. How much of that came from your firm's inbound flow and name versus your own sourcing? *(1–5 → `brand_help`)*
7. Would a newly hired originator at an unknown firm, with no inbound and no landowner book, do better or worse — and by roughly how much? *(Direct empirical read on the haircut. Ask it of every respondent.)*

**C. Piggybacked falsifiers (8 min)** — zero marginal cost, tests §19.2–19.5
8. If someone handed you a ranked, parcel-level shortlist with named utility contacts and a credible energization date, would you pay for it? **What would you pay?** *(→ §19.2; `q_wtp_screen_usd`. Push for a number; "it's valuable" is not data.)*
9. On loads above 50 MW, does anyone still pay a retail broker commission? At what MW does that stop? What rate? *(→ §19.3)*
10. If a third party managed your flexibility and monetised it, what share would you concede? *(→ §19.4)*
11. What payment terms do you impose on small vendors? *(→ §19.5; `q_dso_days`)*

**D. Close (2 min)**
12. What actually kills these deals?
13. The referral ask (§8.3).

**Conduct rules.** Ask consent before recording. Never request client names, contract prices tied to a named counterparty, or anything under NDA. Honour the anonymity promise — one breach ends the snowball. Send the promised map within 24 hours.

---

## 10. Track A — public-record deal census ($0, hardest evidence)

This is the track that does not depend on anyone's cooperation or honesty.

**Method.** For 12–20 named mid-market developers and IPPs, count deals that reached a signed milestone over 2023–2026 from public records, then divide by origination headcount.

```
MW per originator-year  =  MW reaching a signed milestone in the period
                           ÷ (origination FTE × years)
```

- **Numerator** from: interconnection queue entries and executed IAs (per-ISO public files); county deed and option records for land; press releases and economic-development announcements; FERC filings; for public companies, 10-K/10-Q and investor-day disclosures of MW contracted or sites secured.
- **Denominator** from: LinkedIn headcount filtered to origination, land, site acquisition and interconnection titles at that firm. Imperfect, and the main source of error — state it as a range.

**For the handful of public comparables, the denominator is disclosed.** Where a developer reports both MW secured and development headcount, you get a defensible firm-level figure with no self-reporting at all. Three or four such observations outweigh ten interviews.

**Expected precision:** ±40%. That is sufficient, because the decision threshold is 60 against an assumption of 110 — a 1.8× gap. The experiment does not need to distinguish 95 from 110; it needs to distinguish 45 from 110, and this track can.

---

## 11. Track C — quota and job-ad evidence ($0)

Employers write down what they expect. Search current and archived postings for "Director of Origination," "Land Acquisition Manager," "Site Acquisition," "Interconnection Manager" at data center developers, IPPs and utilities. Capture any stated MW target, deal-count target, or "manages a pipeline of X MW."

**Why this is good evidence:** a quota is an employer's own commercial estimate of achievable throughput, set by people with the historical data, and with money at stake. It is also *forward-looking* and *unflattering* — a firm that sets 80 MW is telling you more than an originator who recalls 150.

Treat a stated pipeline target as an **upper bound** on closings — pipeline is not closed. Log separately; do not pool with Track A or B.

---

## 12. Recording and analysis

**Template:** `model/responses.csv` — header row with the 21-field schema, ready to fill.

Key fields: `is_individual` (the exclusion gate), `years_covered` and `mw_closed_total` (the statistic), `milestone` (definitional drift), `brand_help` (haircut calibration), `segment` (skew check), plus `q_wtp_screen_usd`, `q_broker_mils_large`, `q_broker_cutoff_mw`, `q_flex_share_pct`, `q_dso_days` for the piggybacked falsifiers.

**Analysis:** `python3 analyze_experiment.py` from `model/`. It:

1. applies the exclusion rules and reports what was excluded and why;
2. computes median, mean, IQR and a 20,000-draw bootstrap 90% CI on the median;
3. flags right-skew when mean/median > 1.4;
4. applies the haircut and prints the planning range;
5. returns a verdict against the pre-registered thresholds;
6. **re-runs the full five-year model at the measured figure** and prints revised Year-5 revenue, EBITDA, FTE, peak capital, residual mix and implied EV;
7. summarises the four piggybacked falsifiers;
8. breaks the sample down by segment so a skewed sample is visible.

Verified against synthetic kill, proceed and empty-file cases before release.

---

## 13. Decision rules

Applied to the **planning-adjusted midpoint** (median × haircut), not the raw median.

| Result | Verdict | Action |
|---|---|---|
| Planning range entirely **< 60 MW** | **KILL** | Abandon the origination thesis. Year-5 revenue cannot exceed ~$2M; residual streams never reach scale. Redeploy to an alternative from dossier §20 — most likely the MGA/insurance-float architecture, which has the better financing structure |
| Range **straddles 60** | **INCONCLUSIVE** | Collect 8–10 more interviews weighted to the segment you would actually hire from. Do not commit either way |
| Midpoint **60–90 MW** | **CAUTION** | Viable but materially smaller than base. Re-plan at the measured figure. Expect Year-5 revenue of $2–4M. Reconsider whether that justifies five unpaid years |
| Midpoint **> 90 MW** | **PROCEED** | Thesis survives. Note that even 96 MW yields $4.75M — below the $5.81M base — so re-plan at the measured number regardless |

**Secondary triggers, any one of which changes the plan independently:**

- `q_wtp_screen_usd` > 0 for **fewer than 5 of 15** → §19.2 fails; the entry wedge is wrong even if throughput is fine
- `q_broker_cutoff_mw` median **below 100 MW** → §19.3 confirmed; cut brokerage from the model for target deal sizes (−$800k of Year-5 revenue)
- `q_flex_share_pct` median **below 8%** → §19.4 fails; flexibility is worth under $5k/MW-yr (−$1.0M)
- `q_dso_days` median **above 75** → §19.5 confirmed; peak capital exceeds $650k and the strict-$0 path breaks

---

## 14. Budget

| Item | $0 version | Recommended | Full |
|---|---|---|---|
| Domain (1 yr, credibility on cold email) | — | $12 | $12 |
| Email on domain (Cloudflare routing / Zoho free) | $0 | $0 | $0 |
| LinkedIn Sales Navigator, 1 month | free search | $99 | $99 |
| Transcription (local Whisper / free tier) | $0 | $0 | $0 |
| Scheduling (Calendly free) | $0 | $0 | $0 |
| Data, tooling (EIA/FERC/ISO data, Python, QGIS) | $0 | $0 | $0 |
| Coffee / meals, 3–4 in-person | — | — | $120 |
| One regional industry event | free events only | — | $150 |
| Contingency | — | $20 | $19 |
| **Total** | **$0** | **$131** | **$400** |

**The $131 version captures most of the value.** The domain matters more than it looks — a cold email from a personal gmail to a VP of Infrastructure is materially less likely to be read. Sales Navigator for one month compresses the name-building from six hours to about two.

Everything load-bearing is free: the data, the tooling, the name sources, and the reciprocity offer.

---

## 15. Three-week timeline

**Week 1 — build and calibrate (no outreach yet)**
- Days 1–2: build v0 of the free ERCOT substation-headroom map. This is the reciprocity offer and must exist before you ask for anything.
- Days 3–4: Track A public-record census on 12–20 firms. Track C job-ad sweep. **You now have a prior.**
- Day 5: build the 120-name list from conference agendas, ISO rosters and docket service lists.

**Week 2 — outreach**
- Day 6: first 40 LinkedIn approaches + 25 emails. Expect ~4 replies.
- Days 7–10: 4–6 interviews. Referral ask every time. Second wave of 80 approaches.
- Day 10: **interim check** — run `analyze_experiment.py` at n≈6. If the median is already below 40 or above 180, the answer may be arriving early.

**Week 3 — close out and decide**
- Days 11–14: snowball interviews (highest conversion). Target n = 15–18.
- Day 15: reconcile the three tracks. Where interviews exceed the public-record census by more than ~1.5×, trust the census and record the gap as measured inflation.
- Day 16: run the analysis, take the verdict, write down what you learned that you did not expect.

**Interim-read discipline:** look at n≈6 only to detect an extreme result, not to decide. Stopping early on a favourable partial read is the most likely way to corrupt this experiment.

---

## 16. How this experiment itself could fail

| Failure | Detection | Response |
|---|---|---|
| **Sample skews to one segment** | Script's by-segment breakdown | Weight outreach to the missing segments, especially ex-originators and utility account executives |
| **Everyone reports team production** | Exclusion count is high | Re-ask with the §3 definition read first; if it persists, lean on Track A |
| **Response rate below 3%** | Fewer than 3 replies from 60 approaches | The reciprocity offer is too weak — the map is not good enough, or not specific enough. Fix the artifact, not the copy |
| **Answers cluster on round numbers** (100, 200, 500) | Visible in raw data | Recall bias, not measurement. Push for deal-by-deal counts, which are harder to round |
| **n reaches 15 but the CI stays very wide** | Bootstrap CI spans the threshold | Genuine heterogeneity: throughput depends on segment and market. Re-plan around the specific niche you would enter rather than a market-wide average |
| **You like the answer** | — | Re-read the pre-registered thresholds before interpreting. This is the failure mode with no automatic detector |

---

## 17. What this experiment does **not** tell you

Boundaries, so the result is not over-claimed:

1. **It does not test whether you can recruit originators at all,** nor at what compensation. The model assumes a $120k base plus commission; if the market rate is $180k plus 25% of fees, the economics change independently of throughput.
2. **It does not test your own throughput as founder.** Years 1–2 depend entirely on that, and it is probably below the median of experienced professionals.
3. **It does not validate the $584k/MW powered-land price** or the colocation rate that anchors willingness to pay. Both remain `[VERIFY]` and require primary sources.
4. **It is retrospective.** If FERC's 2026 Show Cause Orders materially change interconnection terms, historical throughput may understate or overstate the future.
5. **n = 15 cannot distinguish 95 from 110 MW.** It can distinguish 45 from 110, which is what the decision requires. Do not read false precision into the median.

---

## 18. One-paragraph summary

Build the free ERCOT substation-headroom map first, because it is the only reason anyone will talk to you. Then establish a prior from public records and job postings before speaking to a single person, so that no confident round number becomes your plan. Approach roughly 215 people across seven segments — deliberately including ex-originators and utility account executives, who have no quota to defend — and ask every respondent for two introductions, because the snowball is the campaign. Read the measurement definition aloud before asking the number, ask for three years rather than one, record which milestone counted, exclude every team-level answer rather than adjusting it, and apply the 0.50–0.70 no-brand haircut without negotiating with yourself about it. Then run `analyze_experiment.py`, which re-runs the five-year model at whatever you measured and prints the verdict against thresholds you fixed in advance. Total cost $0–$400 and roughly 45–50 hours. The most likely outcome, given that even a favourable median of 160 MW yields a planning figure of 96 MW and a Year-5 revenue of $4.75M against a $5.81M base, is that the base case was already optimistic — and the experiment's real value is learning that for $131 instead of for five unpaid years.
