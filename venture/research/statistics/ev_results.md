# EV model results

Monte Carlo draws per candidate: 20,000; seed 20260930; discount rate 30%; horizon 5 years + terminal value on Y5 ARR.

All inputs are [M] model assumptions tied to benchmarks in `ev_params.json`. Outputs are model results, not forecasts.

| Rank | Candidate | Mean NPV (±SE) | P10 | P50 | P90 | P(NPV>0) | Y5 ARR P50 | P(ARR5>$10M) | Capital req. P50 / P90 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | #1 Payee assurance + Nacha controls (lower mid-market) | $8.4M (±$0.1M) | $-1.9M | $5.4M | $22.3M | 79% | $9.3M | 46% | $9.1M / $14.4M |
| 2 | #12 NSA IDR automation for independent provider groups | $2.9M (±$0.1M) | $-4.4M | $0.3M | $13.8M | 52% | $4.7M | 21% | $10.1M / $13.8M |
| 3 | #100 ACH pre-flight screening API for TPSPs/vertical SaaS | $2.4M (±$0.1M) | $-3.8M | $0.4M | $11.1M | 53% | $4.7M | 16% | $9.4M / $13.0M |
| 4 | #26 SMB duty drawback automation | $-1.0M (±$0.0M) | $-5.2M | $-2.3M | $4.8M | 29% | $2.9M | 6% | $11.7M / $14.7M |
| 5 | #48 EU CRA vulnerability-reporting workflow for SMB makers | $-1.8M (±$0.0M) | $-5.0M | $-2.7M | $2.5M | 21% | $2.4M | 2% | $11.3M / $14.3M |
| 6 | #2 White-label originator portal sold to community banks/CUs | $-2.4M (±$0.0M) | $-5.2M | $-3.1M | $1.3M | 16% | $2.4M | 1% | $12.4M / $15.5M |
| 7 | #34 CPG deductions (control: eliminated at G3) | $-3.7M (±$0.0M) | $-5.6M | $-4.0M | $-1.5M | 4% | $1.3M | 0% | $12.0M / $14.6M |
| 8 | #25 IEEPA refund filing (control: eliminated at G5) | $-5.7M (±$0.0M) | $-6.8M | $-5.7M | $-4.6M | 0% | $0.0M | 0% | $12.3M / $14.9M |

## Global sensitivity (Spearman rank correlation of input with NPV)

- **#1 Payee assurance + Nacha controls (lower mid-market)**: arpa_usd +0.57, y5_penetration +0.52, exit_multiple +0.27, reachable_accounts +0.19, nrr_expansion +0.13
- **#12 NSA IDR automation for independent provider groups**: arpa_usd +0.45, y5_penetration +0.34, reachable_accounts +0.24, exit_multiple +0.22, opex_base -0.14
- **#100 ACH pre-flight screening API for TPSPs/vertical SaaS**: arpa_usd +0.54, y5_penetration +0.44, reachable_accounts +0.30, exit_multiple +0.24, nrr_expansion +0.23
- **#26 SMB duty drawback automation**: arpa_usd +0.47, y5_penetration +0.37, opex_base -0.27, reachable_accounts +0.26, exit_multiple +0.22
- **#48 EU CRA vulnerability-reporting workflow for SMB makers**: arpa_usd +0.47, y5_penetration +0.47, opex_base -0.32, reachable_accounts +0.26, exit_multiple +0.26
- **#2 White-label originator portal sold to community banks/CUs**: arpa_usd +0.53, y5_penetration +0.42, opex_base -0.35, exit_multiple +0.27, months_to_first_revenue -0.21
- **#34 CPG deductions (control: eliminated at G3)**: opex_base -0.54, y5_penetration +0.40, arpa_usd +0.38, exit_multiple +0.24, reachable_accounts +0.18
- **#25 IEEPA refund filing (control: eliminated at G5)**: opex_base -0.99, launch_investment -0.14, gross_margin +0.02, opex_var -0.02, cac_usd -0.01

## Tornado for leader (#1 Payee assurance + Nacha controls (lower mid-market))

Deterministic path at modal values, regime intact, no compression: base NPV $3.7M.

| Parameter | Low | High | NPV at low | NPV at high | Swing |
|---|---|---|---|---|---|
| arpa_usd | 2400 | 15000 | $-3.4M | $21.4M | $24.8M |
| y5_penetration | 0.002 | 0.02 | $-2.9M | $20.8M | $23.7M |
| exit_multiple_arr | 2.0 | 7.0 | $-0.6M | $10.2M | $10.9M |
| reachable_accounts | 120000 | 275000 | $0.0M | $7.2M | $7.1M |
| nrr_expansion | 0.0 | 0.12 | $1.8M | $6.9M | $5.2M |
| opex_base_per_year_usd | 900000 | 2000000 | $5.5M | $1.6M | $3.9M |
| cac_usd | 2500 | 9000 | $5.0M | $1.6M | $3.4M |
| months_to_first_revenue | 3 | 9 | $4.7M | $1.8M | $2.9M |
| gross_margin | 0.78 | 0.89 | $3.4M | $4.0M | $0.6M |
| annual_churn | 0.08 | 0.25 | $3.9M | $3.4M | $0.4M |
