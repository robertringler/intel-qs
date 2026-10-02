# 120-Day Execution Plan: The Vertical Wedge

**Companion to:** `trillion-dollar-opportunity-dossier.md`
**Date:** 2 October 2026
**Capital required:** $0 through first revenue. No entity, tooling, or outside funding needed before Day 1.
**Evidence labels:** `[FACT]` · `[ESTIMATE]` · `[FORECAST]` · `[INFERENCE]` · `[HYPOTHESIS]`

---

## 1. The Vertical: AI decisioning inside regulated insurance operations

**Specifically: AI-assisted utilization management and claims determination at health plans, as the entry point into the broader AI Systems governance obligation now binding on regulated insurers.**

### 1.1 Why this vertical, derived from the dossier's own falsification tests

The dossier's §19 test 7 states: *if median monetised loss per adjudicated agent failure stays below ~$5,000, insurability fails, because frequency risk is retained by insureds rather than transferred.* That test, applied honestly, eliminates the vertical most people would pick first.

| Candidate vertical | Median loss per failure | Verdict |
|---|---|---|
| Autonomous customer service | **CA$812** (*Moffatt v. Air Canada*, the actual award) `[FACT]` | **Fails test 7.** High frequency, trivial severity. Uninsurable as a standalone line |
| AI coding agents | Diffuse, rarely monetised | Fails — no adjudicated loss event; buyer is engineering, not risk |
| AI hiring/screening | Audit fees commoditised; see §1.4 | Fails on value capture, not severity |
| **AI utilization management / claims determination** | **$15k–60k per wrongly denied episode**, plus bad-faith, regulatory penalty and class exposure `[ESTIMATE]` | **Passes decisively** |

A wrongly denied post-acute skilled-nursing stay runs ~$15–25k; an inpatient admission $20–60k; a specialty drug $5–50k/month `[ESTIMATE]`. Layered on top: statutory per-violation penalties, extracontractual/bad-faith exposure, market-conduct exam findings, and class action. This is the severity profile of an insurable long-tail liability line, not a service-credit.

### 1.2 Five converging conditions, all dated, none speculative

**(a) The most litigated AI use case in America, now in compelled discovery.**
`[FACT]` Putative class actions filed November 2023 against UnitedHealth (nH Predict, Medicare Advantage post-acute denials, alleged **90% error rate**) and Cigna (PxDx — alleged **300,000+ claims auto-reviewed in two months at ~1.2 seconds per claim**). Humana faces a near-identical action. **In March 2026 a magistrate judge ordered UnitedHealth to produce how nH Predict was built, whether it was designed to replace physicians, who sat on its internal AI Review Board, and what cost savings were achieved.**

`[INFERENCE]` The discovery order is the single most important fact in this plan. It converts "can you reconstruct how your AI reached this determination, and who actually decided?" from a governance nicety into a question every general counsel at every plan in the country now knows they may have to answer under oath, with internal communications attached. That is the most reliable purchase trigger in enterprise software: a peer's compelled discovery.

**(b) A binding governance mandate across 25 states, with an exam tool arriving now.**
`[FACT]` As of July 2026, **25 states have formally adopted the NAIC Model Bulletin on the Use of AI Systems by Insurers**, with 8 more in process; several non-adopting states already apply its expectations through market-conduct examination. It requires a written **AIS Program** with senior-management and board accountability, risk controls, **model validation and testing for bias and errors**, and **oversight of third-party AI tools, where the insurer remains fully responsible for the AI's behaviour.** `[FACT]` The NAIC's **AI Systems Evaluation Tool** for regulators is in state pilots and expected to be formally adopted at the **2026 Fall National Meeting** — i.e. within this plan's window.

**(c) California has already criminalised the core failure mode.**
`[FACT]` **SB 1120, the Physicians Make Decisions Act**, effective 1 January 2025: a licensed physician must make the final medical-necessity determination; the decision must rest on **the enrollee's own clinical circumstances rather than a group dataset alone**; plans must file policies and **remain accountable for accuracy**; services may not be denied, delayed or modified based solely on an AI algorithm.

`[INFERENCE]` "Remain accountable for accuracy" is an attestation hook with no incumbent supplier. No one currently sells a plan a defensible, independent evidentiary basis for that assertion.

**(d) A hard federal deadline is forcing procurement right now.**
`[FACT]` **CMS-0057-F requires payers to support electronic prior authorization by January 2027.** Payers are in active procurement for prior-auth automation *this quarter*. `[FACT]` The payer-side AI UM vendor field is real and named: **Cohere Health, Availity (AuthAI/Intelligentum, sub-90-second recommendations), Optum/Change Healthcare, CoverMyMeds (McKesson), Anterior ("Florence" agent, Stellarus partnership), Latent Health, Humata Health.**

