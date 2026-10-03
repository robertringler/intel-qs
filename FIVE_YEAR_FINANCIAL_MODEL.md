# Five-Year Financial Diligence Memo
## Located Firm Capacity Origination — the business implied by the Strategic Research Dossier

**Date:** 3 October 2026
**Posture:** adversarial venture-finance diligence. The dossier is the subject, not the authority.
**Model:** formula-driven, 5 years, 3 scenarios, 2 financing modes, 20,000-draw Monte Carlo. Customer and cash rollforwards are enforced by assertion in code (`beginning + additions − churn = ending`; `beginning cash + FCF = ending cash`), and the model aborts if either fails.

---

## Executive Financial Conclusion

**The dossier identifies a real market. The business it implies is far smaller than the dossier claimed, and the gap is not a matter of judgement — it is an arithmetic error plus an omitted constraint.**

Four findings dominate.

**1. The dossier's own Year-5 base case was internally inconsistent, and it overstates this model by 9.5×.**
The dossier projected Year-5 revenue of $55.0M. Priced at the dossier's *own* stated unit rates, its two residual line items alone come to $67.3M — more than its stated total, before origination fees, retainers or screens:

```
flexibility   1,500 MW × $30,000/MW-yr                     = $45.00M
brokerage     1,500 MW × 2.0 mils ($14,892/MW-yr)          = $22.34M
                                              subtotal       $67.34M
                              ...against a stated total of   $55.00M
```
`[FACT — arithmetic on the dossier's §8 and §16]`

This model's Year-5 base revenue is **$5.81M**.

**2. The omitted constraint is who closes the megawatts.** The dossier modelled revenue *per MW* and never modelled origination *capacity*. Its Year-5 figure required roughly 5,000 MW of cumulative origination. At ~110 MW per originator-year that is ~45 originator-years — about 15 originators on staff by Year 3, a payroll of ~$2.2M/yr that the dossier's own $0-capital premise cannot fund. The dossier's revenue assumptions and its financing assumptions contradict each other. This model reaches **1,033 MW cumulative** by Year 5.

**3. This is a capacity-constrained business in an abundant market — which is the opposite of how the dossier framed it.** The Year-5 base case requires **0.57% of US annual MW origination flow** and **0.0097%–0.039% of the US origination revenue pool**. Market size is not the binding constraint and never becomes one inside five years. Internal throughput — recruiting, ramping and retaining originators — is. No amount of TAM relieves it. Across 20,000 Monte Carlo draws spanning the full structural range, **P(Year-5 revenue ≥ $55M) = 0.0%** and **P(≥ $25M) = 0.0%**.

**4. The $0 claim survives, but only in a specific and uncomfortable form.** Two bootstrap modes diverge sharply:

| | Year-5 revenue | Peak capital needed | Founder cash comp, 5 yrs |
|---|---|---|---|
| **Disciplined bootstrap** (hires while losses are fundable) | $5.81M | **$441k** | $220k |
| **Strict $0** (ending cash never below zero) | $4.53M (−22%) | **$0** | **$0 — five years unpaid** |

`P(peak capital < $50k) = 0.0%` in the disciplined mode. So: a single person *can* run this on literally no outside money, at a cost of 22% of Year-5 revenue and **five consecutive years of zero personal income**. That is sweat equity of roughly **$750k–$1.25M** in forgone salary `[ASSUMPTION: $150–250k/yr opportunity cost]` — which is the real entry price, and it is not zero.

**The honest headline:** the base case is a **$5.8M-revenue, ~19-person, $1.0M-EBITDA firm worth $8–20M after five years.** That is a good small business and a poor venture outcome. It is also, notably, the same order of magnitude as the closest real comparable — LandGate, at $12.2M of revenue after about a decade `[ESTIMATE — ZoomInfo/Owler]`. The model independently reproducing the one real-world data point is the strongest evidence that the haircut is right rather than merely pessimistic.

**One finding runs in the dossier's favour:** the unit economics are genuinely good. LTV/CAC of **8.1×** with a **4.9-month** CAC payback and a **70.7%** gross margin. The problem is not profitability per unit. It is that the number of units one firm can originate per year is small, and capital does not raise it — **$3.0M of funding buys only +9% of Year-5 revenue in the base case, and is actively destructive in the downside.** This business should not raise venture capital.

---

## 1. Business Model Extracted From the Dossier

Taken strictly from the dossier. No products invented to enlarge the projection.

| Element | Extraction | Label |
|---|---|---|
| **Exact customer** | Data center developer or "neocloud" operator needing 50–300 MW, holding GPU commitments and capital but no energized site. Explicitly not hyperscalers (internal power teams) nor sub-10 MW operators (uneconomic) | `[HYPOTHESIS]` — dossier §6; no customer evidence exists |
| **Economic problem** | Cannot identify a site that will energize before compute commitments expire. Median interconnection wait 61 months; 13% of 2000–2020 requests reached operation, 75% withdrawn | `[FACT — LBNL]` **[VERIFY] Primary-source verification required** |
| **Product sold** | (a) site-deliverability screening, (b) ongoing advisory retainer, (c) brokered site/power transactions, (d) electricity supply brokerage, (e) load-flexibility management | `[HYPOTHESIS]` |
| **Unit of sale** | Two units: the **engagement** (screens, retainers) and the **megawatt originated** (fees, residuals). The MW is the economically meaningful unit | `[INFERENCE]` |
| **Buyer** | VP Infrastructure / Chief Development Officer / CEO | `[HYPOTHESIS]` |
| **Payer** | Developer for screens, retainers and success fees; **electricity supplier** for brokerage residual (embedded in rate, not invoiced to customer); **ISO/RTO or load owner** for flexibility | `[FACT]` for the supplier-paid mechanic — industry standard |
| **Economic beneficiary** | Developer (time-to-energization), landowner (land monetized), supplier (load acquired), grid (deferred capacity) | `[INFERENCE]` |
| **Triggering event** | Compute commitment or tenant LOI secured without an energized site; or an interconnection study returning an unacceptable date/cost | `[HYPOTHESIS]` |
| **Pricing mechanism** | Fixed fee (screens $9–21k); monthly retainer ($96–198k/yr); success fee $/MW ($1.8–6.0k); per-kWh residual (0.25–0.85 mils); $/MW-yr flexibility share ($4–16k) | `[INFERENCE]` from dossier §8 and §16, haircut per §3 below |
| **Sales cycle** | 2–6 weeks (screen); **12–18 months** (brokered transaction) | `[HYPOTHESIS]` — dossier §6 |
| **Repeat purchase** | Developers run multi-site programmes; each site is a new screen and a new mandate | `[HYPOTHESIS]` |
| **Retention** | Retainer contracts; embedded dispatch relationships; supply contract terms of 3–5 years | `[INFERENCE]` |
| **Expansion** | Screen → retainer → origination mandate → supply brokerage → flexibility management on the same site | `[HYPOTHESIS]` |

### Monetization mechanisms the dossier supports — and their fate in this model

