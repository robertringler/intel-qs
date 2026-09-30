# Market sizing — PayeeProof (bottom-up)

TAM figures from syndicated market reports are **not used**. Sizing is bottom-up from firm counts.

## Firm universe
- [F] US firms with 20–99 employees: **519,015**. Firms with 100–499: **88,023**. Source: Census SUSB 2021 (S057).
- [D] Core universe (20–499 employees) = **607,038 firms**. Firms with 500–999 employees are a stretch segment and are not counted.

## Reachable segment (originate outside AP suites)
- [F] Only 20% of AP teams are fully automated, and 73% use some automation (S082).
- [F] ERPs such as Sage Intacct and Business Central generate NACHA or positive-pay files for bank upload (S083).
- [M] 20–45% of core firms originate ACH or wires from ERP-generated files or bank portals, so they are not
  protected end-to-end by one AP suite. This gives **120k–275k reachable firms**, mode 200k.
- [I] Firms paying mainly through BILL or Ramp are a lower-priority segment (S062, S064). They are not excluded,
  because vendor-master change control still applies to them.

## Value pools (annual)
| Layer | Calculation | Value | Tag |
|---|---|---|---|
| TAM (software spend capacity) | 607k firms × $6k ARPA mode | ≈ $3.6B | [M] |
| SAM (reachable) | 200k × $6k | ≈ $1.2B | [M] |
| SOM Y5 (model P50) | ~0.7% of SAM accounts, ≈1,400 accounts × ~$6.6k | ≈ $9.3M ARR | [M], from ev_results |

## Loss pool the product addresses
- [F] BEC reported losses $3.046B in 2025 (IC3; floor, S001). [F] FBI (2016) estimated only ~15% of fraud victims report (S081).
- [D] Mean loss per reported BEC complaint ≈ **$123k** (3.046e9 / 24,768).
- [I] Using IC3 as a floor, the true annual US BEC loss is several multiples of $3B. We make no point estimate
  because there is insufficient evidence for statistical inference.

## Cross-check against incumbents
- [F] Eftsure + Sis ID + Relish: >4,000 customers across three regions after ~10 years (S014).
- [F] Trustpair: ~400 enterprise customers (S012).
The Y5 P50 of ~1,400 accounts at mid-market price points is the same order of magnitude as these
benchmarks, so the model does not assume unprecedented adoption.
