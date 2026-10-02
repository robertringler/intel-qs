# ADR-1 — Assessment of AI Determination Systems in Utilization Management and Claims Adjudication

**Version:** 1.0
**Published:** 2 October 2026
**Status:** Published for use. Open for comment through 31 January 2027; comments inform v1.1.
**Maintainer:** ⟨MAINTAINER⟩ *(replace with publishing entity before release)*
**Licence:** Creative Commons Attribution 4.0 International (CC BY 4.0). You may copy, quote, adapt and build on this document, including commercially, with attribution.

**How to cite:** ⟨MAINTAINER⟩, *ADR-1: Assessment of AI Determination Systems*, v1.0 (2 October 2026). Cite individual failure modes by their stable identifier, e.g. **ADR-1.B1**. Cite document sections as **ADR-1 v1.0 §7.3**.

**Stable identifiers:** failure-mode identifiers (A1–E4) will not be reused or renumbered across versions. A mode that is withdrawn is marked withdrawn and its identifier retired.

---

## Foreword — why this document is free

This document is published at no cost, with no registration, under a licence permitting commercial reuse, because a taxonomy's usefulness depends on being cited, and nothing behind a paywall gets cited. Anyone may use it: health plans assessing themselves, vendors preparing for review, regulators framing examination questions, auditors structuring engagements, and attorneys framing discovery.

What is not free, and cannot be, is an **independent assessment opinion** rendered against it. That requires an assessor who is independent of both the system's developer and its deployer (§4), and it is an opinion, not a document that can be copied.

The distinction matters for a reason beyond commerce. A standard that its author monetises by restricting access has an incentive to stay complex and proprietary. A standard its author monetises by assessing against it has an incentive to stay clear, testable and widely adopted. The second incentive produces better standards. This document is published under the second.

---

## 1. Scope and purpose

### 1.1 Purpose
ADR-1 provides a structured taxonomy of failure modes, an assessment method, and two comparable indices for **AI systems that participate in determinations of medical necessity, coverage, or claim disposition**.

It exists because these systems have become consequential faster than any means of establishing whether they work. Three facts frame the need:

- In March 2026 a United States magistrate judge ordered a health insurer to produce how its post-acute determination model was built, whether it was designed to replace physicians, who sat on its internal AI review board, and what cost savings it achieved. The question *"can you reconstruct a specific AI-assisted determination, and show who actually decided it?"* is now a question that may have to be answered under oath.
- California's **SB 1120** (effective 1 January 2025) requires that a licensed physician or qualified health professional make the final medical-necessity determination where AI is used in utilization review, that the determination rest on the enrollee's own clinical circumstances rather than a group dataset alone, and that plans remain accountable for accuracy.
- The **NAIC Model Bulletin on the Use of Artificial Intelligence Systems by Insurers**, adopted in a substantial majority of US jurisdictions, requires a written AI Systems ("AIS") Program including model validation, testing for bias and errors, and oversight of third-party AI systems for which the insurer remains fully responsible.

None of these supplies a method. ADR-1 supplies a method.

### 1.2 Systems in scope
Any system using machine learning, large language models, rules engines, predictive models, or statistical classifiers that:
- (a) produces a recommendation, score, prediction, classification or draft determination that is used in deciding medical necessity, coverage, level of care, length of stay, or claim disposition; **or**
- (b) selects, routes, prioritises or pends such cases in a manner that affects their disposition or timeliness; **or**
- (c) retrieves, summarises or characterises clinical information presented to a human reviewer for such a decision.

**Clause (c) is deliberately broad.** A system that only summarises a medical record for a reviewer is in scope, because a determination made on a defective summary is a determination made on a defective record, and the summarisation step is frequently excluded from governance on the grounds that it is "not decisioning." That exclusion is itself a finding (see **ADR-1.A3**).

### 1.3 Determination types in scope
Prior authorization · concurrent review · continued-stay review · retrospective and post-service review · level-of-care determination · claim adjudication and payment-integrity denial · appeal and grievance determination.

### 1.4 Out of scope
Provider-side administrative automation with no payer determination effect; clinical decision support directed at treating clinicians; eligibility and enrollment determinations; fraud investigation referrals that do not themselves deny a claim; pricing and rating. Some of these may be in scope of a future ADR document; they are not in scope of ADR-1 and must not be described as assessed under it.

### 1.5 Who may use this document
Anyone. Self-assessment, vendor pre-assessment, internal audit and regulatory examination use are all permitted and encouraged. **Only an assessment meeting §4 may be described as an independent ADR-1 assessment.** Self-assessment must be described as self-assessment (§10.6).

---

## 2. What this document is not

2.1 **Not legal advice.** The regulatory mappings in §11 and in each failure mode are informational, describe obligations in general terms, and may be incomplete or superseded. Verify against current statutory and regulatory text in the applicable jurisdiction.

2.2 **Not a certification of legal or regulatory compliance.** An ADR-1 assessment reports whether specified evidence was present for specified clauses as of a date. It does not determine compliance with any statute, rule or contract. Any assessor or deployer describing an ADR-1 result as establishing compliance is misusing this document.

2.3 **Not a guarantee of future performance.** Findings are as of the assessment date, on the defined system boundary, based on the evidence obtained.

2.4 **Not a model-performance benchmark.** ADR-1 does not rank systems by accuracy. Two systems with identical accuracy may score very differently, because the subject is the *determination process* and its evidentiary integrity, not the model in isolation.

2.5 **Not a substitute for clinical judgement.** Where an assessment requires a clinical opinion, it requires a qualified clinician (§4.4).

2.6 **Not an accreditation programme.** There is no registry, no accredited-assessor list, and no mark. v1.0 deliberately omits these. A conformity-assessment scheme requires governance this document does not yet have, and premature marks degrade into unverified badges.

---

## 3. Terms and definitions