| Stream | Dossier assumption | Model assumption | Why changed |
|---|---|---|---|
| Screens | $5–25k | $9–21k | Retained |
| Retainers | implied | $96–198k/yr | Retained |
| Success fees | $2–15k/MW (blend $6k) | $1.8–6.0k/MW (base $3.5k) | 1–3% of the $584k/MW powered-land price is the dossier's own anchor; **that price is `[VERIFY]`**, and most sites a new entrant finds are secondary/tertiary, not primary-market |
| **Supply brokerage** | **2.0 mils → $14.9M/GW-yr** | **0.25–0.85 mils (base 0.50)** | **Materially reduced.** The 1–5 mil benchmark is explicitly a *retail C&I* rate `[FACT]`. Loads above ~150 MW increasingly bypass retail entirely — registering for direct wholesale access, e.g. as an ERCOT Controllable Load Resource `[FACT]`. Applying a mid-market retail rate to a segment that structurally exits retail is the dossier's largest single error |
| **Flexibility** | **$30k/MW-yr (25% of PJM's $118,625)** | **$4–16k/MW-yr (base $10k)** | **Materially reduced.** The load owner bears curtailment risk and holds the negotiating leverage; Emerald AI, at a $1.05bn valuation with $220M raised and NVIDIA backing, compresses the software share `[FACT]`. Also gated: PJM requires minimum capitalization *or posted collateral* `[FACT]` |
| Contracted-capacity ownership | dossier §9 | **excluded** | Requires project finance and is a Year 6+ event. Including it in a five-year model would be unsupported |

Mechanisms considered and **rejected as unsupported**: data subscriptions (the dossier itself argues against, citing LandGate's $12.2M ceiling), registry/settlement fees (Year 10+), licensing.

---

## 2. Core Unit Economics

### 2.1 The megawatt (the real unit)

```
BROKERAGE REVENUE PER MW-YEAR
  = 8,760 h × 0.85 load factor × 1,000 kWh/MWh × $/kWh
  = 7,446,000 kWh/MW-yr × $/kWh
  at 0.50 mils ($0.0005/kWh)              = $3,723 /MW-yr     [INFERENCE]
  (at the dossier's 2.0 mils              = $14,892 /MW-yr)

LIFETIME REVENUE PER MW ORIGINATED  (NPV @ 15%)
  = success fee
  + brokerage attach × rate × annuity(1/attrition)
  + flexibility attach × rate × annuity(1/attrition)
```

| | Downside | **Base** | Upside |
|---|---|---|---|
| Success fee (one-time) | $2,000 | **$3,500** | $5,000 |
| + Brokerage NPV (attach × rate × life) | $765 (18%×$1,862×3.1y) | **$4,000** (35%×$3,723×4.5y) | $13,000 (50%×$6,329×6.7y) |
| + Flexibility NPV | $1,000 (8%×$4,500×3.8y) | **$8,000** (20%×$10,000×6.2y) | $24,000 (32%×$16,000×9.1y) |
| **= Lifetime revenue / MW** | **$4,000** | **$15,000** | **$43,000** |
| − carrying, account mgmt, commission | $2,000 | **$5,000** | $8,000 |
| **= Lifetime gross profit / MW** | **$1,500 (39%)** | **$10,000 (66%)** | **$35,000 (81%)** |
| **Share of the $584k/MW powered-land price** `[VERIFY]` | 0.65% | **2.64%** | 7.29% |

**The 2.64% figure is the single most useful sanity check in this memo.** The originator captures about two-and-a-half cents of every dollar of asset value it unlocks. That is a credible intermediary take rate — real-estate and M&A success fees run 1–5% `[ESTIMATE]`. The upside case's 7.29% is above that range and should be treated as the suspicious input, not the aspiration.

### 2.2 The customer

```
CAC           = cumulative 5-yr S&M ÷ cumulative new customers
ARPU          = Year-5 revenue ÷ Year-5 average customers
Customer life = 1 ÷ annual logo churn
LTV           = ARPU × gross margin × customer life
CAC payback   = CAC ÷ (ARPU × gross margin) × 12 months
```

| Metric | Downside | **Base** | Upside |
|---|---|---|---|
| CAC | $20k | **$26k** | $19k |
| ARPU (Yr 5) | $59k | **$90k** | $135k |
| Gross margin | 67% | **71%** | 84% |
| Churn / implied life | 45% / 2.2 yr | **30% / 3.3 yr** | 22% / 4.5 yr |
| LTV | $88k | **$212k** | $516k |
| **LTV / CAC** | **4.4×** | **8.1×** | **26.6×** |
| **CAC payback** | **6.1 mo** | **4.9 mo** | **2.1 mo** |

**Metrics that cannot be reliably calculated, and must be flagged as such:**
- **Churn** — no historical data. The entire LTV calculation inherits this. A 30% assumption against a 45% reality cuts base LTV from $212k to $141k.
- **Net revenue retention** — not calculable. The expansion mechanism (screen → retainer → mandate → residual) is a `[HYPOTHESIS]` with zero observations.
- **ARPU is partly an artefact.** Most Year-5 revenue is MW-driven, not customer-driven, so dividing total revenue by customer count overstates the per-customer relationship. The MW economics in §2.1 are the more honest unit.

---

## 3. Modeling Assumptions

### Scenario levers — every material difference stated

| Driver | Downside | Base | Upside |
|---|---|---|---|
| Inbound leads/yr (Yr1→5) | 18→140 | 35→340 | 55→530 |
| Qualified conversations / selling FTE / yr | 68 | 85 | 100 |
| Lead qualification rate | 24% | 32% | 38% |
| Conversion, qualified → customer (Yr1→5) | 7%→12% | 12%→20% | 17%→26% |
| Logo churn | 45% | 30% | 22% |
| Screens per delivery FTE / yr | 10 | 13 | 16 |
| Retainer clients per delivery FTE | 1.7 | 2.2 | 2.8 |
| Screen price (Yr1→5) | $9k→$11k | $12k→$16k | $15k→$21k |
| **MW closed per originator / yr (Yr2→5)** | 22→55 | **48→110** | 75→170 |
| Success fee $/MW (Yr1→5) | $1.8k→$2.4k | $3.0k→$4.25k | $4.0k→$6.0k |
| Brokerage attach / rate / attrition | 18% / 0.25 mil / 32% | **35% / 0.50 mil / 22%** | 50% / 0.85 mil / 15% |
| Flexibility attach / $per MW-yr / start | 8% / $4.5k / Yr4 | **20% / $10k / Yr3** | 32% / $16k / Yr2 |
| New-originator first-year productivity | 25% | 40% | 55% |
| Flexibility carrying cost $/MW-yr | $5,200 | $3,600 | $2,600 |
| MW under management per account-mgmt FTE | 180 | 260 | 360 |
| DSO | 68 days | 48 days | 40 days |

### Three structural constraints absent from the dossier, added here

1. **Delivery capacity.** Screens and retainers are limited by delivery FTE-hours, not demand. 25% of delivery capacity is reserved for screens, since screens are the lead-generation product. Without this the model produced revenue/FTE of $1.46M — far outside services norms.
2. **Endogenous headcount.** In bootstrap mode the founder cannot hire into losses they cannot fund. The solver cuts founder pay first, then scales hiring. This creates the governing feedback loop: *gross profit → opex capacity → originator headcount → MW closed → residual revenue → gross profit.*
3. **Originator ramp.** A new originator produces at 25–55% in year one. A 12–18-month sales cycle makes instant productivity impossible.

### Load-bearing external inputs and their verification status

| Input | Use | Status |
|---|---|---|
| Powered land $584,000/MW, +51% | Anchors the success fee at 1–3% | **`[VERIFY]` Primary-source verification required** (CBRE; blocked by egress policy in the dossier's research environment) |
| PJM $325/MW-day = $118,625/MW-yr | Bounds the flexibility share | `[FACT — PJM 2028/29 BRA report, primary]` |
| Retail broker 1–5 mils | Brokerage rate, *then rejected* for >150 MW loads | `[FACT — industry]`; inapplicability `[FACT]` |
| Colocation ~$204/kW/month | Customer's cost-of-delay, i.e. willingness to pay | **`[VERIFY]` Primary-source verification required** |
| 61-month median queue; 13% completion | Motivates willingness to pay; not a model input | **`[VERIFY]` Primary-source verification required** |
| PJM minimum capitalization or collateral | Gates flexibility revenue; drives the collateral line | `[FACT — PJM credit overview, primary]` |

---

## 4. Customer Acquisition Model

```
Leads          = inbound(content) × √(hiring factor) + selling FTE × conversations per FTE
Qualified      = Leads × qualification rate
New customers  = Qualified × conversion rate
Ending custs   = Beginning + New − (Beginning × churn)        [asserted in code]
Selling FTE    = (1 − founder delivery share) + effective originator FTE
CAC            = S&M spend ÷ New customers
```

**Base case funnel:**

| | Yr1 | Yr2 | Yr3 | Yr4 | Yr5 |
|---|---|---|---|---|---|
| Leads | 73 | 163 | 303 | 540 | 811 |
| Qualified | 23 | 52 | 97 | 173 | 259 |
| Conversion rate | 12% | 16% | 18% | 19% | 20% |
| New customers | 2.8 | 8.3 | 16.3 | 29.8 | 50.1 |
| Churned | 0.0 | 0.8 | 3.1 | 7.1 | 13.9 |
| **Customers (end)** | **2.8** | **10.3** | **23.6** | **46.3** | **82.5** |
| S&M spend | $16k | $135k | $350k | $804k | $1.50M |

**The channel, modelled explicitly, with no paid acquisition.** The dossier's $0 claim rests on a free published artifact — a parcel-level map of substations with headroom — generating inbound credibility. The model gives this 35 inbound leads in Year 1 rising to 340 by Year 5, plus outbound capacity of 85 qualified conversations per selling FTE. Note that the founder in Year 1 is 55% occupied with delivery, so has only 0.45 FTE of selling capacity: **73 leads, 23 qualified, 2.8 customers, $34k of revenue.**

**$0 → first customer → $10k → $100k → $1M (base case):**

| Milestone | When | What has to happen |
|---|---|---|
| First $1 | Year 1 | One developer pays for one site screen after verifying one non-obvious claim in the free artifact |
| $10k cumulative | Year 1 | First screen delivered and a second sold |
| $100k cumulative | Year 2 | ~8 screens delivered; first retainer signed; founder still unpaid |
| $1M cumulative | Year 3 | First retainers compounding, first success fees closing from the Year-2 pipeline, ~100 MW closed |
| **$1M annual** | **Year 3** | 3.6 retainers + ~127 MW closed + first flexibility revenue |

Year 1 at **$34k** is the number that most contradicts the dossier, which projected $800k. A solo founder splitting time between selling and delivery, with no track record and a 12% conversion rate, cannot produce $800k. **The dossier's Year-1 figure is overstated roughly 24×.**

---

## 5. Five-Year Revenue Projection

Each stream modelled separately; aggregated only at the total.

### Base case

| | Yr1 | Yr2 | Yr3 | Yr4 | Yr5 |
|---|---|---|---|---|---|
| MW closed (annual) | 0 | 38 | 127 | 294 | 573 |
| MW brokered (cumulative) | 0 | 13 | 55 | 146 | 314 |
| MW flexibility (cumulative) | 0 | 0 | 25 | 80 | 182 |
| 1 Screens | $34k | $113k | $70k | $120k | $224k |
| 2 Retainers | $0 | $139k | $342k | $588k | $1.11M |
| 3 Success fees | $0 | $115k | $446k | $1.17M | $2.44M |
| 4 Brokerage residual | $0 | $25k | $122k | $351k | $797k |
| 5 Flexibility | $0 | $0 | $102k | $457k | $1.25M |
| **TOTAL REVENUE** | **$34k** | **$392k** | **$1.08M** | **$2.69M** | **$5.81M** |
| YoY growth | — | 1,062% | 176% | 149% | 116% |

*The Year-2 growth rate is an artefact of a $34k base and should not be read as momentum.*

### All three scenarios

| Year | Downside | **Base** | Upside |
|---|---|---|---|
| 1 | $6k | **$34k** | $112k |
| 2 | $47k | **$392k** | $1.22M |
| 3 | $112k | **$1.08M** | $4.83M |
| 4 | $140k | **$2.69M** | $12.97M |
| 5 | **$179k** | **$5.81M** | **$27.10M** |

**Year-5 revenue mix (base):** success fees 42%, retainers 19%, flexibility 22%, brokerage 14%, screens 4%. Residual streams (brokerage + flexibility) are 36% — which matters for the valuation multiple in §18.

**The downside is not a small profitable consultancy — it is a business that never achieves escape velocity.** It shrinks to 1.1 FTE, $179k of revenue, $3k of EBITDA, and the founder is never paid. Screens revenue actually *declines* after Year 3 as retainers consume the available delivery capacity. This is the modal failure mode and it is not catastrophic — it is merely unrewarding.

---

## 6. Five-Year Cost Projection

COGS is **built up from resources**, not taken as a percentage of revenue:

```
COGS = delivery labour (70% of analyst payroll + founder delivery share)
     + subcontracted engineering (9–20% of screen + retainer revenue)
     + residual carrying cost (brokered MW × $/MW-yr + flexibility MW × $/MW-yr)
     + account management (MW under management ÷ MW per AM FTE × loaded salary)
```

### Base case

| | Yr1 | Yr2 | Yr3 | Yr4 | Yr5 |
|---|---|---|---|---|---|
| COGS: delivery labour | $0 | $92k | $162k | $307k | $520k |
| COGS: subcontract | $5k | $35k | $72k | $128k | $207k |
| COGS: residual carrying | $0 | $6k | $123k | $390k | $858k |
| COGS: account management | $0 | $5k | $34k | $101k | $216k |
| **COGS total** | **$5k** | **$139k** | **$347k** | **$807k** | **$1.70M** |
| S&M (originator payroll, commission, travel, content) | $16k | $135k | $350k | $804k | $1.50M |
| R&D (engineering, cloud) | $1k | $7k | $19k | $203k | $278k |
| Operations (ops + analyst 30%, data/software) | $6k | $61k | $157k | $320k | $628k |
| G&A (founder, compliance, legal, insurance, admin) | $10k | $54k | $153k | $332k | $709k |
| **Total OpEx** | **$33k** | **$257k** | **$679k** | **$1.66M** | **$3.12M** |

**Cash expenses vs founder sweat equity — stated explicitly as the brief requires.** Year-1 cash costs total ~$38k. The founder is paid **$0** in Year 1, **$0** in Years 3 and 4 (the solver cuts founder pay to fund hiring), and $200k only in Year 5. Cumulative founder cash compensation across five years in the disciplined base case is **$220k**, against a market opportunity cost of **$750k–$1.25M** `[ASSUMPTION]`. **The business is financed primarily by the founder's forgone income, not by its own margins.**

**A cost the dossier omitted entirely:** state-by-state retail energy broker registration, ISO market-participant qualification, and E&O insurance. These appear as the legal/compliance line, rising to $155k/yr by Year 5 in the base case, plus **$450k of cumulative ISO collateral** posted as restricted cash. Both are prerequisites to the flexibility and brokerage revenue the dossier treated as freely accessible.

---

## 7. Five-Year P&L

### Base case

| Metric | Yr1 | Yr2 | Yr3 | Yr4 | Yr5 |
|---|---|---|---|---|---|
| Revenue | $34k | $392k | $1.08M | $2.69M | $5.81M |
| COGS | $5k | $139k | $347k | $807k | $1.70M |
| **Gross profit** | **$29k** | **$253k** | **$735k** | **$1.88M** | **$4.11M** |
| Gross margin | 86.0% | 64.5% | 67.9% | 70.0% | **70.7%** |
| Sales & marketing | $16k | $135k | $350k | $804k | $1.50M |
| R&D | $1k | $7k | $19k | $203k | $278k |
| Operations | $6k | $61k | $157k | $320k | $628k |
| G&A | $10k | $54k | $153k | $332k | $709k |
| **Total OpEx** | **$33k** | **$257k** | **$679k** | **$1.66M** | **$3.12M** |
| **EBITDA** | **($4k)** | **($4k)** | **$56k** | **$225k** | **$989k** |
| EBITDA margin | −12.4% | −1.1% | 5.2% | 8.3% | **17.0%** |
| D&A | $900 | $4k | $9k | $20k | $32k |
| EBIT | ($5k) | ($8k) | $47k | $205k | $957k |
| Taxes @25% | $0 | $0 | $12k | $51k | $239k |
| **Net income** | **($5k)** | **($8k)** | **$35k** | **$154k** | **$718k** |
| Revenue / FTE | $34k | $154k | $215k | $253k | **$307k** |

**Revenue per FTE of $307k is the key plausibility check** — it sits squarely in the professional-services range (elite boutique advisory runs $400–700k; Aon and Marsh are nearer $250–300k `[ESTIMATE]`). The upside case reaches $804k/FTE, at the very top of defensible, and its 62.9% EBITDA margin should be treated with suspicion: it assumes software-like economics on flexibility management that no comparable has demonstrated.

### Accounting profit vs cash generation — they diverge sharply

| Base case | Yr3 | Yr4 | Yr5 |
|---|---|---|---|
| EBITDA | $56k | $225k | $989k |
| Free cash flow | **($168k)** | **($201k)** | **$119k** |

**The business is EBITDA-positive from Year 3 but free-cash-flow-negative until Year 5.** Three causes: accounts-receivable build at 48 days DSO (the AR balance reaches $764k by Year 5), ISO collateral ($450k of restricted cash), and cash taxes paid on accounting profit before cash arrives. **Reporting EBITDA as evidence of self-funding would be wrong by $426k in Year 4 alone** ($225k of EBITDA against $201k of cash outflow).

### Scenario comparison, Year 5

| | Downside | **Base** | Upside |
|---|---|---|---|
| Revenue | $179k | **$5.81M** | $27.10M |
| Gross profit (margin) | $120k (67.0%) | **$4.11M (70.7%)** | $22.77M (84.0%) |
| EBITDA (margin) | $3k (1.9%) | **$989k (17.0%)** | $17.04M (62.9%) |
| Net income | $3k | **$718k** | $12.74M |
| FTE | 1.1 | **18.9** | 33.7 |

---

## 8. Five-Year Cash Flow

```
FCF = Revenue − COGS − OpEx − Taxes − ΔWorking capital − CapEx − ΔISO collateral
Ending cash = Beginning cash + FCF                              [asserted in code]
```

### Base case, disciplined bootstrap

| | Yr1 | Yr2 | Yr3 | Yr4 | Yr5 |
|---|---|---|---|---|---|
| Beginning cash | $15k | $4k | ($56k) | ($225k) | ($426k) |
| Revenue (cash basis) | $34k | $392k | $1.08M | $2.69M | $5.81M |
| COGS | $5k | $139k | $347k | $807k | $1.70M |
| OpEx | $33k | $257k | $679k | $1.66M | $3.12M |
| Taxes | $0 | $0 | $12k | $51k | $239k |
| Working capital (AR build) | $4k | $47k | $91k | $212k | $410k |
| ISO collateral | $0 | $0 | $102k | $119k | $150k |
| CapEx | $2k | $9k | $20k | $44k | $70k |
| **Free cash flow** | **($11k)** | **($61k)** | **($168k)** | **($201k)** | **$119k** |
| **Cumulative FCF** | **($11k)** | **($71k)** | **($240k)** | **($441k)** | **($322k)** |

- **Annual burn:** peaks at $201k (Year 4)
- **Maximum cash deficit:** **($441k)**, in Year 4
- **Minimum required capital:** **$441k** (base), $30k (downside — it shrinks instead of burning), $0 (upside)
- **EBITDA breakeven:** Year 3
- **Operating (FCF) breakeven:** Year 5
- **Monte Carlo P50 peak capital requirement: $482k; P(< $50k) = 0.0%**

### Is the $0 claim economically credible?

**Partly. The precise answer has three parts.**

**(a) Technically possible — yes.** A strict-$0 run, constraining ending cash to never fall below zero, is feasible:

| Strict $0, base | Yr1 | Yr2 | Yr3 | Yr4 | Yr5 |
|---|---|---|---|---|---|
| Revenue | $34k | $347k | $783k | $1.79M | **$4.53M** |
| EBITDA | ($4k) | $57k | $160k | $293k | **$724k** |
| Free cash flow | ($11k) | ($4k) | $0 | $0 | $0 |
| Hiring factor achieved | 1.00 | 0.74 | 0.35 | 0.44 | 0.86 |
| **Founder cash pay** | **$0** | **$0** | **$0** | **$0** | **$0** |

**(b) The cost of strict $0 is 22% of Year-5 revenue** ($4.53M vs $5.81M) and a hiring plan throttled to 35–44% of target in Years 3–4 — precisely when the origination pipeline needs people most.

**(c) It is only possible because the founder provides unpaid labour for five consecutive years.** Cumulative founder cash compensation: **$0**. This is not a $0-cost business; it is a business financed by **$750k–$1.25M of forgone salary** `[ASSUMPTION]`, which is simply an unpriced equity investment. Describing it as "starting with $0" is true of the bank balance and false of the economics.

---

## 9. Headcount

Hiring is triggered by affordability, not convention. No role is added because a conventional startup would add it.

### Base case

| Function | Yr1 | Yr2 | Yr3 | Yr4 | Yr5 | Loaded cost each |
|---|---|---|---|---|---|---|
| Founder | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | $0 / $0 / $0 / $0 / $248k |
| Originators | 0 | 0.5 | 1.6 | 3.7 | 6.0 | $149k |
| Analysts (delivery) | 0 | 1.0 | 2.0 | 3.7 | 6.0 | $118k |
| Operations | 0 | 0 | 0.4 | 0.9 | 2.0 | $105k |
| Engineering | 0 | 0 | 0 | 0.9 | 1.0 | $198k |
| Compliance / legal | 0 | 0 | 0.4 | 0.9 | 1.0 | $161k |
| Account mgmt (MW-driven) | 0 | 0.1 | 0.3 | 0.9 | 2.1 | $105k |
| **Total FTE** | **1.0** | **2.6** | **5.0** | **10.6** | **18.9** | |
| **Total personnel expense** | **$0** | **$217k** | **$492k** | **$1.22M** | **$2.42M** | |

Compensation assumes a 24% burden for payroll taxes and benefits `[ASSUMPTION]`. Account-management headcount is *derived*, not planned: one FTE per 260 MW under management, which is why the residual book carries real cost rather than arriving free.

Hiring logic: the first analyst arrives only when delivery capacity binds (Year 2, at 100% utilization). The first originator is half-time in Year 2 and produces at 40% of full productivity in their first year. Compliance arrives in Year 3 with state broker registrations. Engineering arrives in Year 4 — **after** $2.7M of cumulative revenue has proven the manual process, consistent with the dossier's own sequencing discipline.

---

## 10. Break-Even Analysis

```
Contribution margin = (Gross profit − commission) ÷ Revenue
Break-even revenue  = Fixed OpEx ÷ Contribution margin
```

Against the Year-5 base cost structure:

| | Value |
|---|---|
| Fixed OpEx (Year-5 OpEx less commission) | $2.79M |
| Contribution margin | **65.1%** |
| **Break-even revenue** | **$4.29M** |
| Actual Year-5 revenue | $5.81M (**1.35× break-even**) |

**Break-even by revenue mix** — the same fixed base, reached four different ways:

| Route | Volume required |
|---|---|
| Retainer clients only @ $156k/yr | **28 clients** |
| MW originated only (success fee @ $4,250/MW) | **1,009 MW/yr** |
| Screens only @ $16k | **268 screens/yr** |
| Flexibility only @ $10k/MW-yr | **429 MW under management** |

The retainer route is by far the most capital-efficient (28 clients against 268 screens for the same contribution), which is why the model allocates delivery capacity to retainers first. **A 1.35× break-even coverage ratio in the best full year is thin** — a 26% revenue shortfall erases Year-5 EBITDA entirely.

---

## 11. Capital Requirements

| Milestone | Capital required (base) |
|---|---|
| First paying customer | **~$4k** (entity formation, insurance, data; founder unpaid) |
| $10,000 cumulative revenue | **~$8k** |
| $100,000 cumulative revenue | **~$25k** (reached Year 2) |
| $1M annual revenue | **~$240k** (reached Year 3; cumulative FCF −$240k) |
| Cash-flow breakeven | **$441k** (Year 5) |

| | Absolute minimum bootstrap | Prudent operating capital |
|---|---|---|
| **Downside** | $30k | $150k |
| **Base** | **$441k** | **$650k–$750k** (MC P90–P95: $642k–$685k) |
| **Upside** | $0 | $200k (timing buffer) |

**Prudent capital exceeds minimum capital by ~50%** because the Monte Carlo P90 peak requirement is $642k against a base-case $441k — the distribution of the capital requirement is right-skewed, and running at the base-case estimate leaves a ~40% chance of running out.

**No VC assumed, and none warranted — see §17.**

---

## 12. Downside / Base / Upside Scenarios

| Metric | Downside | **Base** | Upside |
|---|---|---|---|
| **Year-5 revenue** | **$179k** | **$5.81M** | **$27.10M** |
| Year-5 ARR-equivalent (retainers + residuals) | $68k | $3.16M | $17.73M |
| Year-5 gross profit | $120k | $4.11M | $22.77M |
| Year-5 EBITDA | $3k | $989k | $17.04M |
| Year-5 EBITDA margin | 1.9% | 17.0% | 62.9% |
| Year-5 customers | 3 | 83 | 253 |
| Year-5 employees (FTE) | 1.1 | 18.9 | 33.7 |
| Capital required | $30k | $441k | $0 |
| Cash-flow breakeven | Year 4 | Year 5 | Year 1 |
| 5-yr cumulative MW originated | 118 | 1,033 | 2,735 |

---

## 13. Sensitivity Analysis

One-way, from base, Year-5 revenue. Ranked by swing.

| Rank | Variable | Low | High | Year-5 revenue swing | EBITDA range |
|---|---|---|---|---|---|
| **1** | **MW closed per originator / yr** | −50%: **$1.26M** | +50%: **$8.88M** | **$7.62M (−78% to +53%)** | $84k → $3.14M |
| 2 | Success fee $/MW | −50%: $2.45M | +50%: $7.70M | $5.25M (−58% to +33%) | $148k → $2.57M |
| 3 | Flexibility $/MW-yr | $5k: $4.57M | $18k: $7.45M | $2.88M (−21% to +28%) | $268k → $2.47M |
| 4 | Brokerage rate | 0.25 mil: $4.94M | 1.00 mil: $7.27M | $2.33M (−15% to +25%) | $314k → $2.19M |
| 5 | Delivery productivity | −30%: $4.75M | +36%: $6.85M | $2.10M (−18% to +18%) | $290k → $1.79M |
| 6 | Flexibility start year | Yr2: $5.97M | Yr5: $4.86M | $1.11M | — |
| 7 | Screen price | −50%: $5.44M | +50%: $6.17M | $0.73M | — |
| 8 | Residual attrition | 10%: $5.97M | 40%: $5.60M | $0.37M | — |
| 9 | Conversion rate | −50%: $5.61M | +50%: $5.81M | $0.20M | — |
| 10 | Logo churn | 15%: $5.81M | 50%: $5.81M | ~$0 | — |

**Two results worth dwelling on.**

**Churn and conversion barely matter.** This is counter-intuitive for a services business and it is diagnostic: by Year 5, 78% of revenue is MW-driven (success fees, brokerage, flexibility) rather than customer-driven. **The customer count is nearly irrelevant to the outcome; the megawatt count is nearly everything.** Any diligence that focuses on customer metrics is measuring the wrong thing.

**The single most dangerous assumption is MW closed per originator per year.** It carries a $7.62M swing on a $5.81M base — the only variable that can independently move Year-5 revenue by more than ±50%. And it is the assumption with **no empirical support whatsoever**. The dossier offers no evidence for it; I set base 110 MW/originator/yr by inference from a 12–18-month cycle and plausible deal sizes. If the true figure is 55 MW, Year-5 revenue is $1.26M and the business is not viable as anything but a consultancy.

---

## 14. Probabilistic Analysis

Two Monte Carlo runs, 20,000 draws each, triangular distributions.

**A caveat that must not be skipped.** The input ranges are the downside/base/upside bounds I set in §3. They are **modelling assumptions, not empirical distributions.** The output therefore measures *assumption sensitivity*, not real-world probability. No frequency data exists for any driver in this business. Reporting these as probabilities of commercial outcomes would be the exact error the brief warns against — so read them as "how much of the assumed parameter space leads where."

**Run 1** varied 9 drivers around the base business *design* (P5 $2.73M → P95 $8.17M). **Run 2**, reported below, additionally varies the structural levers — attach rates, headcount plan scale, pricing, delivery productivity, flexibility start year, cost rates — across the full downside-to-upside range.

### Year-5 revenue distribution (wide run)

| Percentile | Revenue | | Percentile | EBITDA |
|---|---|---|---|---|
| P5 | $1.82M | | P5 | $44k |
| P10 | $2.55M | | P10 | $127k |
| P25 | $4.03M | | P25 | $306k |
| **P50** | **$5.53M** | | **P50** | **$778k** |
| P75 | $7.15M | | P75 | $1.71M |
| P90 | $8.76M | | P90 | $2.74M |
| P95 | $9.80M | | P95 | $3.40M |
| P99 | $11.80M | | mean | — |
| mean | $5.65M | | | |

### Peak capital requirement

| P10 | P25 | P50 | P75 | P90 | P95 |
|---|---|---|---|---|---|
| $301k | $375k | **$482k** | $571k | $642k | $685k |

### Threshold probabilities

| Outcome | Probability |
|---|---|
| Year-5 revenue ≥ $1M | **99.2%** |
| Year-5 revenue ≥ $5M | **59.7%** |
| Year-5 revenue ≥ $10M | **4.3%** |
| Year-5 revenue ≥ $25M | **0.0%** |
| Year-5 revenue ≥ $55M (**the dossier's base case**) | **0.0%** |
| Year-5 revenue ≥ $100M | **0.0%** |
| Year-5 EBITDA > 0 | **98.2%** |
| Peak capital < $50k | **0.0%** |
| Peak capital < $250k | **4.5%** |
| Peak capital > $1M | **0.0%** |

**The two decisive readings.** First, **the dossier's base case does not appear anywhere in 20,000 draws spanning the entire plausible parameter space.** It is not a optimistic scenario; it is outside the model. Second, the distribution is remarkably *tight* — P10 to P90 spans $2.55M to $8.76M, barely 3.4×. A business whose outcome is capacity-constrained rather than demand-constrained has low variance, because the constraint binds in nearly every draw. **This is a high-probability small outcome, not a lottery ticket.** For a founder that is reassuring; for a venture investor it is disqualifying.

---

## 15. Market-Share Requirements

Addressable market taken from the dossier, with its own labels preserved.

| Layer | Size | Label |
|---|---|---|
| **TAM** — global electricity-sector investment | $2.2T/yr | `[FACT — IEA]` |
| **TAM** — global retail electricity spend | $3.1–3.7T/yr | `[INFERENCE]` |
| **SAM** — US origination + flexibility revenue pool | $15–60B/yr | `[INFERENCE — dossier §4.4]` |
| **SAM** — US MW origination flow | ~100 GW/yr | `[INFERENCE — dossier §4.4]` |
| **SOM** — this model, Year 5 (base) | $5.81M / 573 MW/yr | model output |

### Required share, Year 5

| | Share of US revenue pool ($15–60B) | Share of US MW flow (100 GW/yr) | Share of US retail electricity revenue ($514.8B `[VERIFY]`) |
|---|---|---|---|
| Downside | 0.0003% – 0.0012% | 0.044% | 0.00003% |
| **Base** | **0.0097% – 0.039%** | **0.573%** | **0.00113%** |
| Upside | 0.045% – 0.18% | 1.46% | 0.00526% |

**This is the most important analytical result in the memo, and it cuts both ways.**

Favourably: the projection requires on the order of **one hundredth of one percent** of the addressable revenue pool. It does not depend on winning a market, displacing an incumbent, or any heroic penetration assumption. The forecast is robust to almost any view of market size.

Unfavourably, and decisively: **because the required share is so small, market size is not the constraint — and therefore growing the market cannot grow the business.** The dossier's central rhetorical move was to establish that the pool exceeds $1T annually. The model shows that fact is nearly irrelevant to five-year outcomes. The business is gated by how many originators can be recruited, ramped and retained, and by a 12–18-month sales cycle. **A trillion-dollar market and a thousandth-of-a-percent share produce a $5.8M company.** TAM is not revenue, and here the distance between them is five orders of magnitude.

---

## 16. Competitive Response Analysis

| Scenario | Mechanism | Financial impact on Year-5 base |
|---|---|---|
| **A — No meaningful response** | Enverus and LandGate continue selling data subscriptions; Emerald AI stays inside the data center | Base case holds: **$5.81M** |
| **B — Existing companies copy the product** | Enverus adds per-MW transaction fees on its 136,000-acre / 272 GW dataset `[FACT]`; LandGate monetizes its marketplace transactionally | Success fee compresses ~40% ($3,500 → $2,100/MW) and MW/originator falls ~20% on competition for mandates. **Year-5 ≈ $3.6M, EBITDA ≈ $150k** |
| **C — A major incumbent bundles it free** | A hyperscaler or large utility offers origination free to win load or supply; Enverus bundles screening into an existing subscription | Screens → ~$0, retainers −50%, success fee −60%. **Year-5 ≈ $2.1M, EBITDA negative.** Business reverts to a boutique |
| **D — The market standardizes on an incumbent** | FERC's 2026 Show Cause Orders `[FACT]` produce mandated machine-readable transparency; Emerald AI's dispatch layer becomes the de facto flexibility standard | Flexibility stream largely lost (−$1.25M) and brokerage compressed. **Year-5 ≈ $3.9M.** But note: mandated transparency destroys the *data* business, which this model does not rely on. Partially survivable |

**Pricing power is explicitly not assumed to persist.** The base case already embeds compression: the success fee rises only from $3,000 to $4,250/MW over five years (+42% nominal, barely ahead of inflation), and brokerage is modelled at 0.50 mils against an industry range of 1–5 mils for smaller loads.

**The structurally dangerous scenario is C**, and it is not remote. A hyperscaler giving away origination to secure power, or a utility holding company standing up a merchant origination arm, would both be rational and would both compress this business to a boutique. The model's defence is weak: at Year-5 revenue of $5.81M there is no scale advantage, no network effect yet binding, and no switching cost worth the name. **The moat the dossier described — the realized-outcome dataset — does not become economically protective within five years.** It is a Year 7–10 asset, which means the five-year window is fought without it.

---

## 17. Bootstrap vs Funded Model

| | Bootstrap (disciplined) | Funded ($3.0M at inception) |
|---|---|---|
| **Year-5 revenue, base** | **$5.81M** | **$6.36M (+9%)** |
| Year-5 EBITDA, base | $989k | $1.37M |
| Max cumulative deficit, base | ($441k) | ($1.20M) |
| Year-5 FTE, base | 18.9 | 19.2 |
| **Year-5 revenue, downside** | **$179k** | **$858k** |
| **Year-5 EBITDA, downside** | **$3k** | **($1.60M)** |
| Max cumulative deficit, downside | ($30k) | **($4.40M)** |
| Capital required | $441k | $3.0M |
| Time to breakeven | Year 5 | Year 4 |
| Founder ownership | ~100% | ~60–75% `[ASSUMPTION: $3M at $9–12M post]` |

**$3.0M of capital buys 9% more Year-5 revenue in the base case.** That is the finding, and it is unusual enough to state twice. The reason: the binding constraints are originator productivity, the 12–18-month sales cycle, and the ramp time for new originators — **none of which capital relieves.** Money cannot shorten an interconnection study, cannot make a developer decide faster, and cannot make a newly hired originator productive in month one. Capital accelerates hiring into a funnel whose throughput is set by physics and counterparty behaviour.

**In the downside, funding is actively destructive**: −$1.60M of Year-5 EBITDA and a −$4.40M trough, versus a bootstrapped business that shrinks to 1.1 FTE and survives at break-even. Funding converts a non-viable business from a cheap failure into an expensive one.

**Conclusion: do not raise venture capital for this.** The right structure is bootstrap with a **$450–750k buffer** — ideally a line of credit against receivables, or customer prepayments on retainers, rather than priced equity. Dilution of 25–40% to accelerate Year-5 revenue by 9% destroys founder value. This conclusion is the opposite of the conventional recommendation and follows directly from the sensitivity analysis in §13.

---

## 18. Potential Enterprise Value

Multiples drawn from the **least flattering defensible** comparable set, as instructed.

| Comparable set | Revenue multiple | EBITDA multiple | Justification |
|---|---|---|---|
| Origination / advisory services | 1.0–2.0× | 6–9× | People-dependent, project revenue, limited recurring |
| Services + contracted residual book | 2.0–3.5× | 8–12× | Applies when residual mix > 25%; residuals are contracted and partly recurring |
| **LandGate (closest real comparable)** | — | — | **$12.2M revenue after ~10 years** `[ESTIMATE]` |

### Year-5 implied enterprise value

| | Residual mix | Revenue multiple → EV | EBITDA multiple → EV | **Defensible range** |
|---|---|---|---|---|
| Downside | 21% | 1.0–2.0× → $179k–$357k | 6–9× → $21k–$31k | **$20k–$350k** |
| **Base** | **35%** | **2.0–3.5× → $11.6M–$20.3M** | **8–12× → $7.9M–$11.9M** | **$8M–$20M** |
| Upside | 55% | 2.0–3.5× → $54.2M–$94.8M | 8–12× → $136M–$204M | **$54M–$95M** |

**Three disciplines applied.**

First, **for the upside I take the lower of the two methods** ($54–95M, not $136–204M). The EBITDA multiple produces a higher value precisely because the upside's 62.9% EBITDA margin is the assumption I trust least; using it would compound an optimistic input with a generous multiple.

Second, **the base case is cross-checked against reality and passes.** A model-derived $8–20M enterprise value on $5.81M of revenue sits in the same range as LandGate's actual $12.2M of revenue after a decade in an adjacent position. The model independently reproducing the one observable comparable is meaningful corroboration.

Third, and most important: **this business is not a billion-dollar company on a five-year view, and the large TAM provides no evidence that it is.** The dossier's §17 trillion-dollar arithmetic concerned a Year 15–20 infrastructure-ownership entity financed by project debt. Nothing in a five-year window speaks to it. **A $1T market and an $8–20M five-year enterprise value are both true and entirely consistent,** which is the central lesson of this exercise.

---

## 19. Falsification Tests — What Would Make This Business Fail?

Five assumptions that could destroy the economics, each with a cheap experiment. Priority given to tests costing $0–$1,000.

### 19.1 MW closed per originator per year (the most dangerous assumption)

| | |
|---|---|
| **Current assumption** | 110 MW/originator/yr by Year 5 (base); 48 MW in Year 2 |
| **Evidence for** | None in the dossier. Inferred from 12–18-month cycles, 50–300 MW deal sizes, and plausible 25–30% close rates `[HYPOTHESIS]` |
| **Evidence against** | LBNL: only 13% of interconnection requests ever reach operation and 75% are withdrawn `[FACT, VERIFY]`. If closings mirror that base rate, an originator working 8 live opportunities closes roughly one |
| **Failure threshold** | **Below ~60 MW/originator/yr the business cannot exceed $2M of Year-5 revenue and is a consultancy, not a platform** |
| **Experiment** | Interview 12–15 land/power originators at developers, utilities and brokerages. Ask one question: how many MW did you personally close last year, and over what cycle? |
| **Cost** | **$0–$400** (outreach; coffee). **Run this first.** It is the highest-value $400 in the entire plan |

### 19.2 Willingness to pay for a screen before any track record

| | |
|---|---|
| **Current assumption** | $12k screen in Year 1; 12% conversion of qualified prospects |
| **Evidence for** | Cost of delay is large — a 100 MW site delayed 12 months forgoes ~$245M of revenue at $204/kW/month `[VERIFY]` |
| **Evidence against** | Developers already retain CBRE/JLL and site-selection consultants. Value created ≠ willingness to pay, especially from an unknown solo vendor. The dossier assumes purchase on the strength of one non-obvious correct claim — untested |
| **Failure threshold** | **Fewer than 2 paid engagements from the first 50 qualified conversations** |
| **Experiment** | Publish the free substation artifact. Make 50 outbound approaches. Count paid engagements, not compliments |
| **Cost** | **$0** (public data, open-source tooling, own labour) |

### 19.3 Brokerage residual is accessible at all on large loads

| | |
|---|---|
| **Current assumption** | 0.50 mils on 35% of originated MW → $3,723/MW-yr |
| **Evidence for** | 1–5 mils is the documented retail C&I broker range `[FACT]` |
| **Evidence against** | **Strong.** That range is explicitly for *retail* supply contracts. Loads above ~150 MW increasingly register for direct wholesale access `[FACT]`, bypassing retail and the broker entirely. A supplier is unlikely to pay a boutique $370k/yr on a 100 MW load for an introduction |
| **Failure threshold** | **Below 0.15 mils or attach below 15%, the stream is immaterial (−$800k of Year-5 revenue, −14%)** |
| **Experiment** | Ask 5 retail suppliers and 3 wholesale market participants directly what they pay on loads above 50 MW, and at what size they stop paying |
| **Cost** | **$0** (8 phone calls) |

### 19.4 Flexibility revenue arrives before Year 5, and at a shareable rate

| | |
|---|---|
| **Current assumption** | $10k/MW-yr from Year 3, 20% attach |
| **Evidence for** | PJM clears capacity at $118,625/MW-yr `[FACT, primary]`; Duke/Nicholas estimates ~76–100 GW of curtailment-enabled headroom `[ESTIMATE]` |
| **Evidence against** | Order 2222 timing: PJM energy/ancillary services not until **Feb 2028**, MISO **Jun 2029**, SPP **Q2 2030** `[FACT]`. PJM requires minimum capitalization **or posted collateral** `[FACT]` — a capital gate. Emerald AI at a $1.05bn valuation with NVIDIA backing compresses the share `[FACT]`. The load owner bears curtailment risk and holds the leverage |
| **Failure threshold** | **Start slipping to Year 5, or rate below $5k/MW-yr: −$1.0M to −$1.25M of Year-5 revenue (−17% to −21%)** |
| **Experiment** | Read the ERCOT Controllable Load Resource and PJM DER aggregation registration requirements; price the collateral. Then ask 3 data center operators what share of flexibility value they would concede to a third party |
| **Cost** | **$0** (public tariffs) — **$1,500** if energy-regulatory counsel is engaged for an hour |

### 19.5 Working capital and collateral do not strangle the growth phase

| | |
|---|---|
| **Current assumption** | 48-day DSO; $450k of cumulative ISO collateral by Year 5 |
| **Evidence for** | Retainers bill in advance; success fees pay at closing |
| **Evidence against** | Brokerage residuals are paid monthly **in arrears** by suppliers, often on 30–60 day lags `[FACT]`. ISO settlement adds 30–60 days. Large developers dictate payment terms to small vendors. The model already shows Year-4 EBITDA of +$225k against FCF of −$201k |
| **Failure threshold** | **DSO above 75 days pushes peak capital beyond $650k and breaks the strict-$0 path entirely** |
| **Experiment** | Obtain standard payment terms from 5 target developers and 3 suppliers before signing anything |
| **Cost** | **$0** |

**Total cost to test all five falsifiers: $0–$1,900.** Four of the five cost nothing but time. The experiment in §19.1 is the one to run first; if it returns 60 MW rather than 110, the rest is moot.

---

## 20. Final Economic Assessment

**What the model says, stated without decoration.**

The dossier's market thesis survives this exercise; its financial projection does not. The opportunity is real: electricity capacity is genuinely scarce, the coordination failure is genuinely enormous, and the willingness to pay is plausible. **But the business implied by that thesis is a professional-services firm with a residual annuity attached, and it is bounded not by the market's size but by the number of megawatts its people can close.**

The base case is a **$5.8M-revenue, 19-person, $1.0M-EBITDA business worth $8–20M after five years**, requiring **$441k of working capital** — or **$0 of capital and five years of unpaid founder labour**, which is the same investment routed through a different account. The probability-weighted distribution is tight: **P10 $2.55M, P50 $5.53M, P90 $8.76M.** There is a 59.7% chance of exceeding $5M, a 4.3% chance of exceeding $10M, and — across 20,000 draws spanning the full plausible parameter space — **a 0.0% chance of reaching the $55M the dossier projected.**

Three things are genuinely attractive and should not be lost in the haircut. The unit economics are strong (LTV/CAC 8.1×, payback 4.9 months, 70.7% gross margin). The required market share is negligible (0.57% of MW flow), so the forecast is robust to almost any view of the market. And the downside is cheap: the business shrinks to one person at break-even rather than failing expensively, with a maximum loss of about $30k plus the founder's time.

Two things are disqualifying for venture capital and should be equally clear. Capital does not relieve the binding constraint — **$3.0M buys 9% more Year-5 revenue** and makes the downside catastrophic rather than merely disappointing. And the moat the dossier relied upon, the realized-outcome dataset, does not become economically protective inside five years, which leaves the business undefended in exactly the window when an incumbent bundling the function for free would compress it to a boutique.

**The correct characterization: a high-probability, low-variance, capital-efficient small business, in a market whose size is almost irrelevant to its five-year outcome.** Whether that is worth five unpaid years is a question about the founder's alternatives, not about the model. What the model can say is that the trillion-dollar framing in the source dossier had no bearing on the answer.

---

## Final Summary Table

| Question | Answer |
|---|---|
| **Can it start with $0?** | **Technically yes; economically no.** Strict $0 is feasible and reaches $4.53M by Year 5 (−22%), but requires **five consecutive years of zero founder pay** — $750k–$1.25M of forgone salary. The disciplined path needs **$441k**; P(peak capital < $50k) = **0.0%** |
| **First plausible paying customer** | A 50–300 MW data center developer or neocloud operator with GPU commitments and no energized site, buying a **$12k site-deliverability screen** after verifying one non-obvious claim in a free published artifact |
| **Year-1 revenue** | **$34k** base ($6k downside, $112k upside). The dossier's $800k is overstated ~24× |
| **Year-3 revenue** | **$1.08M** base ($112k / $4.83M) |
| **Year-5 revenue** | **$5.81M** base ($179k / $27.10M). MC: P10 $2.55M, P50 $5.53M, P90 $8.76M |
| **Year-5 EBITDA** | **$989k (17.0% margin)** base ($3k / $17.04M) |
| **Capital required to reach breakeven** | **$441k** minimum, **$650–750k** prudent (MC P90–P95). Or $0 with an unpaid founder and 22% less revenue |
| **Break-even point** | **$4.29M of revenue** (65.1% contribution margin, $2.79M fixed) = 28 retainer clients, or 1,009 MW/yr, or 429 MW under flexibility management. EBITDA-positive Year 3; FCF-positive Year 5 |
| **Year-5 customers** | **83** base (3 / 253) — but customer count is nearly irrelevant: 78% of Year-5 revenue is MW-driven |
| **Required market share** | **0.0097%–0.039%** of the US origination revenue pool; **0.573%** of US MW origination flow; **0.00113%** of US retail electricity revenue |
| **Biggest economic risk** | **Scenario C** — a hyperscaler or utility bundling origination for free to win load or supply. Compresses Year-5 to ~$2.1M with negative EBITDA, and the realized-outcome moat is not protective within five years |
| **Biggest assumption** | **MW closed per originator per year (110 by Year 5).** $7.62M of Year-5 swing on a $5.81M base, with **zero** empirical support. Below ~60 MW the business cannot exceed $2M |
| **Most important validation experiment** | **Interview 12–15 working land/power originators: "how many MW did you personally close last year, over what cycle?" Cost: $0–$400.** Run it before anything else |

---

### What the financial model implies about the economic significance of this opportunity, independent of the rhetoric surrounding it

The model implies that the opportunity's economic significance is real but modest at the level of the firm, and that the two are almost unrelated. The underlying market is as large as the dossier claimed — that was never in question and the model does not contradict it. What the model establishes is that the size of the pool does not transmit to the entrant: a five-year projection requiring one hundredth of one percent of the addressable revenue produces $5.8M of revenue and $8–20M of enterprise value, because the limiting factor is the throughput of a small number of people working 12-to-18-month transaction cycles, and that factor is indifferent to how much electricity the world buys. Capital does not relieve it, market growth does not relieve it, and no plausible combination of the assumed parameters relieves it — the distribution is tight precisely because the constraint binds in nearly every draw. The business is therefore best understood as a capital-efficient professional-services firm accumulating a contracted residual annuity, with good unit economics, a cheap downside, and a defensible but unremarkable five-year value. The trillion-dollar characterization in the source document describes a Year 15–20 infrastructure-ownership entity financed by third-party debt; it has no bearing on the five-year economics and should not be used to value them. On the evidence assembled here, the single most consequential unknown is not the market, the regulation, the technology or the competition, but how many megawatts one originator can actually close in a year — a question answerable for roughly $400, and one that should be settled before any further work is done.
