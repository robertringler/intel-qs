# Developer target list — and what building it revealed

**3 October 2026.** Gate still not passed. This is a list, not outreach; no one here is to be contacted until the primary reads in `TEST_01_CORRECTION_AND_STATUS.md` are done.

**All of it is trade press** — the same source class that produced two wrong tariff figures in Test 01. Treat every row as `[VERIFY]`. §5 names the one subset whose exposure is in primary, reachable filings.

---

## 1. Three findings that came out of the search, not the list

I went looking for mid-market 50–300 MW developers. What I found cuts against the thesis in three independent ways, and it would be dishonest to bury that under a table of names.

**1.1 The entities actually doing flexibility are the ones both dossiers excluded as non-customers.**

Every named flexibility deployment I could find involves a hyperscaler, a chip vendor, a large REIT, or a utility:

| Deployment | Parties |
|---|---|
| Santa Clara pilot, 21 Apr 2026 | **Silicon Valley Power** + **Nvidia** workloads, Emerald AI platform |
| Peer-reviewed flexibility test | **Salt River Project** + Emerald AI |
| Demonstrations at 100% target alignment | **National Grid** + Emerald AI |
| ~100 MW power-flexible AI factory, Manassas | **Digital Realty** + **Nvidia** |
| 1 GW of reducible demand committed nationwide | **Google**, via utility agreements |

The dossiers excluded hyperscalers (they staff their own power teams and will not pay a stranger) and utilities (they are the counterparty, not the buyer). **So on current evidence the population doing the thing WATTFLOCK would advise on is precisely the population that will not buy the advice.** I found no named mid-market flexible-load deployment.

**1.2 The curtailment-literate population is converting away from curtailment.**

Bitcoin miners are the most curtailment-experienced load class in existence — ERCOT crypto demand reached 4,288 MW in Nov 2025, and mining load "can curtail to near zero in seconds without equipment damage" `[ESTIMATE]`. They looked like the ideal customer. They are not, for a structural reason:

> "The sites most worth converting to AI are the least Bitcoin-native: large, grid-connected, contiguous, fiber-reachable, financeable campuses with firm power. The most Bitcoin-native sites — remote, interruptible, modular, flare-gas, stranded-hydro, demand-response-optimized — are exactly the ones that fail the AI screen." `[ESTIMATE — trade analysis]`

**Entering AI means moving to firm power.** The converts shed curtailment exposure as they convert; the ones that stay interruptible stay mining. And mining demand response has historically been worth only **2–10% of miner revenues** `[ESTIMATE]` — which is the most flexible load class in the economy telling you what flexibility is worth. The dossier's §25 test 4 kill line was *"flexibility share below 8% deletes the stream."* That benchmark now has a number against it, and it straddles the line.

**1.3 In the largest market, curtailment is becoming statutory rather than negotiated.**

Texas SB6 requires loads of **75 MW or more interconnecting from 2026 onward to accept mandatory curtailment during firm load shed events** `[FACT]`, and the PUCT has affirmed curtailment authority over co-located data centers in its first net-metering case under SB6 `[FACT]`.

**A mandatory term is not a negotiated term.** There is no cap to argue over, no deal to advise on, and no leverage a quantified distribution would improve. Separately, ERCOT **cut its 2026 summer peak forecast by 3.7 GW** on updated modelling of large computational load behaviour, because more data centers can be curtailed `[FACT]` — the ISO is already computing the quantity, and it is the party that controls the curtailment.

---

## 2. In-band candidates: public HPC converts

The only in-band population that has actually been curtailed at scale, and — critically — **the only one whose power contracts and curtailment exposure sit in SEC filings.**

| Company | Ticker | Relevant capacity | Footprint | Why on the list |
|---|---|---|---|---|
| **Cipher Mining** | CIFR | **170 MW** 10-year hosting deal with Fluidstack (Google-backed); fitted for H100/Blackwell | TX, SPP | Dead centre of the 50–300 MW band with a disclosed long-term contract |
| **Core Scientific** | CORZ | **100 MW** HPC with Port Muskogee, OK, operational 2026 | **SPP** | In-band, in the SPP footprint where CHILLS lives |
| **TeraWulf** | WULF | **360 MW** of contracted AI hosting | NY, PJM-adjacent | Above band but discloses hosting contracts |
| **Applied Digital** | APLD | HPC pivot at scale | ND, MISO/SPP | Long interruptible operating history |
| **Soluna Holdings** | SLNH | Green data centers co-located with renewables for AI/HPC | TX, SPP | Smallest and most curtailment-native; best interview, worst customer |
| **IREN** | IREN | 1.6 GW Alva, OK campus; ~3 GW by 2026 | **SPP** | Far above band; included because the SPP footprint matters |