`[INFERENCE]` A federal deadline three months out, in the most litigated AI category in the country, inside 25 states newly requiring documented third-party AI oversight, is as tight a timing window as this thesis will ever get. Procurement under deadline pressure *plus* a new governance obligation *plus* a peer in discovery is precisely the condition that makes an independent assessment purchasable in weeks rather than quarters.

**(e) And the structural reason this vertical beats every other — your customers are insurers.**

`[INFERENCE]` This is the argument that decided the selection, and it is specific to this vertical.

The dossier's escalator requires reaching rung 4 — delegated underwriting authority on a carrier's balance sheet. In every other vertical, rungs 1 and 4 have **disjoint** customer bases: you sell assessments to software companies, then start cold with insurers years later. Here they are **the same population.** A health plan is an insurer. It has an affiliated P&C or specialty arm, often a captive, and relationships with managed-care E&O and medical professional liability underwriters. Its chief risk officer and its general counsel think natively in terms of retained risk, transfer, and reserving.

You therefore meet your future capacity providers **as paying clients**, two to four years earlier than in any other vertical, and you build loss data about AI failures *inside insurance operations* — which is exactly the data needed to underwrite AI risk generally. **The vertical compresses the escalator.** That is worth more than a larger addressable pool.

### 1.3 Scope discipline: what this wedge is not
- **Not** general AI governance consulting. One use case: AI in medical-necessity and claims determination.
- **Not** an AI Act / NIST RMF compliance product. Those are frameworks; this is an evidentiary opinion on a specific deployed system.
- **Not** a bias-audit shop (see §1.4).
- **Not** software. No product is built in 120 days.

### 1.4 The cautionary precedent, stated up front
`[FACT]` NYC Local Law 144 mandates an **independent** bias audit by an auditor who may be neither the vendor nor the employer — structurally the exact business model proposed here. `[FACT]` But the New York State Comptroller's December 2025 audit found DCWP's enforcement **"ineffective"**: of 32 bias-audit disclosures DCWP reviewed, it identified **1** likely non-compliance, while the Comptroller found **at least 17** potential issues in the same 32.