**3.1 AI determination system (ADS)** — a system within §1.2.

**3.2 Determination** — a decision on medical necessity, coverage, level of care, length of stay, or claim disposition, communicated to an enrollee, provider, or both.

**3.3 Adverse determination** — a determination denying, delaying, reducing, modifying or terminating a requested or ongoing service or payment, in whole or in part.

**3.4 Reviewer** — the natural person recorded as making or approving a determination.

**3.5 Effective authority** — the locus of actual decisional control, as distinct from recorded authority. Where a reviewer's recorded decision is not supported by evidence of independent consideration, effective authority rests with the system. See **ADR-1.B1**.

**3.6 Retained artefact** — any record persisted by the deployer or its vendor that evidences an element of a determination: inputs, system and model versions, criteria version and content, system outputs, reviewer identity and credentials, reviewer actions with timestamps, notices issued.

**3.7 Reconstruction** — independent rebuilding of a determination from retained artefacts alone, without recourse to the memory of participants or to re-execution of the system. See §8.1.

**3.8 Criteria set** — the clinical guidelines, coverage policies, medical policies or decision rules applied, identified by name **and version**.

**3.9 System boundary** — the explicitly enumerated components, interfaces, data flows, criteria sets, human workflow steps and determination types within the assessment's scope (§5.2).

**3.10 Assessment period** — the historical period from which the determination population is drawn (§5.4).

**3.11 Deployer** — the entity making determinations, typically a health plan or its delegate. **Developer** — the entity that built the system, which may be the deployer, a vendor, or both.

---

## 4. Assessor independence

**These requirements are mandatory.** An assessment not meeting them is not an independent ADR-1 assessment.

**4.1** The assessor must not have developed, configured, selected, implemented, tuned or operated the system under assessment, nor advised on its procurement.

**4.2** The assessor must not be employed by, controlled by, or under common control with either the developer or the deployer.

**4.3** The assessor must not provide remediation services for findings it has issued on the same system, for twelve months following the assessment, unless the remediation is performed by a party the assessor does not control and the assessor does not reassess the remediated system. **Rationale:** an assessor who sells the fix for the findings it issues has an incentive to find them. This is the conflict that discredited structured-finance credit ratings and it is not a theoretical risk.

**4.4** Where an assessment includes clinical determination review (§8.3, Parts A and D), a clinician licensed and in good standing, with specialty standing appropriate to the determinations reviewed, must perform or supervise that review and be identified in the report.

**4.5** Compensation must not be contingent on the findings, the indices, or any outcome of the assessment.

**4.6** The assessor must disclose in the report every prior and current commercial relationship with the developer and the deployer in the preceding 24 months, including relationships of affiliates.

**4.7** The assessor must publish and maintain an independence policy consistent with §4.1–4.6.

---

## 5. Assessment method

### 5.1 Overview
An ADR-1 assessment comprises: scope definition (§5.2) → evidence request (§5.3) → population definition and sampling (§5.4) → clause assessment (§6, §7) → index computation (§8) → reporting (§10).

### 5.2 Defining the system boundary
The assessor must document, and the deployer must confirm in writing:
- (a) each system component in scope, with version identifiers;
- (b) each determination type and line of business in scope;
- (c) each criteria set in scope, by name and version;
- (d) each human workflow step in scope;
- (e) the interfaces between in-scope and out-of-scope components;
- (f) each component the deployer asserts is out of scope, **with the asserted basis**.

**5.2.1** Clause (f) is mandatory and is assessed, not merely recorded. An exclusion asserted on the basis that a component "does not make determinations" is tested against §1.2(b) and §1.2(c). Unsupported exclusions are a finding under **ADR-1.A3**.

### 5.3 Evidence request
The assessor must request, at minimum, the items in **Annex A**. The deployer's response — including non-production — is part of the evidence.

**5.3.1 Non-production is a finding, not an exclusion.** Where evidence necessary to assess a clause is not produced, the clause is scored **Deficient** or **Materially deficient** under §7, and the non-production is reported under §10.4. It must **never** be reported as "not assessed," "not applicable," or "unable to determine." *Rationale: the ability to produce evidence of a determination is itself the subject of Part C. Treating absent evidence as an assessment limitation rather than a finding would allow the most serious deficiency this document addresses to be scored as neutral.*

### 5.4 Population and sampling

**5.4.1 Assessment period.** Not less than the twelve months preceding the assessment, or the full operational life of the system if shorter.

**5.4.2 Complete population listing.** The deployer must provide a complete listing of all determinations in scope for the assessment period, with a record count reconciled to an independent operational or financial control total. **The assessor draws the sample. A sample supplied by the deployer, or drawn from a listing that is not reconciled, invalidates the indices in §8** and must be reported as such.

**5.4.3 Sample size.** For the Reconstructability Index:

| Sample size *n* | Worst-case 95% CI half-width | Use |
|---|---|---|
| 300 | ±5.7% | **Minimum** for a reported RI |
| 385 | ±5.0% | **Recommended** |
| 600 | ±4.0% | Where RI will inform underwriting or remediation sign-off |

Half-widths are for a binomial proportion at *p* = 0.5 (worst case); precision improves as RI approaches 0 or 1. An RI reported on *n* < 300 must be labelled **indicative** and must not be presented as comparable.

**5.4.4 Stratification.** Stratify by (a) determination type, (b) line of business, (c) **adverse versus favourable outcome**, and (d) calendar quarter.

**5.4.5 Deliberate oversampling of adverse determinations.** Adverse determinations must be oversampled to at least 50% of the sample regardless of their population share. Both **unweighted** (sample) and **population-weighted** indices must be reported (§8.1.4). *Rationale: adverse determinations carry essentially all of the severity, and a proportionate sample of a population with a 6% denial rate would contain too few to characterise.*