Sector context: over **$70bn of cumulative AI/HPC contracts** announced across public miners `[ESTIMATE]`.

---

## 3. In-band candidates: independent developers and colocation

| Company | Capacity | Footprint | Note |
|---|---|---|---|
| **WhiteFiber** | NC-1 campus on a **99 MW capacity agreement with Duke Energy**, up to 200 MW over time; 10-yr/40 MW colo deal with Nscale (~$865M TCV); first 20 MW billing from 30 Apr 2026 | NC, Duke | **The cleanest single case on this list** — in-band, named utility agreement, disclosed terms, conditions on "infrastructure upgrades and other conditions" |
| **Novva** | Project Borealis, Phoenix/Mesa — **300 MW** total, first **96 MW** phase late 2026; also Tahoe Reno | AZ (SRP/APS), NV | In band. Arizona matters: SRP is an Emerald AI test partner |
| **PowerHouse Data Centers** | Spotsylvania NoVA campus; Reno NV | VA (Dominion), NV | In band |
| **AVAIO Digital Partners** | Little Rock multi-phase, up to 1 GW, $6bn | AR, SPP/Entergy | Above band; SPP footprint |
| **Prime, Tract, Crane, Corscale, Rowan Digital, Edged Energy** | Named new entrants, capacities not confirmed | various | Unverified; include only after checking |
| **Stack Infrastructure** (20–50 MW builds), **Flexential** (10–40 MW) | Below band | various | Listed to exclude: too small to carry a five-figure fee |

**Deliberately excluded**, consistent with both dossiers: Google, Meta, Amazon, Microsoft, Oracle, CoreWeave at current scale, Crusoe/Stargate (1.2 GW), and all non-US developers (Pure Data Centres Finland, Volt Dubai, Elea Brazil, Macquarie Sydney, AirTrunk).

**Note how thin §3 is relative to §2.** Nearly every large named US project I found is a hyperscaler. The independent 50–300 MW developer that both theses are built around is real but hard to enumerate from public sources — which is itself a warning about the size of the addressable set.

---

## 4. Who to approach, when that time comes

**Role level only. I have not named individuals and will not infer them** — a guessed name at a real company is worse than no name, and these are private people.

| Target | Role | Why them |
|---|---|---|
| Public converts (§2) | VP Energy / Head of Power Strategy; **and the CFO's disclosure counsel for the 10-K risk language** | They have been curtailed and can price it |
| Independents (§3) | VP Infrastructure / Chief Development Officer | They sign the utility agreement |
| Utilities running pilots | Large-load account executive | **Interview only, never a customer** — they are the counterparty |
| Lenders and independent engineers | Director, Power & Infrastructure credit; IE practice lead | The second reader of any opinion, and the better long-run customer |

**Sourcing routes, all free and public:** ERCOT Large Load Working Group and TAC attendance; SPP stakeholder rosters; PUCT, PUCO, IURC and OPUC docket service lists; 7x24 Exchange, Data Center World and Infocast past speaker lists; **SEC filings for the six public converts.**

---

## 5. The one thing worth doing with this list now

**Read the 10-Ks and 10-Qs of the six public converts in §2.**

This is the strongest recommendation in the document, for four reasons:

1. **It is primary.** SEC filings, not trade press. Test 01 failed partly because every input was a secondary summary, and `sec.gov` is reachable from here while `spp.org`, `montana-dakota.com`, `sepapower.org` and the rest are not.
2. **Curtailment exposure must be disclosed.** A public company with interruptible load has to describe the risk in its risk factors and its power-contract discussion. That is a quantified, audited, adversarially-reviewed statement of exactly the exposure WATTFLOCK proposes to price.
3. **It directly tests the thesis.** If the filings disclose expected curtailment hours, historical curtailed hours, or the revenue effect, then **the distribution is already public for the most exposed load class in the market** — and a third-party opinion has materially less to sell. If they disclose the exposure as unquantifiable, the thesis survives a real test for the first time.
4. **It costs nothing and breaks no discipline.** Reading public filings is not approaching a customer.

**Pre-register before reading, as the correction document requires:** if three or more of the six disclose either a quantified curtailment-hour expectation or a historical curtailed-hours figure, that is further evidence against the curtailment opinion — and should be recorded as such before the first filing is opened, not after.

---

## 6. Status unchanged

| | |
|---|---|
| Curtailment opinion | Gate not passed. **Three new adverse findings** above: flexibility sits with excluded parties; converts move to firm power; Texas curtailment is statutory and the ISO already models it |
| Origination desk | Still closed on market grounds |
| Being built | **Nothing** |
| This list | Research. **Not a call sheet.** Nobody is contacted until the primary reads are done |