`[INFERENCE]` A mandated audit with weak enforcement commoditises to a cheap checkbox, because buyers optimise for the cheapest document that satisfies a regulator who is not looking. **Do not anchor this business on a mandate.** Anchor it on three consequence-driven buying motives that survive weak enforcement: **litigation defensibility**, **market-conduct exam readiness** (where examiners do look, and findings carry penalties and corrective action plans), and **procurement unblocking** (where the vendor's revenue is the forcing function). The NAIC mandate supplies the vocabulary and the budget line; it must not supply the entire reason to buy.

### 1.5 If your network points elsewhere
`[INFERENCE]` The binding input on Day 1 is warm access to risk, compliance or clinical leadership — not domain knowledge, which is learnable in three weeks. If your network is in **P&C claims** (AI in claims handling/fraud: same NAIC bulletin, same exam tool, same severity profile, slightly lower litigation temperature) or **life/annuity underwriting** (same bulletin, accelerated-underwriting scrutiny), substitute that vertical and keep **every other element of this plan unchanged** — the regulatory hook, the escalator logic, the pricing, the schema and the gates all transfer, because they derive from the NAIC bulletin rather than from healthcare. If your access is in banking (model risk management under SR 11-7) the plan transfers but the competitive field is mature and crowded; expect worse pricing. Do **not** substitute a vertical that fails §1.1's severity test.

---

## 2. The 120-Day Objective

**One sentence:** Publish the reference failure taxonomy for AI determination systems, convert it into three or more paid independent assessments, produce the first structured loss-observation dataset in the category, and open one credible insurance-capacity conversation — all without outside capital.

### Four assets, in dependency order
| # | Asset | Done by | Why it exists |
|---|---|---|---|
| 1 | **ADR-1**: published, versioned failure taxonomy + scoring rubric for AI determination systems | Day 21 | The citable artefact. Creates standing; costs $0; is the thing you are hired to assess against |
| 2 | **The engagement**: a repeatable 3-week independent assessment with fixed scope and fixed fee | Day 45 | Converts standing into revenue and revenue into data |
| 3 | **The loss schema**: structured, severity-monetised observations from every engagement | Day 60 | The only asset that compounds and cannot be bought |
| 4 | **The capacity thread**: a live conversation with an underwriter who writes managed-care E&O or MPL | Day 120 | Opens rung 4. Without it, the ceiling is a consultancy |

### Three gates with explicit kill criteria
| Gate | Day | Pass | Kill |
|---|---|---|---|
| **A — Interest** | 30 | ≥20 qualified conversations held; ≥3 unsolicited written scoping requests | <1 scoping request → the problem is not felt. Stop or change vertical |
| **B — Willingness to pay** (dossier falsification test 2) | 90 | ≥3 paid engagements; ≥$60k booked | ≤1 paid engagement after 30+ qualified conversations → **thesis falsified at the wedge. Stop.** |
| **C — Insurability + pull** | 120 | ≥1 repeat or referred engagement; ≥1 underwriter in a second meeting; median observed severity >$5k (test 7) | Severity median <$5k across ≥40 observations → the risk is retained, not transferable. Revert to a certification-only business and re-plan |

`[INFERENCE]` Gate B is the entire point of the 120 days. It costs nothing but time and it tests the assumption on which every projection in the dossier depends. Running it honestly matters more than passing it.

---

## 3. Week-by-Week

### Days 1–14 — Learn the domain properly, then write the taxonomy

**Objective:** become genuinely competent on AI in utilization management. Not conversant — competent. Risk and clinical leaders detect bluffing in one question, and credibility is the only product.

**Days 1–5: primary sources only.** All free.
- `[FACT]` **CA SB 1120** full text and DMHC filing guidance; the "group dataset alone" and "accountable for accuracy" language verbatim.
- `[FACT]` **NAIC Model Bulletin on the Use of AI Systems by Insurers** — full text; build the list of the 25 adopting states and their adoption instruments.
- `[FACT]` **CMS-0057-F** final rule — the January 2027 obligations and what they require of payer decisioning systems.
- Medicare Advantage utilization-management rules: CMS coverage-criteria requirements, the two-midnight rule, adverse-determination notice requirements, appeal timelines.
- The **nH Predict and PxDx complaints** themselves, plus the March 2026 discovery order. Read the complaints, not the coverage: they are a free, specific, lawyer-drafted enumeration of exactly how these systems fail and what plaintiffs allege the plan should have done. This is the single highest-value document set available.
- NCQA UM accreditation standards and typical delegated-vendor oversight audit requirements — this establishes the **existing purchase motion** you are extending, which is how you avoid sounding like a new category nobody budgets for.

**Days 6–10: interview for calibration, not for sales.** Fifteen to twenty conversations with: former UM medical directors, UM nurse reviewers, appeals-and-grievances staff, health-plan compliance analysts, and plaintiff-side ERISA/bad-faith attorneys. Framing: *"I'm writing a public taxonomy of how AI goes wrong in utilization review. What have you actually seen, and what would you want an independent reviewer to check?"*

`[INFERENCE]` Former staff and plaintiff attorneys will talk freely; current plan employees will not. Plaintiff-side attorneys are the single most underrated source: they have already built, at their own expense, detailed theories of exactly how these systems fail and what evidence would establish it. That is your rubric, pre-validated by people with money at stake.

**Days 11–14: draft ADR-1.** Content specified in §4.

**Output by Day 14:** complete draft taxonomy; 15–20 calibration conversations; a target list of 60 organisations (§5).

---

### Days 15–30 — Publish, then run the first 20 outreach conversations

**Day 15–18: ship ADR-1 publicly.**
- Static site, free hosting, no gate, no email capture. Versioned (`ADR-1 v1.0`), dated, numbered clauses so it can be cited precisely: *"assessed against ADR-1 v1.0 §4.2"*. Plain licence permitting anyone to reference it.
- Publish alongside it a short note: *"Why we are publishing this instead of selling it"* — the standard is free; the opinion is not.

`[INFERENCE]` Publishing free is the non-obvious move and it is correct. A standard's value is proportional to citation, and nothing behind a paywall gets cited. Every incentive points the other way for a founder with no revenue; resist it. The monetisable asset is the independent opinion, which cannot be pirated because it requires an independent party to sign it.

**Days 18–30: outreach.** Target 60 contacts → 20 conversations held. Sequence and copy in §6.
- Two populations, run in parallel: **vendors** (Anterior, Cohere Health, Latent Health, Humata Health and the next tier of payer-side AI UM startups — stalled in payer AI-governance review, revenue on the line, decide in days) and **payers** (regional plans, Medicaid MCOs, provider-sponsored plans, BUCA subsidiaries — slower, bigger budgets, exam-driven).
- Start with vendors. `[INFERENCE]` They move 5–10× faster, they have an acute commercial reason to pay, and each one that buys becomes a distribution channel into the payers in its pipeline — which converts your CAC to roughly zero.

**Gate A at Day 30.**

---

### Days 31–60 — Sell and deliver the first engagement

**Days 31–40: convert.** Target 3 signed. Pricing and terms in §7–8. Terms that matter from engagement one: **50% deposit**, fixed fee, fixed 3-week scope, and a **data clause** permitting your retention and anonymised aggregate use of findings. The data clause is not negotiable and is worth more than the fee.

**Days 38–55: deliver engagement #1.** The three-week cycle:
- *Week 1 — Scope and evidence request.* System boundary, lines of business, determination types in scope, the specific ADR-1 clauses assessed. Request: model/system documentation, the decisioning policy as filed, the prompt/rule/criteria configuration, the human-review workflow definition, 12 months of determination and appeal-overturn data, audit-log samples, and the vendor contract's oversight provisions.
- *Week 2 — Adversarial testing and evidentiary review.* Re-run a held-out sample of 300–500 real historical determinations. Two questions dominate: **can the determination be reconstructed after the fact** (the discovery question), and **did a qualified human genuinely decide, or ratify** (the SB 1120 and nH Predict question). Then disparity analysis across protected classes, criteria-version correctness, turnaround-clock integrity, and appeal-loop independence.
- *Week 3 — Report.* Structure in §7.3.

**Days 55–60: instrument.** Every finding entered into the loss schema (§9) the day it is found, not retrospectively.

---

### Days 61–90 — Make it repeatable, publish the aggregate, open the capacity track

**Days 61–75: engagements #2 and #3,** with the first contractor paid from revenue — a former UM medical director on a per-engagement basis for clinical sign-off. `[INFERENCE]` Hire credibility before capacity. A report on medical-necessity determinations that is not clinically signed is worth materially less, and the right clinician's name on it is worth more than three weeks of your own time.

**Days 70–80: publish the first aggregate findings report.** *"Findings from the first N independent assessments of AI determination systems"* — anonymised, de-identified, with frequency and severity distributions by ADR-1 clause.

`[INFERENCE]` This is the distribution engine and the second-most-important artefact after ADR-1. It is the document that gets cited in trade press, forwarded inside plans, and — critically — **read by underwriters**, because it is the first severity-distributed loss data in the category. It generates inbound at zero CAC and it is your entire credential with capacity providers.

**Days 75–90: open the capacity track (§10).** Six to ten approaches to managed-care E&O and MPL underwriters, specialty MGAs, and Lloyd's managing agents. The ask at this stage is *not* an appointment — it is a second meeting and a reaction to your loss data.

**Gate B at Day 90.**

---

### Days 91–120 — Convert to recurring, formalise, and decide

**Days 91–105:**
- Convert at least one engagement to **annual surveillance** (§8). This is the single most valuable commercial step in the 120 days: it turns project revenue into recurring revenue and turns point-in-time assessment into continuous data flow.
- Publish **ADR-1 v1.1**, revised from real findings. Versioning visibly in response to evidence is what distinguishes a standard from a marketing document.
- Draft the first **RFP language** a payer could paste into a vendor solicitation requiring independent ADR-1 assessment, and give it away to friendly contacts. `[INFERENCE]` This is how a standard becomes a requirement: not by lobbying, but by making it trivially easy for a buyer to demand it. The first RFP naming ADR-1 by version is the first network effect in the dossier's §22.

**Days 100–115: legal and risk hygiene (§13).** Entity, E&O, opinion scoping, independence policy. Funded from revenue.

**Days 115–120: Gate C and the Day 121 decision (§15).**

---

## 4. Asset 1 — ADR-1, the taxonomy

The substantive content. Each failure mode carries: definition, observable indicators, evidence required to assess it, the legal or regulatory hook, and a severity band.

### Part I — Decision integrity
| # | Failure mode | Hook |
|---|---|---|
| 1.1 | **Group-data substitution** — determination driven by cohort/benchmark prediction rather than the enrollee's own clinical circumstances | **SB 1120** directly; the core nH Predict allegation |
| 1.2 | **Criteria misapplication** — wrong guideline, wrong version, wrong line of business, or criteria applied more restrictively than as filed | MA coverage-criteria rules; state UM law; filed-policy accountability |
| 1.3 | **Incomplete clinical picture** — determination rendered on partially retrieved records without flagging the gap | Medical-necessity standard; appeal reversal exposure |
| 1.4 | **Scope excursion** — system used for a benefit, population or determination type it was never validated on | NAIC AIS Program validation requirement |
| 1.5 | **Configuration drift** — thresholds, prompts or criteria changed without revalidation or change control | NAIC AIS Program risk controls |

### Part II — Human authority (the highest-severity cluster)
| # | Failure mode | Hook |
|---|---|---|
| 2.1 | **Ratification, not decision** — a qualified reviewer nominally decides but effective authority sits with the model; measurable as near-100% concordance, sub-threshold review durations, and absent documented independent reasoning | **SB 1120**; the central nH Predict and PxDx allegation. *Cigna: ~1.2 seconds per claim* |
| 2.2 | **Reviewer qualification mismatch** — reviewer lacks the specialty standing the determination requires | State UM law; MA rules |
| 2.3 | **Appeal-loop contamination** — the same model or configuration informs the appeal of its own determination | Independent-review requirements; basic adjudicative fairness |
| 2.4 | **Override suppression** — reviewer disagreement is hard to record, discouraged, or invisible in the audit trail | AIS Program governance; discovery exposure |

### Part III — Reconstructability (the discovery cluster)
| # | Failure mode | Hook |
|---|---|---|
| 3.1 | **Non-reconstructable determination** — the decision cannot be rebuilt after the fact from retained artefacts (inputs, criteria version, model version, reviewer actions) | **The March 2026 nH Predict discovery order.** Litigation-fatal |
| 3.2 | **Inadequate adverse-determination rationale** — notice fails to state a reason that survives appeal or regulatory review | Adverse-determination notice requirements |
| 3.3 | **Audit-log insufficiency** — logs lack identity, timestamp, version or sequence fidelity to establish who decided what, when | AIS Program; evidentiary admissibility |
| 3.4 | **Third-party opacity** — the plan cannot evidence oversight of a vendor's system it remains fully responsible for | **NAIC bulletin third-party provision, explicitly** |

### Part IV — Equity and outcome monitoring
| # | Failure mode | Hook |
|---|---|---|
| 4.1 | **Disparate determination rates** across protected classes and their intersections | Civil rights law; ACA §1557; NAIC bias-testing requirement |
| 4.2 | **Overturn-signal suppression** — high appeal-overturn rates not fed back into the system or escalated | AIS Program; evidence of knowledge for bad-faith purposes |
| 4.3 | **Proxy discrimination** — facially neutral features reproducing protected-class effects | Same |
| 4.4 | **Absent outcome monitoring** — no ongoing measurement of determination accuracy against realised clinical outcomes | **"Accountable for accuracy"** under SB 1120 |

### Part V — Operational and data integrity
| # | Failure mode | Hook |
|---|---|---|
| 5.1 | **Turnaround-clock breach** induced by the AI pathway (queueing, escalation loops, pended states) | Statutory UM timeframes; penalties are per-violation |
| 5.2 | **PHI minimum-necessary breach** in the AI pipeline, including third-party inference and retention | HIPAA |
| 5.3 | **Degradation without detection** — no monitoring for accuracy decay after deployment | AIS Program |
| 5.4 | **Absent failure-mode inventory and incident process** for the system itself | AIS Program |

### Scoring
Per clause: **Conformant / Conformant with observations / Deficient / Materially deficient**, each requiring named evidence. Plus a **Reconstructability Index** (can N randomly selected determinations be fully rebuilt from retained artefacts — expressed as a fraction) and a **Human Authority Index** (concordance rate, median review duration, documented-independent-reasoning rate, override rate).

`[INFERENCE]` Those two indices are the commercial core. They are single numbers a general counsel can carry into a board meeting and an underwriter can put in a rating schedule. Everything else in ADR-1 is supporting structure. Design them to be comparable across plans from engagement one, because comparability is what eventually makes them a rating input rather than a report finding.

---

## 5. Target list construction (all public, all free)

**Vendors (target 25).** The named field — Cohere Health, Availity, Optum/Change, CoverMyMeds, Anterior, Latent Health, Humata Health — plus the next tier found through: health-plan press releases announcing AI UM deployments; HLTH/AHIP/ViVE exhibitor lists; Elion and similar health-tech directories; CMS-0057 readiness marketing. For each, record: payer logos claimed, funding stage, whether they publish any validation evidence.

**Payers (target 35).** Prioritise in this order `[INFERENCE]`:
1. **Regional and provider-sponsored plans in SB 1120 California and the 25 NAIC-adopting states** — the mandate is live, and they lack the in-house model-risk function a BUCA has.
2. **Medicaid MCOs** — state contract oversight adds a second forcing function.
3. **Medicare Advantage plans with post-acute exposure** — nH Predict is *their* fact pattern. This is the most acute population in the country.
4. BUCA subsidiaries and new MA entrants — slower, larger, approach after you have three references.

**Public sources for names and triggers:** state DOI company filings and market-conduct examination reports (examiner findings tell you precisely what a regulator is looking at); California DMHC filings and enforcement actions; NAIC listings; CMS MA contract and star-ratings data; plan appeal-and-grievance public reporting; vendor customer announcements.

**Roles, in priority order:** Chief Risk Officer · General Counsel / Deputy GC for regulatory · Chief Compliance Officer · Chief Medical Officer / VP Utilization Management · Head of Model Risk or AI Governance (increasingly exists post-NAIC) · VP Internal Audit.

`[INFERENCE]` Lead with **General Counsel at MA plans with post-acute exposure.** They have read about the March 2026 discovery order, they are the one person who cannot delegate the question, and they control a budget that does not require a business case — legal spend is defensive by nature.

---

## 6. Outreach

### Sequencing
60 contacts → ~20 conversations → ~6 scoping discussions → 3 signed `[FORECAST]`. Assumes a ~33% response rate on a credible first-touch to a named role with a specific artefact attached, which is achievable because the message carries a free document and no ask beyond 25 minutes.

### Vendor first-touch
> Subject: independent assessment — the question your payer prospects are about to ask
>
> I've published ADR-1, a free taxonomy of the ways AI determination systems fail in utilization review — 22 failure modes, each mapped to SB 1120, the NAIC AI bulletin, or the nH Predict and PxDx pleadings. [link]
>
> I'm writing because plans in the 25 states that adopted the NAIC bulletin now have to evidence oversight of third-party AI they remain responsible for. In practice that lands on you as a security-questionnaire-shaped problem that no SOC 2 answers.
>
> Not selling you software. I do independent three-week assessments against ADR-1 that you can hand to a prospect's risk committee.
>
> Worth 25 minutes? I'd also just like to know which of the 22 modes your payer reviews are actually catching — I'm revising v1.1 from real engagements.

### Payer first-touch (General Counsel)
> Subject: reconstructing an AI-assisted determination after the fact
>
> In March a magistrate ordered UnitedHealth to produce how nH Predict was built, who sat on its AI review board, and what savings it achieved. Whatever that case does, it established the question: can a plan reconstruct a specific AI-assisted determination, and show a qualified human genuinely decided it?
>
> I've published ADR-1, a free taxonomy of 22 failure modes in AI determination systems, mapped to SB 1120, the NAIC bulletin and the pleadings in the pending class actions. [link]
>
> Two of its measures are the ones I'd expect to matter most to you: a Reconstructability Index (what fraction of sampled determinations can be fully rebuilt from retained artefacts) and a Human Authority Index (concordance, review duration, documented independent reasoning, override rate).
>
> I do independent assessments producing both. Before pitching anything, I'd value 25 minutes on whether these are the right two measures.

`[INFERENCE]` Both messages lead with a free artefact and a genuine question, and both make the ask a conversation rather than a meeting-about-buying. This works for a reason that matters: you are not yet credible as a vendor, but you are immediately credible as the author of a specific document. Lead with the document.

### The one question that qualifies
> *"If a regulator or a plaintiff asked you to reconstruct a specific AI-assisted determination from eight months ago — the inputs, the criteria version, the model version, and who actually decided — could you?"*

`[INFERENCE]` Nearly everyone says no, or says yes and then qualifies it. Either answer opens the engagement, and the question costs nothing to ask. Track the answers: the distribution is itself publishable data.

---

## 7. The engagement

### 7.1 Three tiers
| Tier | Scope | Duration | Fee | Buyer |
|---|---|---|---|---|
| **T1 — Readiness Review** | Documentary assessment against ADR-1, no determination re-run. Gap list + remediation priorities | 2 weeks | **$18,000** | Vendors; first-time payers |
| **T2 — Independent Determination Review** | Full ADR-1 assessment incl. 300–500 held-out determination re-run, both indices, signed opinion | 3 weeks | **$38,000** | Payers. **The core product** |
| **T3 — AIS Program Attestation + Surveillance** | T2 plus quarterly surveillance, annual re-attestation, exam-support | 3 wks + 12 mo | **$65,000** + **$30,000/yr** | Payers post-T2. **The recurring product** |

### 7.2 Why these prices
`[INFERENCE]` Anchored between two observable references. Above: Big Four AI-risk engagements at **$250k–$1M**, and healthcare actuarial consulting billed at partner hourly rates (Milliman, WTW) where a scoped model-validation engagement runs well into six figures. Below: nothing credible exists — and the NYC LL 144 experience (§1.4) shows what happens when a mandated audit commoditises, which is the floor to stay away from. $38k is deliberately set just under the threshold where most plans require competitive procurement, which is the difference between a three-week and a three-quarter sales cycle. **Never discount below $15k.** Price is a credibility signal in assurance; a cheap independent opinion is a contradiction in terms.

### 7.3 The deliverable
1. Scope and independence statement (what was and was not assessed; your independence from vendor and plan)
2. **Reconstructability Index** and **Human Authority Index**, with method
3. Clause-by-clause ADR-1 findings with evidence cited
4. Determination re-run results: disagreement rate, disagreement characterisation, severity-banded exposure
5. Disparity analysis
6. Prioritised remediation, each item mapped to its regulatory hook
7. **Residual risk statement** — carefully scoped (§13)
8. Clinical sign-off by a licensed reviewer

### 7.4 Contract terms that matter more than the fee
- **Data clause** — your right to retain findings and use anonymised, aggregated data. **Non-negotiable.** Walk from an engagement that refuses it; it is the only asset that compounds.
- 50% deposit; balance on delivery.
- Fixed scope, change-order for expansion.
- Opinion scoping: assessment as of a date, on a defined system boundary, based on evidence provided. Not a guarantee or a certification of future performance.
- Right to be named as assessor only with written consent; right to decline to be named.

---

## 8. Unit economics and 120-day financials

### Per T2 engagement
| | |
|---|---|
| Fee | $38,000 |
| Clinical reviewer (contract, ~20 hrs) | ($4,500) |
| Your time | ~90 hours |
| **Contribution** | **~$33,500** |
| Cash cost to deliver before first invoice | **$0** (deposit precedes clinician engagement) |

`[INFERENCE]` The deposit-before-contractor sequencing is what makes this a genuinely $0 business rather than a $0 business that needs $20k of working capital in month two. Honour it strictly: never engage the clinician before the deposit clears.

### 120-day base case `[FORECAST]`
| | Base | Downside | Upside |
|---|---|---|---|
| Engagements signed | 3 | 1 | 6 |
| Mix | 1×T1, 2×T2 | 1×T1 | 2×T1, 3×T2, 1×T3 |
| Booked | $94,000 | $18,000 | $215,000 |
| Collected by Day 120 | ~$66,000 | $18,000 | ~$150,000 |
| Contractor cost | ($9,000) | $0 | ($22,500) |
| Entity + E&O + tooling | ($12,000) | ($4,000) | ($14,000) |
| **Net cash, Day 120** | **~$45,000** | **~$14,000** | **~$113,000** |
| Loss observations logged | 120–200 | 40 | 300+ |
| Outside capital | **$0** | **$0** | **$0** |

Downside is Gate B failure: one engagement from 30+ conversations means the problem is real but not yet purchasable, and the honest response is to stop rather than to persist on conviction.

---

## 9. Asset 3 — the loss schema

Design it on Day 1 and never log an engagement outside it. This is the dossier's entire moat in embryo.

**Per observation:**
`observation_id` · `engagement_id` · `adr1_clause` · `determination_type` (prior auth / concurrent / post-service / appeal) · `line_of_business` (MA / Medicaid / commercial / ACA) · `vendor_system` (coded, confidential) · `human_authority_pattern` · `detected_by` (re-run / documentary / log / interview) · `monetised_severity_estimate` · `severity_basis` · `appeal_overturn_observed` (bool) · `regulatory_hook` · `remediated_at_followup` (bool) · `observation_date`

**Per engagement:** organisation type · state(s) · enrollment band · determination volume band · Reconstructability Index · Human Authority Index · disparity findings · clause-level scores · remediation accepted (bool).

**Per quarter:** frequency and severity distribution by clause, by LOB, by vendor system; remediation effectiveness; emerging modes for the next ADR-1 version.

`[INFERENCE]` The `monetised_severity_estimate` and `severity_basis` fields are the two that make this an actuarial asset rather than an audit file. They are also the hardest to populate and the ones most likely to be skipped under delivery pressure. Populate them even when the estimate is a wide band with a stated method — a defensible range beats a blank, and Gate C depends on this field existing across ≥40 observations.

---

## 10. The capacity track (Days 75–120)

Runs in parallel and is the step most founders would defer. Do not defer it: it is what separates this from a consultancy, and the conversation takes two years to mature, so it must start now.

**Who to approach**
1. **Managed-care E&O and medical professional liability underwriters** — they already write the adjacent exposure for these exact plans and are already being asked about AI at renewal.
2. **Specialty MGAs and program managers** in healthcare liability — fastest-moving, most likely to delegate, and the realistic source of your first binding authority.
3. **Lloyd's managing agents** writing healthcare liability or tech E&O — the coverholder route the dossier identifies (§9.3, rung 4).
4. **Reinsurer innovation teams** (Munich Re, Swiss Re) — slowest, but they are the ones building AI performance products and will read loss data seriously.

**The pitch, which is not a pitch**
> I'm not asking for capacity. I have severity-distributed loss observations on AI determination systems inside health plans — the first structured set I'm aware of. You're being asked about this exposure at renewal and you have no loss data. I'd like to show you mine and hear what you'd need before you'd price it.

`[INFERENCE]` This inverts the normal dynamic. A founder asking an underwriter for capacity is one of hundreds. A founder bringing an underwriter proprietary loss data in a class they are being questioned about is rare enough to get a second meeting, and the second meeting is the Day 120 objective. Do not ask for an appointment in the first meeting; you will get a no that is hard to reopen.

**Products to have drafted by Day 120** (not to sell yet):
- **Vendor performance warranty** — AI UM vendor warrants a determination-accuracy or overturn-rate threshold; cover responds on breach. Buyer: the vendor, as a sales instrument. This is the easier first product because it is a defined, measurable, short-tail trigger.
- **Determination integrity cover** — responds to defence costs and regulatory penalties arising from AI-assisted determination failures, conditional on ADR-1 attestation and continuous surveillance. Buyer: the plan. Larger, longer-tail, and the real prize.

---

## 11. Metrics

**Weekly:** contacts initiated · conversations held · scoping requests received · proposals out · signed · cash collected · observations logged · ADR-1 citations observed.

**The four that actually predict the outcome** `[INFERENCE]`:
1. **Unsolicited scoping requests.** The only unfakeable demand signal. Everything else can be manufactured by effort.
2. **Median monetised severity** across observations. Gate C; determines whether any insurance product is possible at all.
3. **Repeat and referral rate.** Distinguishes a product from a favour.
4. **External ADR-1 citations** — in an RFP, a policy document, a vendor's marketing, a law-firm client alert. The leading indicator of the standard becoming infrastructure, and the first one is worth more than the next $50k of revenue.

---

## 12. Budget

**Days 1–30: $0.** Primary sources, public filings, free hosting, your own outreach. Nothing required.

**From first deposit:** LLC/PC formation ($500–1,500) · professional liability (E&O) — bind before delivering the *second* engagement, ~$3,000–8,000/yr for early limits · clinical contractor per engagement · minimal tooling (<$200/mo).

**Do not spend on, before Day 120:** software development, design, conferences, PR, paid acquisition, or a second full-time person.

---

## 13. Legal and risk hygiene

`[INFERENCE]` You are entering the business of giving opinions about systems that make consequential medical decisions. The hygiene is not optional and three items are genuinely load-bearing:

1. **E&O before the second engagement.** The first can be delivered uninsured with carefully scoped language; do not make a habit of it. You will later ask underwriters for capacity — being uninsured yourself is disqualifying.
2. **Opinion scoping.** Assessment *as of a date*, on a *defined system boundary*, based on *evidence provided by the client*. Never certify future performance; never state that a system is compliant with a statute — state that specified evidence was or was not present for specified clauses. This distinction is what keeps you an assessor rather than a guarantor.
3. **Independence policy, published.** You may not assess a system you helped build, configure or select. Write this down publicly before anyone offers you remediation work, because the offer will come, it will be lucrative, and accepting it destroys the asset. `[FACT]` The LL 144 independence requirement — auditor may be neither vendor nor employer — is the codified version of this, and the issuer-pays conflict that discredited credit ratings in 2008 is what happens when it erodes.
4. **Conflict firewall for the insurance leg.** You will eventually certify and underwrite the same systems. Separate legal entities, published methodology, and surveillance independent of the underwriting P&L, designed in now rather than retrofitted under scrutiny.
5. **PHI.** Assess on de-identified or limited data sets where possible; BAA where not. Do not take custody of PHI you do not need.

---

## 14. What not to do

`[INFERENCE]` Each of these is a real temptation at a specific point in the 120 days, and each is the failure mode it maps to in the dossier.

| Don't | Why |
|---|---|
| Build software | §18.5 services trap in reverse — premature product spends the only resource you have (time) on the asset that matters least |
| Take remediation work from an assessment client | Destroys independence, which is the entire product |
| Raise capital before Gate B | Converts an honest test into a commitment you must defend |
| Broaden to "AI governance" | The specificity is the credibility. A general AI-governance consultant is indistinguishable from a thousand others |
| Compete with AIUC/Armilla head-on | They hold the general-purpose slot (dossier §10.1). Depth in one regulated vertical is the available position |
| Sell a certification before you have loss data | The attestation is worth what the data behind it is worth. Certifying early and thinly is the LL 144 outcome |
| Anchor on the NAIC mandate as the reason to buy | §1.4. Mandates without enforcement commoditise. Sell litigation defensibility and exam readiness |
| Skip the `monetised_severity_estimate` field under deadline pressure | It is the field Gate C depends on and the field that makes the data actuarial |

---

## 15. Day 121 decision tree

| Condition at Day 120 | Read | Action |
|---|---|---|
| ≥3 paid · ≥1 repeat/referral · underwriter in 2nd meeting · median severity >$5k | Thesis intact at the wedge | Proceed. Next 120 days: convert 2+ to T3 surveillance, publish ADR-2 extending to P&C claims decisioning, pursue binding authority. Still no outside capital |
| ≥3 paid · severity median <$5k | Assurance business real, insurance leg not | Build the certification business deliberately; defer the insurance leg. Realistic ceiling ~$1–4B (the Vanta comparable). A good outcome, honestly stated |
| 2 paid · strong pipeline · no underwriter traction | Demand real, capacity premature | Continue 90 days. Capacity conversations mature over years; do not read early silence as refusal |
| ≤1 paid from 30+ qualified conversations | **Dossier falsification test 2 has fired** | **Stop.** Do not persist on conviction. Either the vertical is wrong (re-run §1.5 with a different vertical, reusing every asset) or the thesis is wrong at the wedge. The 120 days cost you time and ~$0, which was the point |
| 0 paid, but ADR-1 cited externally | Standing without revenue | Diagnose: is it pricing, buyer role, or scope? Re-test for 60 days with a $12k T0 diagnostic before concluding. Citation without revenue usually means you are reaching the wrong role, not that the problem is unfelt |

---

## 16. The first three things, concretely

Everything above reduces to this. The first action is executable today, at $0.

1. **Today:** download and read the nH Predict and PxDx complaints, the March 2026 discovery order, SB 1120, and the NAIC Model Bulletin. Free. That is the domain.
2. **This week:** list 25 payer-side AI UM vendors and 35 plans in SB 1120 California and the 25 NAIC-adopting states, with a named General Counsel or Chief Risk Officer for each. Public sources only.
3. **Within 21 days:** publish ADR-1 and send the first 20 messages, each carrying the free taxonomy and the single qualifying question — *can you reconstruct a specific AI-assisted determination from eight months ago, and show who actually decided it?*

Gate B resolves by Day 90. If it fails, you will have learned that for the price of three months and nothing else — which is the strongest argument for starting.
