"""PayeeProof 5-year operating model (monthly cohorts, annual roll-up).

Scenarios are parameter sets tied to research benchmarks (see assumptions.md).
A Monte Carlo layer samples the key uncertain drivers to produce distributions
for Y5 ARR, break-even month and peak cash need.

Run: python financial/model.py  -> writes financial/scenarios.md and scenarios.json
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, replace
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
MONTHS = 60


@dataclass(frozen=True)
class Scenario:
    name: str
    # acquisition
    free_signups_m1: float          # free signups per month at launch
    signup_growth_mom: float        # monthly growth of signups (content/SEO/channel compounding)
    signup_growth_decay: float      # growth decays each month (saturation)
    free_to_paid: float             # share of signups converting to paid within ~2 months
    partner_paid_m: float           # paid logos/month from bank/insurer/accounting partners (from month 7)
    # monetisation
    arpa_month: float               # blended $ per paying account per month
    expansion_annual: float         # net expansion of retained ARPA per year
    logo_churn_month: float         # monthly logo churn of paying accounts
    # costs
    gross_margin: float
    cac_paid_logo: float            # blended marketing+sales cost per new paying logo
    base_opex_month_y1: float       # R&D + G&A + support base (excl. S&M variable)
    opex_growth_annual: float
    starting_cash: float


BASE = Scenario("base", free_signups_m1=40, signup_growth_mom=0.12, signup_growth_decay=0.035,
                free_to_paid=0.08, partner_paid_m=4, arpa_month=500, expansion_annual=0.05,
                logo_churn_month=0.012, gross_margin=0.84, cac_paid_logo=5000,
                base_opex_month_y1=95000, opex_growth_annual=0.35, starting_cash=3_000_000)
PESSIMISTIC = replace(BASE, name="pessimistic", free_signups_m1=25, signup_growth_mom=0.08,
                      free_to_paid=0.05, partner_paid_m=1.5, arpa_month=300, expansion_annual=0.0,
                      logo_churn_month=0.02, gross_margin=0.8, cac_paid_logo=8000)
AGGRESSIVE = replace(BASE, name="aggressive", free_signups_m1=50, signup_growth_mom=0.14,
                     free_to_paid=0.09, partner_paid_m=6, arpa_month=650, expansion_annual=0.08,
                     logo_churn_month=0.009, gross_margin=0.86, cac_paid_logo=4500,
                     base_opex_month_y1=110000)


def run(s: Scenario) -> dict:
    signups = np.zeros(MONTHS)
    paid_new = np.zeros(MONTHS)
    paid = np.zeros(MONTHS)
    mrr = np.zeros(MONTHS)
    growth = s.signup_growth_mom
    level = s.free_signups_m1
    arpa = s.arpa_month
    prev_paid = 0.0
    for m in range(MONTHS):
        if m > 0:
            level *= 1 + growth
            growth = max(growth - s.signup_growth_decay * growth, 0.0)
        signups[m] = level
        conv = s.free_to_paid * (signups[m - 2] if m >= 2 else 0.0)
        partner = s.partner_paid_m if m >= 6 else 0.0
        paid_new[m] = conv + partner
        paid[m] = prev_paid * (1 - s.logo_churn_month) + paid_new[m]
        if m > 0 and m % 12 == 0:
            arpa *= 1 + s.expansion_annual
        mrr[m] = paid[m] * arpa
        prev_paid = paid[m]
    revenue = mrr
    cogs = revenue * (1 - s.gross_margin)
    s_and_m = paid_new * s.cac_paid_logo
    opex = np.array([s.base_opex_month_y1 * (1 + s.opex_growth_annual) ** (m // 12) for m in range(MONTHS)])
    ebitda = revenue - cogs - s_and_m - opex
    cash = s.starting_cash + np.cumsum(ebitda)
    be = next((m + 1 for m in range(MONTHS) if ebitda[m] > 0 and all(ebitda[m:m + 3] > 0)), None)
    years = []
    for y in range(5):
        sl = slice(12 * y, 12 * y + 12)
        years.append({
            "year": y + 1,
            "paying_customers_end": round(float(paid[12 * y + 11])),
            "new_paying_logos": round(float(paid_new[sl].sum())),
            "arpa_month_end": round(float(mrr[12 * y + 11] / max(paid[12 * y + 11], 1e-9)), 0),
            "mrr_end": round(float(mrr[12 * y + 11])),
            "arr_end": round(float(mrr[12 * y + 11] * 12)),
            "revenue": round(float(revenue[sl].sum())),
            "gross_profit": round(float((revenue - cogs)[sl].sum())),
            "s_and_m": round(float(s_and_m[sl].sum())),
            "opex_ex_sm": round(float(opex[sl].sum())),
            "ebitda": round(float(ebitda[sl].sum())),
            "cash_end": round(float(cash[12 * y + 11])),
        })
    ltv = s.arpa_month * s.gross_margin / max(s.logo_churn_month, 1e-9)
    return {
        "scenario": asdict(s), "years": years,
        "breakeven_month": be,
        "min_cash": round(float(cash.min())),
        "peak_cash_need": round(float(max(0.0, s.starting_cash - cash.min()))),
        "unit_economics": {
            "ltv_gross_margin": round(ltv),
            "ltv_to_cac": round(ltv / s.cac_paid_logo, 2),
            "cac_payback_months": round(s.cac_paid_logo / (s.arpa_month * s.gross_margin), 1),
        },
    }


def monte_carlo(n: int = 5000, seed: int = 11) -> dict:
    rng = np.random.default_rng(seed)
    arr5, be, need = [], [], []
    for _ in range(n):
        s = replace(
            BASE,
            free_signups_m1=rng.triangular(25, 40, 60),
            signup_growth_mom=rng.triangular(0.08, 0.12, 0.16),
            free_to_paid=rng.triangular(0.04, 0.08, 0.11),
            partner_paid_m=rng.triangular(1, 4, 8),
            arpa_month=rng.triangular(250, 500, 800),
            expansion_annual=rng.triangular(0.0, 0.05, 0.12),
            logo_churn_month=rng.triangular(0.007, 0.012, 0.022),
            gross_margin=rng.triangular(0.78, 0.84, 0.88),
            cac_paid_logo=rng.triangular(3000, 5000, 9000),
        )
        r = run(s)
        arr5.append(r["years"][-1]["arr_end"])
        be.append(r["breakeven_month"] or 999)
        need.append(r["peak_cash_need"])
    a, b, c = np.array(arr5), np.array(be), np.array(need)
    pct = lambda x, q: float(np.percentile(x, q))
    return {
        "draws": n,
        "arr5_p10": pct(a, 10), "arr5_p50": pct(a, 50), "arr5_p90": pct(a, 90),
        "p_breakeven_within_60m": float((b <= 60).mean()),
        "breakeven_month_p50_given_reached": float(np.median(b[b <= 60])) if (b <= 60).any() else None,
        "peak_cash_need_p50": pct(c, 50), "peak_cash_need_p90": pct(c, 90),
    }


def main() -> None:
    results = [run(s) for s in (PESSIMISTIC, BASE, AGGRESSIVE)]
    mc = monte_carlo()
    (HERE / "scenarios.json").write_text(json.dumps({"scenarios": results, "monte_carlo": mc}, indent=2))
    f = lambda x: f"${x/1e6:,.2f}M"
    lines = ["# Five-year scenarios (generated by financial/model.py)", "",
             "Outputs are model results from [M] assumptions in assumptions.md, not forecasts.", ""]
    for r in results:
        s = r["scenario"]
        lines += [f"## {s['name'].title()}", "",
                  f"Break-even month (3 consecutive EBITDA-positive months): **{r['breakeven_month'] or 'not within 60 months'}**. "
                  f"Peak cash need: **{f(r['peak_cash_need'])}**. LTV/CAC {r['unit_economics']['ltv_to_cac']}, "
                  f"CAC payback {r['unit_economics']['cac_payback_months']} months.", "",
                  "| Year | Paying customers | New logos | ARPA/mo | ARR (end) | Revenue | Gross profit | S&M | Other opex | EBITDA | Cash (end) |",
                  "|---|---|---|---|---|---|---|---|---|---|---|"]
        for y in r["years"]:
            lines.append(f"| {y['year']} | {y['paying_customers_end']:,} | {y['new_paying_logos']:,} | ${y['arpa_month_end']:,.0f} | "
                         f"{f(y['arr_end'])} | {f(y['revenue'])} | {f(y['gross_profit'])} | {f(y['s_and_m'])} | "
                         f"{f(y['opex_ex_sm'])} | {f(y['ebitda'])} | {f(y['cash_end'])} |")
        lines.append("")
    lines += ["## Monte Carlo over key drivers (5,000 draws)", "",
              f"- Y5 ARR: P10 {f(mc['arr5_p10'])}, P50 {f(mc['arr5_p50'])}, P90 {f(mc['arr5_p90'])}",
              f"- P(break-even within 60 months): {mc['p_breakeven_within_60m']:.0%}; median break-even month when reached: {mc['breakeven_month_p50_given_reached']}",
              f"- Peak cash need: P50 {f(mc['peak_cash_need_p50'])}, P90 {f(mc['peak_cash_need_p90'])}", ""]
    (HERE / "scenarios.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
