# Financial model

- Engine: `financial/model.py` (monthly cohorts over 60 months, rolled up annually), with a 5,000-draw Monte Carlo layer over
  the nine uncertain drivers. Reproducible: `python financial/model.py`.
- Consistency check: the independent opportunity-level EV model (`research/statistics/ev_model.py`) gives Y5 ARR P50
  **$9.3M**. The operating model's Monte Carlo gives Y5 ARR P50 **$10.5M**. The two agree within ~13%.

## Key results (see scenarios.md for full tables)
| Metric | Pessimistic | Base | Aggressive |
|---|---|---|---|
| Y5 ARR | $0.90M | $10.63M | $32.81M |
| Y5 paying customers | 251 | 1,458 | 3,092 |
| Break-even month | none within 60 | 53 | 30 |
| Peak cash need | $12.8M (not survivable; kill criterion applies) | $5.7M | $3.2M |
| LTV/CAC | 1.5 | 7.0 | 13.8 |
| CAC payback | 33 mo | 12 mo | 8 mo |

Monte Carlo: Y5 ARR P10 $6.0M / P50 $10.5M / P90 $18.7M. P(break-even ≤ 60 months) = 62%.
Peak cash need P50 $6.8M, P90 $11.4M.

## Capital plan
- **Seed: $3.0M** funds ~24 months of the base plan to ~$1.6M ARR (Y2).
- **Series A (~$5–6M)** is needed in the base case around month 20–24, conditional on the milestone gates.
- **Kill gate (month 9–12):** fewer than 25 paying customers, or ARPA below $250/month, triggers stop or pivot. Maximum capital
  at risk before the gate is ≈ $1.3M (Y1 burn in every scenario).
- **Capital-efficient variant:** holding opex growth at 15% instead of 35% moves base-case break-even to month 42 and
  cuts peak cash need to $3.97M, with Y5 ARR unchanged at $10.6M (computed with `replace(BASE, opex_growth_annual=0.15)`).

## Likely bottleneck
Top-of-funnel volume combined with free-to-paid conversion. Both are unmeasured today and are the first things the product instruments.
