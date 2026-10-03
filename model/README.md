# Five-Year Financial Model — Located Firm Capacity Origination

Code behind `../FIVE_YEAR_FINANCIAL_MODEL.md`. Reproduces every figure in that memo.

## Files

| File | Purpose |
|---|---|
| `model4.py` | Scenario definitions (downside/base/upside) and the single-year P&L engine. Standalone-runnable. |
| `final.py`  | Imports `model4`, adds the delivery-capacity fix, the three financing modes, unit economics, break-even, one-way sensitivity, Monte Carlo #1, market share, valuation. |
| `supp.py`   | Imports `final`, adds the wide Monte Carlo, the strict-$0 year-by-year detail, and the dossier reconciliation. |

## Run

```sh
python3 -m pip install numpy      # only needed by nothing; stdlib `random` is used
python3 model4.py                 # scenario tables
python3 final.py                  # main analysis (Tables 1-9)
python3 supp.py                   # Tables 4b, 6b, 10   (~2 min; 20,000 MC draws)
```

`final.py` and `supp.py` must be run from this directory — they load the
preceding module by relative path.

## Internal consistency

Two identities are enforced by `assert` in the engine; the model aborts if either breaks.

```
beginning customers + new − churned = ending customers
beginning cash + free cash flow      = ending cash
```

Both were re-verified after the final parameter set:
`cum_fcf[4] == sum(fcf)` and `cust_end[3] + new[4] − churn[4] == cust_end[4]`.

## Structure of the model

Headcount is **endogenous** in bootstrap mode. The solver cuts founder pay first,
then scales hiring, until the year's loss is fundable from cash on hand. This
creates the governing feedback loop, which is the central result of the analysis:

```
gross profit -> affordable opex -> originator headcount -> MW closed
             -> success + brokerage + flexibility revenue -> gross profit
```

Two financing modes matter:

- `mode="ebitda"` — hires while the EBITDA loss is fundable. Ignores working
  capital, so it runs a cash deficit (base: peak $441k).
- `mode="cash"`   — strict $0: ending cash may never go below zero. Feasible,
  but costs 22% of Year-5 revenue and pays the founder nothing for five years.

## Known modelling artefacts (not bugs)

- Year-2 revenue growth reads as ~1,000% because Year 1 is only $34k.
- In the downside, screen revenue *declines* after Year 3 as retainers consume
  delivery capacity. Retainers earn more per delivery FTE, so the allocation is
  economically rational; 25% of capacity is nonetheless reserved for screens
  because screens are the lead-generation product.
- Monte Carlo inputs are the scenario bounds, i.e. modelling assumptions. The
  output measures assumption sensitivity, NOT real-world probability. No
  frequency data exists for any driver in this business.

## Three corrections made during the build

Each was a real error that inflated results, found by checking outputs against
services-industry norms rather than by inspection:

1. **COGS omitted 70% of analyst payroll.** COGS was a % of revenue, independent
   of delivery labour. Now built up from resources.
2. **No delivery-capacity constraint**, so revenue/FTE reached $1.46M. Screens and
   retainers are now limited by delivery FTE-hours. Base Year-5 revenue/FTE is
   now $307k, inside the professional-services range.
3. **Founder salary was not affordability-constrained**, so the downside "paid" a
   salary it could not fund. Founder pay is now cut before any hiring is scaled.

## Experiment 01 — originator throughput

Supports `../EXPERIMENT_01_ORIGINATOR_THROUGHPUT.md`, the outreach plan for the
$0–$400 test of the model's most dangerous assumption (MW closed per
originator-year, which carries a $7.62M Year-5 swing on a $5.81M base).

| File | Purpose |
|---|---|
| `responses.csv`           | 21-field data-collection template, header only |
| `analyze_experiment.py`   | Exclusion rules, median + bootstrap CI, no-brand haircut, verdict against pre-registered thresholds, and a re-run of the five-year model at the measured value |

```sh
python3 analyze_experiment.py              # reads responses.csv
python3 analyze_experiment.py other.csv    # or a named file
```

Thresholds are **pre-registered** at the top of the script and must not be
edited after collection begins:

```
KILL_BELOW    = 60            # MW/originator-yr, planning-adjusted
CAUTION_BAND  = (60, 90)
MODEL_BASE_MW = 110           # the assumption under test
HAIRCUT_RANGE = (0.50, 0.70)  # no-brand startup vs established-firm originator
```

The decision statistic is the **median**, not the mean: throughput is expected to
be right-skewed, and the mean imports tail outcomes a single new hire cannot
rely on. The script flags skew when mean/median > 1.4, excludes (rather than
adjusts) team-level answers, and reports the by-segment breakdown so a skewed
sample is visible.

Verified against synthetic kill-case, proceed-case and empty-file inputs.

Note the asymmetry the plan makes explicit: a *favourable* interview median of
160 MW becomes a planning figure of 96 MW after the haircut, which re-runs to
Year-5 revenue of $4.75M — below the $5.81M base case. The base case already sat
at the optimistic edge of this parameter.