**5.4.6 Selection method.** Random or systematic selection from the reconciled listing using a documented, reproducible method with a recorded seed. The method and seed must appear in the report.

**5.4.7 No substitution.** A selected determination that cannot be reconstructed is a **failure** under §8.1 and must not be replaced. Replacement of unreconstructable items invalidates the RI.

### 5.5 Mandatory disclosures
The report must disclose: evidence requested and not produced; any deployer restriction on scope, sampling or access; any population segment excluded and why; whether the assessor had access to system outputs and version identifiers or relied on deployer representation; and any clause assessed on representation alone.

---

## 6. The failure-mode taxonomy

Twenty-two failure modes in five parts. Each states a **definition**, **indicators** (observable signals), **evidence** (what is needed to assess it), a **typical severity** band (§9), and a **regulatory hook** (informational; see §2.1).

---

### Part A — Decision integrity
*Whether the determination is substantively sound.*

#### ADR-1.A1 — Group-data substitution
**Definition.** The determination is driven by a cohort-level, benchmark or actuarial prediction of expected course rather than by the individual enrollee's clinical circumstances.
**Indicators.** System output expressed as a predicted length of stay, expected discharge date or expected utilisation derived from a comparison population; determinations clustering tightly on predicted values; reviewer records citing the prediction rather than enrollee-specific findings; absence of a documented step requiring consideration of individual variance from the prediction.
**Evidence.** System design documentation; feature inventory; output schema; 25+ reviewer records on adverse determinations; criteria application records.
**Typical severity.** S4–S5.
**Hook.** California SB 1120 (determination must rest on the enrollee's own clinical circumstances, not a group dataset alone); medical-necessity standards generally; the central allegation in pending US class actions concerning post-acute determination models.

#### ADR-1.A2 — Criteria misapplication
**Definition.** The applied criteria set is the wrong one, the wrong version, inapplicable to the line of business or benefit, or applied more restrictively than the criteria or filed policy permits.
**Indicators.** Criteria version not recorded on determinations; criteria version in the system inconsistent with the version filed or published; commercial criteria applied to a line of business requiring statutory or programme criteria; configured thresholds more restrictive than the criteria text; local coverage rules not reflected.
**Evidence.** Criteria configuration export with versions; filed or published policy documents; configuration change log; 25+ determinations traced from criteria text to configured logic to outcome.
**Typical severity.** S3–S5.
**Hook.** Medicare Advantage utilization-management and coverage-criteria requirements; state utilization review statutes; filed-policy accountability including SB 1120's filing requirement.

#### ADR-1.A3 — Incomplete clinical picture
**Definition.** A determination is rendered on partially retrieved, partially parsed or partially summarised clinical information, without the gap being detected, flagged to the reviewer, or recorded.
**Indicators.** No completeness check between source records and the information presented; summarisation or extraction components excluded from the governed boundary (see §5.2.1); no mechanism for the reviewer to see what was omitted; retrieval failures logged as successes; truncation at a context or page limit without notice.
**Evidence.** Retrieval and extraction architecture; completeness controls; 25+ cases compared source record against presented information; reviewer interface walkthrough; error logs.
**Typical severity.** S3–S4.
**Hook.** Medical-necessity standards; appeal-overturn and bad-faith exposure; NAIC AIS Program risk controls.

#### ADR-1.A4 — Scope excursion
**Definition.** The system is used for a determination type, benefit, population, line of business or jurisdiction for which it was not validated.
**Indicators.** Validation documentation narrower than observed production use; no technical control restricting use to validated scope; expansion to a new line of business or determination type without revalidation; use in a jurisdiction with materially different requirements.
**Evidence.** Validation reports with stated scope; production usage data by determination type, line of business and jurisdiction; access and routing configuration; change records.
**Typical severity.** S3–S5.
**Hook.** NAIC AIS Program validation and risk-control requirements; state utilization review requirements.

#### ADR-1.A5 — Configuration and model drift without revalidation
**Definition.** Models, prompts, thresholds, criteria mappings or routing rules change in production without change control, impact assessment or revalidation.
**Indicators.** No change log, or a log without approvals; prompt or threshold edits outside release control; vendor-side model updates not notified or not assessed; no pre/post comparison on determination outcomes; no contractual right to notice of vendor model change.
**Evidence.** Change management records for the assessment period; release approvals; pre/post outcome analyses; vendor contract change-notification clauses; version history.
**Typical severity.** S3–S4.
**Hook.** NAIC AIS Program risk controls and third-party oversight; SB 1120 accountability for accuracy.

---

### Part B — Human authority
*Whether a qualified person actually decided. The highest-severity cluster.*

#### ADR-1.B1 — Ratification rather than decision
**Definition.** A qualified reviewer is recorded as the decision-maker, but **effective authority** (§3.5) rests with the system: the recorded decision is not supported by evidence of independent consideration of the individual case.
**Indicators.** Concordance between system recommendation and final determination at or near 100%, particularly asymmetric between adverse and favourable outcomes; median effective review duration shorter than the time required to read the material presented; reviewer records that are templated, system-derived, or contain no case-specific reasoning; override mechanisms absent, buried, or requiring justification not required to concur; production targets implying per-case times below the plausible floor; reviewer interviews describing concurrence as the default.
**Evidence.** Determination-level concordance data; reviewer action timestamps (case opened, material viewed, determination recorded); 50+ reviewer records on adverse determinations; workflow walkthrough; reviewer interviews (minimum 3, conducted without management present); productivity standards and incentive arrangements.
**Typical severity.** **S5.**
**Hook.** California SB 1120 (physician must make the final determination; services may not be denied, delayed or modified based solely on an AI algorithm); state utilization review physician-review requirements; the central allegation in pending US class actions, one of which concerns an alleged average review time of approximately 1.2 seconds per claim.

> **Assessor note.** B1 is the mode most likely to be contested and most consequential when present. It must be assessed on **measured behaviour**, never on policy documents. A policy stating that physicians make determinations is not evidence that they do; it is evidence of what the deployer intends. Where B1 is found, the report must present the measured basis (concordance, duration distribution, independent-reasoning rate) rather than a conclusion.

#### ADR-1.B2 — Reviewer qualification mismatch
**Definition.** The reviewer lacks the licensure, specialty standing or jurisdictional authority the determination requires.
**Indicators.** Determinations requiring specialty review decided by a generalist; licensure not verified or not current for the enrollee's jurisdiction; non-clinical staff recorded on determinations requiring clinical judgement; no routing control matching case specialty to reviewer specialty.
**Evidence.** Reviewer roster with licensure and specialty, verified against primary sources for a sample; routing rules; 25+ determinations matched to reviewer credentials.
**Typical severity.** S4–S5.
**Hook.** State utilization review reviewer-qualification requirements; Medicare Advantage requirements; SB 1120 (licensed physician or qualified health professional).

#### ADR-1.B3 — Appeal-loop contamination
**Definition.** The same system, model, configuration or criteria logic that produced a determination materially informs the review of its appeal; or the appeal reviewer is not independent of the initial reviewer.
**Indicators.** Appeal workflow invoking the same system without a documented independence control; appeal reviewer seeing the original system output before forming a view; no control preventing the initial reviewer from deciding the appeal; appeal-overturn rates implausibly low relative to peers.
**Evidence.** Appeal workflow definition; system invocation logs for appeals; reviewer assignment records; appeal-overturn rates by determination type; 15+ appeal records.
**Typical severity.** S4–S5.
**Hook.** Independent-review and appeal-independence requirements under state and federal utilization review regimes; ERISA claims-procedure requirements where applicable; basic adjudicative fairness.

#### ADR-1.B4 — Override suppression
**Definition.** Reviewer disagreement with the system is discouraged, made difficult, penalised, or not durably recorded.
**Indicators.** Override requiring free-text justification where concurrence requires none; override rates near zero; overrides not persisted as structured data; reviewer performance metrics that penalise deviation or reward throughput; interviews describing informal discouragement; no escalation path for systematic disagreement.
**Evidence.** Workflow walkthrough timed for both paths; override data; reviewer performance and incentive documentation; reviewer interviews; audit-log schema.
**Typical severity.** S4.
**Hook.** NAIC AIS Program governance and human-oversight expectations; SB 1120; evidence of institutional knowledge relevant to extracontractual exposure.

---

### Part C — Reconstructability
*Whether the determination can be proven after the fact. The discovery cluster.*

#### ADR-1.C1 — Non-reconstructable determination
**Definition.** A determination cannot be independently rebuilt from retained artefacts alone (§8.1).
**Indicators.** Inputs not retained as presented; model or system version not recorded per determination; criteria version not recorded; system output not persisted; reviewer actions not timestamped or not sequenced; reconstruction requiring participant recollection or system re-execution.
**Evidence.** Attempted reconstruction of the §5.4 sample. This mode is assessed by direct test, not by documentation review.
**Typical severity.** **S5.**
**Hook.** Litigation discovery obligations — a US court has compelled production of exactly these elements; regulatory examination; NAIC AIS Program documentation requirements.

#### ADR-1.C2 — Inadequate adverse-determination rationale
**Definition.** The rationale communicated to the enrollee or provider does not state a reason sufficient to permit meaningful appeal, or does not reflect the actual basis of the determination.
**Indicators.** Template rationales not case-specific; rationale citing criteria not actually applied; rationale omitting the clinical basis; divergence between internal basis and communicated basis; rationale not identifying the criteria set and version.
**Evidence.** 30+ adverse determination notices compared against internal determination records and criteria applied.
**Typical severity.** S3–S4.
**Hook.** Adverse-determination notice content requirements under state utilization review law, Medicare Advantage rules, and ERISA claims procedures where applicable.

#### ADR-1.C3 — Audit-log insufficiency
**Definition.** Logs lack the identity, timestamp, version, sequence or integrity properties needed to establish who decided what, when, on what basis.
**Indicators.** Actions not attributed to identified natural persons; timestamps at insufficient granularity or without timezone; no immutability or tamper-evidence; logs retained for less than the determination record; vendor-side actions not logged to the deployer; service accounts masking human identity; no link between reviewer action and determination record.
**Evidence.** Log schema and samples; retention configuration; integrity controls; attempted end-to-end trace for 25+ determinations; vendor log access terms.
**Typical severity.** S4–S5.
**Hook.** NAIC AIS Program documentation; evidentiary admissibility and authentication; regulatory examination.

#### ADR-1.C4 — Third-party opacity
**Definition.** The deployer cannot evidence oversight of a vendor system for which it remains fully responsible.
**Indicators.** No contractual right to audit, to model documentation, to validation evidence, to change notification, or to logs; vendor validation accepted without independent review; no vendor performance monitoring; vendor treating model behaviour as trade secret with no accommodation; delegated functions without oversight records.
**Evidence.** Vendor contracts and schedules; oversight records; vendor-supplied validation and the deployer's review of it; monitoring reports; delegation oversight audits.
**Typical severity.** S4–S5.
**Hook.** **NAIC Model Bulletin third-party AI oversight provisions explicitly** — the insurer remains fully responsible for the AI's behaviour; delegation oversight requirements under accreditation standards and state law.

#### ADR-1.C5 — Retention shortfall
**Definition.** Retained artefacts are destroyed, aggregated beyond usefulness, or rendered inaccessible before the end of the period in which the determination may be challenged.
**Indicators.** Artefact retention shorter than the applicable limitations period or regulatory lookback; logs retained months while determinations are retained years; model and criteria versions not archived, so a historical determination cannot be reconstructed against the logic then in force; vendor retention shorter than the deployer's obligation; no litigation-hold capability covering AI artefacts; archived data in formats no longer readable.
**Evidence.** Retention schedules for each artefact class; vendor retention terms; model and criteria version archive; litigation-hold procedure; a restoration test on artefacts from the earliest month of the assessment period.
**Typical severity.** S4–S5.
**Hook.** Record-retention requirements under state insurance and utilization review law; litigation-hold and spoliation doctrine; NAIC AIS Program documentation.

> **Assessor note.** C5 is routinely missed because each retention schedule is individually defensible. The failure is in the **mismatch**: a determination retained for ten years, decided by a model version archived for one, applying a criteria version not archived at all, and logged for ninety days, is not reconstructable in year two no matter how good the controls were in year one. Test by restoration from the oldest in-scope month, not by reading the schedule.

---

### Part D — Equity and outcome monitoring
*Whether effects are measured.*

#### ADR-1.D1 — Disparate determination rates
**Definition.** Determination outcomes differ materially across protected classes or their intersections, without assessment or justification.
**Indicators.** No disparity testing performed; testing on single characteristics only, not intersections; no testing of the AI pathway separately from overall outcomes; disparities identified and not acted on; absence of the demographic data needed to test, with no proxy methodology and no plan to obtain it.
**Evidence.** Disparity analyses and methodology; determination data with available demographic attributes; the assessor's independent analysis of the §5.4 sample where data permits.
**Typical severity.** S4–S5.
**Hook.** Federal and state civil rights law; Affordable Care Act §1557; **NAIC AIS Program testing for bias**; state insurance unfair-discrimination provisions.

#### ADR-1.D2 — Overturn-signal suppression
**Definition.** Appeal-overturn and external-review-reversal rates are not measured, not attributed to the AI pathway, or not fed back into the system, its criteria configuration, or its validation.
**Indicators.** Overturn rates not tracked by determination type and by AI involvement; high overturn rates with no corrective action; no feedback loop from overturn to configuration or validation; overturn data held by a function with no channel to the system owner; external review outcomes not reconciled to internal determinations.
**Evidence.** Overturn and external-review data for the assessment period; feedback and corrective-action records; governance minutes.
**Typical severity.** **S5.**
**Hook.** SB 1120 accountability for accuracy; NAIC AIS Program monitoring; evidence of institutional knowledge relevant to extracontractual and bad-faith exposure.

> **Assessor note.** D2 carries S5 severity for a reason that is legal rather than clinical. A measured, unaddressed overturn rate is documentary evidence that the deployer knew the system was producing wrong determinations and continued. That is the element that converts a coverage dispute into an extracontractual claim. Where overturn rates are tracked and high and unaddressed, say so plainly and quantify it.

#### ADR-1.D3 — Proxy discrimination
**Definition.** Facially neutral features reproduce protected-class effects.
**Indicators.** Features strongly correlated with protected characteristics (geography at fine granularity, payer source, language, facility identity, historical utilisation shaped by prior access barriers); no proxy analysis; feature inventory unavailable; vendor model features not disclosed, with no compensating outcome testing.
**Evidence.** Feature inventory; proxy correlation analysis; model documentation; where features are undisclosed, evidence of compensating outcome-based testing.
**Typical severity.** S4.
**Hook.** As D1.

#### ADR-1.D4 — Absent outcome monitoring
**Definition.** No ongoing measurement of determination accuracy against realised clinical or claims outcomes.
**Indicators.** Accuracy measured only at validation, never in production; no comparison of predicted course to actual course; no monitoring of determinations against subsequent readmission, deterioration or reversal; monitoring on operational metrics (throughput, turnaround, denial rate) only.
**Evidence.** Monitoring design and reports; metric definitions; governance review records.
**Typical severity.** S4.
**Hook.** **SB 1120 accountability for accuracy**; NAIC AIS Program ongoing monitoring.

---

### Part E — Operational and data integrity

#### ADR-1.E1 — Turnaround-clock breach induced by the AI pathway
**Definition.** The AI pathway causes or contributes to breach of statutory or contractual determination timeframes through queueing, pending states, escalation loops or routing failures.
**Indicators.** Pended states not counted against the clock; cases cycling between automated and human queues; clock start recorded at a point later than receipt; no monitoring of timeframe compliance by pathway; escalation without a time budget; timeframe breaches concentrated in AI-routed cases.
**Evidence.** Turnaround data by pathway and determination type; clock definitions compared against statutory requirements; queue and pending-state analysis; 25+ case timelines.
**Typical severity.** S3–S4. *Penalties are typically per violation, so severity scales with volume.*
**Hook.** State utilization review timeframe statutes; Medicare Advantage timeliness requirements; CMS prior-authorization rules including the electronic prior authorization obligations effective January 2027.

#### ADR-1.E2 — Protected health information handling
**Definition.** The AI pipeline processes, transmits, retains or exposes PHI beyond the minimum necessary, or outside the permitted relationships.
**Indicators.** Full records transmitted where extracts suffice; PHI to third-party inference endpoints without a business associate agreement; PHI retained in prompts, caches, logs or evaluation datasets without retention control; PHI used for model training without a permitted basis; sub-processors undisclosed; no data-flow map.
**Evidence.** Data-flow map; business associate agreements including sub-processors; retention and minimisation controls; prompt and log inspection; training data provenance.
**Typical severity.** S3–S5.
**Hook.** HIPAA Privacy and Security Rules; state health-privacy and AI-specific data provisions.

#### ADR-1.E3 — Degradation without detection
**Definition.** No monitoring capable of detecting performance decay, distribution shift or silent failure after deployment.
**Indicators.** No drift monitoring; no alerting thresholds; no owner for performance monitoring; silent failures (empty retrieval, failed parse, default output) treated as valid results; no canary or shadow comparison on change; monitoring on availability only.
**Evidence.** Monitoring design, thresholds, alert history, incident records; error-handling behaviour on failure; 12 months of performance trend data.
**Typical severity.** S3–S4.
**Hook.** NAIC AIS Program risk controls and ongoing monitoring.

#### ADR-1.E4 — Absent failure-mode inventory and incident process
**Definition.** The deployer has not enumerated how the system can fail, nor established a process to detect, triage, remediate and report failures.
**Indicators.** No documented failure-mode analysis for the system; no AI-specific incident definition or process; AI failures handled as generic IT incidents; no reporting line to the committee or officer accountable under the AIS Program; no post-incident review; no inventory of AI systems in determination use.
**Evidence.** Failure-mode analysis; incident process and register for the assessment period; governance charters and minutes; AI system inventory.
**Typical severity.** S3–S4.
**Hook.** **NAIC AIS Program** written-programme, governance and accountability requirements; SB 1120 filing requirements.

---

## 7. Scoring

### 7.1 Clause scores
| Score | Meaning |
|---|---|
| **Conformant** | Evidence demonstrates the failure mode is addressed by effective, operating controls. |
| **Conformant with observations** | Controls operate, but with weaknesses that do not currently produce the failure mode. Observations must be stated. |
| **Deficient** | Controls are absent, inadequate, or not operating; or necessary evidence was not produced. The failure mode is possible and may be occurring undetected. |
| **Materially deficient** | The failure mode is **evidenced as occurring**, or controls are absent in a manner making occurrence likely, and the typical severity is S4 or above. |

**7.1.1** Every clause must receive one of these four scores. **"Not assessed," "not applicable" and "unable to determine" are not permitted scores** for a clause within the defined boundary. Where a clause is genuinely inapplicable because the determination type is out of scope, the boundary must be narrowed under §5.2 and the exclusion reported under §10.3 — not recorded as a clause score.

**7.1.2** A clause scored on deployer representation alone, without corroborating evidence, cannot be scored higher than **Conformant with observations**, and the reliance must be disclosed.

**7.1.3** A clause may not be scored **Conformant** where the evidence for it consists only of a policy document. Policies evidence intent. At least one of: operating-effectiveness testing, transaction-level evidence, or system configuration must corroborate.

### 7.2 No composite score
ADR-1 does **not** produce an overall pass, fail, grade, score or rating. Any party aggregating ADR-1 clause scores into a single figure is not reporting an ADR-1 result.

**Rationale.** A composite would permit an S5 finding under B1 or C1 to be offset by conformance on operational clauses. The failures in Parts B and C are not commensurable with the others: a system whose determinations cannot be reconstructed and whose human review is nominal is not partially acceptable. The two indices in §8 exist to provide the comparable summary figures a composite would otherwise be used for.

### 7.3 Mandatory escalation
Where **ADR-1.B1** or **ADR-1.C1** is scored **Materially deficient**, the report must state this in the first paragraph of its summary, with the measured basis. These two findings may not be presented only in a findings table.

---

## 8. The two indices

The indices exist so that results are comparable across assessments, deployers and time. Both must be computed by the method below or not reported as ADR-1 indices.

### 8.1 Reconstructability Index (RI)

**8.1.1 Definition.** The proportion of sampled determinations for which **all** required elements are independently reconstructed from retained artefacts alone.

**8.1.2 Required elements.** For each sampled determination:
1. The complete input set as presented to the system
2. System and model identifier **and version**
3. Criteria set identifier, **version**, and the criteria content as then in force
4. The system's output, including any score, recommendation, rationale or confidence
5. Reviewer identity, and licensure/specialty as at the determination date
6. Reviewer actions in time sequence, with timestamps (case opened, material accessed, determination recorded, any override)
7. The final determination
8. The rationale as communicated to the enrollee or provider

**8.1.3 Pass rule.** All-or-nothing per determination. All eight elements reconstructed = pass. **Reconstruction must not rely on participant recollection or on re-executing the system.** Re-execution is a different test (it shows what the system does now, not what it did then) and does not satisfy 8.1.2.

**8.1.4 Reporting.**
```
RI (unweighted, n=385, adverse-oversampled):      0.41  [95% CI 0.36–0.46]
RI (population-weighted):                          0.58  [95% CI 0.53–0.63]
RI (adverse determinations only, n=193):           0.29  [95% CI 0.23–0.36]
Element failure rates (share of sample where element not reconstructable):
  1 inputs as presented .......... 18%     5 reviewer identity/credentials ..  4%
  2 system/model version ......... 52%     6 reviewer action sequence ....... 44%
  3 criteria version/content ..... 37%     7 final determination ............  0%
  4 system output ................ 29%     8 communicated rationale .........  2%
```
All four RI figures and all eight element rates are mandatory. Element rates are what make the index actionable: they identify which single artefact gap is destroying reconstructability, and it is usually one or two.

**8.1.5** RI must be reported to two decimal places with a 95% confidence interval, the sample size, the stratification, the selection method and the seed.

### 8.2 Human Authority Index (HAI)

**8.2.1** HAI is a **profile of four measures plus a classification**, not a single number. A single number would conceal the asymmetries that matter.

**8.2.2 Measures.** Computed separately for **adverse** and **favourable** determinations. The comparison between them is diagnostic.

| Measure | Definition |
|---|---|
| **Concordance rate** | Share of determinations where the final outcome matches the system's recommendation |
| **Median effective review duration** | Median elapsed time from reviewer opening the case to recording the determination; report also the 10th percentile and the share below the **plausible floor** (8.2.3) |
| **Independent reasoning rate** | Share of determinations whose reviewer record contains case-specific reasoning **not reproducible from the system output** — assessed by a qualified clinician (§4.4) against a documented rubric, on a minimum of 50 adverse determinations |
| **Override rate and viability** | Share overridden; plus whether the workflow permits override without asymmetric friction, established by timed walkthrough of both paths and by reviewer interview |

**8.2.3 Plausible floor.** The assessor must establish, with the clinician under §4.4, the minimum time in which the material presented could be read and considered for each determination type, and report the share of determinations decided below it. The derivation must be stated.

**8.2.4 Classification.**
| Classification | Criteria |
|---|---|
| **Independent** | Concordance materially below 100% in both directions; independent reasoning rate ≥80%; override viable and used; <5% of determinations below the plausible floor |
| **Qualified** | Independent reasoning rate 50–80%, or concordance asymmetry between adverse and favourable outcomes, or 5–15% below the plausible floor |
| **Attenuated** | Independent reasoning rate 20–50%, or >15% below the plausible floor, or override impeded |
| **Nominal** | Independent reasoning rate <20%, or concordance ≥99% on adverse determinations, or median adverse review duration below the plausible floor, or override absent |

**8.2.5** A classification of **Attenuated** or **Nominal** requires a **Materially deficient** score on **ADR-1.B1** and triggers §7.3.

**8.2.6** HAI must not be reported where reviewer action timestamps are unavailable. Report instead: *"HAI not computable — reviewer action timestamps not retained (see ADR-1.C3, scored Deficient)."* Non-computability is a finding under C3, never a neutral omission.

---

## 9. Severity classification

Monetised severity per observed or potential failure instance. Used for comparability and to inform remediation priority.

| Band | Range (USD) | Typical basis |
|---|---|---|
| **S1** | <$1,000 | Administrative rework only; no service or payment effect |
| **S2** | $1,000–$5,000 | Minor service delay; low-cost service or item |
| **S3** | $5,000–$25,000 | Single denied or delayed episode: outpatient procedure, short post-acute stay, specialty drug month |
| **S4** | $25,000–$250,000 | Complex episode or extended stay; per-violation regulatory penalty exposure at volume; single-case extracontractual exposure |
| **S5** | >$250,000 | Systemic pattern across a population; class exposure; corrective action plan; accreditation, contract or licence jeopardy |

**9.1 Recording.** Each observation must record an estimate and its **basis** (actual claim or episode cost, plan-specific average for the service category, published benchmark, or stated assumption). A wide band with a stated method is required; a blank is not acceptable.

**9.2 Potential versus realised.** Distinguish severity **realised** (a failure that occurred and had this cost) from severity **exposed** (a control gap that would have this cost if it occurred). Report separately; never aggregate them into one figure.

**9.3 The S3 threshold.** S3 and above is the region in which risk transfer becomes economically meaningful; S1–S2 failures are generally retained by the deployer regardless of frequency, because the transaction cost of transfer exceeds the loss. Assessors should not characterise an S1–S2 finding as insurable exposure.

---

## 10. Reporting

A report described as an ADR-1 assessment must contain, in this order:

**10.1 Scope and boundary** — §5.2 content, including every asserted exclusion and its basis.
**10.2 Independence statement** — §4 conformance and all §4.6 disclosures.
**10.3 Method** — assessment period; population and reconciliation; sample size, stratification, selection method and seed; evidence obtained; clinician identity and credentials.
**10.4 Limitations and non-production** — §5.5 disclosures; every item of evidence requested and not produced, and the clauses affected.
**10.5 Indices** — RI per §8.1.4; HAI per §8.2, or the §8.2.6 statement.
**10.6 Findings** — all 22 clauses with scores, evidence cited and observations. Where §7.3 applies, the escalated finding appears in the first paragraph of the summary. **A self-assessment must be titled and labelled as a self-assessment on every page.**
**10.7 Severity summary** — realised and exposed, separately, by band and by clause.
**10.8 Prioritised remediation** — each item mapped to its clause and regulatory hook. The assessor may describe what evidence would resolve a finding; the assessor may not design, implement or be engaged to deliver the remediation (§4.3).
**10.9 Residual risk statement** — scoped to the assessment date, the defined boundary and the evidence obtained. Must not assert compliance (§2.2) or future performance (§2.3).
**10.10 Clinical sign-off** — where Parts A or D included determination review.

**10.11 Permitted public statements.** A deployer or developer may state that a system was *"independently assessed against ADR-1 v1.0 as of [date], scope [summary]"* and may publish the indices. It may **not** state or imply that the system is *ADR-1 certified*, *ADR-1 compliant*, *ADR-1 approved*, or that ADR-1 establishes regulatory compliance. There is no ADR-1 certification (§2.6).

---

## 11. Regulatory mapping (informational)

Informational only; see §2.1. Verify against current text in the applicable jurisdiction.

| Regime | Nature of obligation engaged | Clauses most engaged |
|---|---|---|
| **California SB 1120** (Physicians Make Decisions Act, eff. 1 Jan 2025) | Licensed physician/qualified professional makes the final medical-necessity determination; determination rests on the enrollee's own clinical circumstances not a group dataset alone; no denial/delay/modification based solely on AI; plans file policies and remain accountable for accuracy | **A1, B1, B2, D4, E4** |
| **NAIC Model Bulletin on the Use of AI Systems by Insurers** (adopted in a substantial majority of US jurisdictions; AI Systems Evaluation Tool in regulator pilots) | Written AIS Program; senior-management and board accountability; risk controls; model validation; testing for bias and errors; **oversight of third-party AI for which the insurer remains fully responsible** | **A4, A5, C3, C4, D1, E3, E4** |
| **CMS-0057-F** (electronic prior authorization, obligations from Jan 2027) | Electronic prior authorization capability; decision timeframes; denial-reason communication | **C2, E1** |
| **Medicare Advantage utilization management rules** | Coverage criteria constraints; medical-necessity basis; timeliness; adverse-determination notice content | **A1, A2, C2, E1** |
| **State utilization review statutes** | Reviewer qualification; timeframes; appeal independence; notice content; record retention | **B2, B3, C2, C5, E1** |
| **ERISA claims procedures** (where applicable) | Full and fair review; appeal independence; rationale sufficiency | **B3, C2** |
| **HIPAA Privacy and Security Rules** | Minimum necessary; business associate relationships; safeguards | **E2** |
| **ACA §1557 and civil rights law** | Non-discrimination in benefit administration | **D1, D3** |
| **Litigation discovery and spoliation doctrine** | Production of system design, decision basis, governance records; preservation | **C1, C3, C5** |

---

## 12. Versioning and change process

**12.1** Versions are `MAJOR.MINOR`. MINOR adds or clarifies without renumbering. MAJOR may restructure; retired identifiers are never reused.

**12.2** v1.1 is planned following the comment period closing **31 January 2027**, informed by findings from assessments performed under v1.0.

**12.3** Change requests should state the proposed clause, the observed failure it addresses, and the evidence that would assess it. Proposals adding a failure mode without a means of assessing it will not be adopted.

**12.4** A report must state the version assessed against. An assessment against v1.0 remains valid as an assessment against v1.0 after v1.1 publishes.

**12.5 Known limitations of v1.0**, stated so they are not discovered as surprises:
- No conformity-assessment scheme, accredited-assessor register or mark (§2.6).
- Disparity testing (D1, D3) presumes access to demographic attributes many deployers do not hold; proxy methodology is not yet specified and is a priority for v1.1.
- The plausible-floor method (§8.2.3) requires assessor clinical judgement and will vary between assessors until reference floors are published by determination type. This is the index's weakest point for comparability.
- Coverage is US-centric. Non-US regimes are not mapped.
- Scope is utilization management and claims adjudication. Pricing, rating, enrollment, provider-side and fraud-investigation systems are out of scope (§1.4).

---

## Annex A — Minimum evidence request

**A.1 Governance.** AI system inventory covering determination use · AIS Program document · governance charter and minutes for the assessment period · accountable officer and committee · AI incident process and register · failure-mode analysis for the system.

**A.2 System.** Architecture and data-flow documentation · model/system documentation including intended use and stated validation scope · validation reports · feature inventory · output schema · prompt/rule/threshold configuration as at the start and end of the assessment period · change log with approvals · monitoring design, thresholds and alert history.

**A.3 Criteria.** Criteria sets in scope with versions · criteria-to-configuration mapping · filed or published policy documents · criteria version archive covering the full assessment period.

**A.4 Human review.** Workflow definition including override and escalation paths · reviewer roster with licensure and specialty · routing rules · productivity standards and incentive arrangements · reviewer training materials · interface walkthrough access · reviewer interview access (minimum 3, without management present).

**A.5 Determinations.** Complete population listing for the assessment period, reconciled to an independent control total · determination-level records for the assessor-drawn sample · adverse determination notices · appeal and grievance records · external review outcomes · overturn rates by determination type and pathway.

**A.6 Logs.** Log schema · log samples · retention configuration per artefact class · integrity controls · vendor log access terms · restoration test from the oldest in-scope month.

**A.7 Vendor.** Contracts and schedules including audit, model documentation, change-notification, log-access and retention rights · vendor-supplied validation and the deployer's review of it · oversight and monitoring records · sub-processor disclosure · business associate agreements.

**A.8 Operational.** Turnaround data by pathway and determination type · clock definitions · pended-state analysis · disparity analyses and methodology · outcome monitoring reports · data-flow map and minimisation controls.

> Non-production of any item is a finding under §5.3.1, scored against the affected clauses, and reported under §10.4.

---

## Annex B — Conformance statement template

```
ADR-1 ASSESSMENT — CONFORMANCE STATEMENT

System ............. [name, version]
Developer .......... [entity]            Deployer ........... [entity]
Boundary ........... [summary; full boundary at §10.1]
Determination types  [list]              Lines of business .. [list]
Assessment period .. [start]–[end]       Assessment date .... [date]
Assessed against ... ADR-1 v1.0
Assessor ........... [entity]   Independence: §4 conformant [yes/no]
Clinical reviewer .. [name, licence, specialty]

Reconstructability Index
  unweighted (n=___, adverse-oversampled) ....  0.__  [95% CI 0.__–0.__]
  population-weighted .........................  0.__  [95% CI 0.__–0.__]
  adverse only (n=___) ........................  0.__  [95% CI 0.__–0.__]
  [element failure rates: §8.1.4 — all eight mandatory]

Human Authority Index
  classification ..............................  [Independent / Qualified /
                                                  Attenuated / Nominal]
  concordance (adverse / favourable) ..........  __% / __%
  median effective review duration (adverse) ..  __ ; below plausible floor __%
  independent reasoning rate (n=___) ..........  __%
  override rate / viability ...................  __% / [viable / impeded / absent]

Clause scores   C = Conformant · CO = Conformant with observations
                D = Deficient · MD = Materially deficient
  A1 __  A2 __  A3 __  A4 __  A5 __
  B1 __  B2 __  B3 __  B4 __
  C1 __  C2 __  C3 __  C4 __  C5 __
  D1 __  D2 __  D3 __  D4 __
  E1 __  E2 __  E3 __  E4 __

Severity summary    realised: S1__ S2__ S3__ S4__ S5__
                    exposed:  S1__ S2__ S3__ S4__ S5__

§7.3 escalation applicable ... [yes/no]   Evidence not produced ... [yes/no — §10.4]

This statement summarises a report dated [date]. It is an assessment as of that
date, on the boundary defined, based on the evidence obtained. It does not
determine compliance with any statute, rule or contract, and does not assure
future performance. There is no ADR-1 certification.
```

---

*ADR-1 v1.0 · ⟨MAINTAINER⟩ · 2 October 2026 · CC BY 4.0 · comments through 31 January 2027*
