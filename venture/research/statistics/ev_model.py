"""Probability-weighted expected-value model for surviving candidates.

EV_i = sum_j P(outcome_j | evidence) * EconomicValue(outcome_j) - Investment_i,
estimated by Monte Carlo over the parameter distributions in ev_params.json.

Outcome dimensions sampled per draw:
  * regime persistence (Bernoulli) and the year a regime break occurs
  * competitive compression (Bernoulli) scaling penetration
  * continuous uncertainty in reach, penetration, ARPA, margin, churn,
    expansion, CAC, time-to-revenue, opex, exit multiple

Outputs: research/statistics/ev_results.json and ev_results.md
Run:  python research/statistics/ev_model.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).parent
N_DRAWS = 20000
SEED = 20260930
YEARS = 5
# S-curve share of Y5 penetration reached by end of each year (logistic-like)
RAMP = np.array([0.06, 0.2, 0.42, 0.7, 1.0])


def tri(rng, spec, size):
    lo, mode, hi = spec
    if hi == lo:
        return np.full(size, lo, dtype=float)
    c = (mode - lo) / (hi - lo)
    return stats.triang.rvs(c, loc=lo, scale=hi - lo, size=size, random_state=rng)


def simulate(p: dict, meta: dict, rng: np.random.Generator, n: int = N_DRAWS) -> dict:
    draws = {
        "reachable_accounts": tri(rng, p["reachable_accounts"], n),
        "y5_penetration": tri(rng, p["y5_penetration"], n),
        "arpa_usd": tri(rng, p["arpa_usd"], n),
        "gross_margin": tri(rng, p["gross_margin"], n),
        "annual_churn": tri(rng, p["annual_churn"], n),
        "nrr_expansion": tri(rng, p["nrr_expansion"], n),
        "cac_usd": tri(rng, p["cac_usd"], n),
        "months_to_first_revenue": tri(rng, p["months_to_first_revenue"], n),
        "p_regime_persists": tri(rng, p["p_regime_persists"], n),
        "p_competitive_compression": tri(rng, p["p_competitive_compression"], n),
        "opex_base": tri(rng, meta["opex_base_per_year_usd"], n),
        "opex_var": tri(rng, meta["opex_variable_share_of_revenue"], n),
        "launch_investment": tri(rng, meta["launch_investment_usd"], n),
        "exit_multiple": tri(rng, meta["exit_multiple_arr"], n),
    }
    regime_ok = rng.random(n) < draws["p_regime_persists"]
    break_year = rng.integers(2, YEARS + 1, size=n)  # year the regime breaks (if it does)
    compressed = rng.random(n) < draws["p_competitive_compression"]
    pen5 = draws["y5_penetration"] * np.where(compressed, p["compression_penetration_factor"], 1.0)
    target_customers = draws["reachable_accounts"][:, None] * pen5[:, None] * RAMP[None, :]

    # delay: months to first revenue shifts the ramp; fraction of year-1 lost
    delay_frac = np.clip(draws["months_to_first_revenue"] / 12.0, 0, 1.5)
    ramp_shift = np.clip(1 - delay_frac * 0.5, 0.3, 1.0)
    target_customers *= ramp_shift[:, None]

    churn = draws["annual_churn"]
    active_years = p.get("active_years", YEARS)
    revenue = np.zeros((n, YEARS))
    new_logos = np.zeros((n, YEARS))
    customers_end = np.zeros((n, YEARS))
    prev = np.zeros(n)
    for t in range(YEARS):
        if t >= active_years:
            tgt = np.zeros(n)
        else:
            tgt = target_customers[:, t]
        retained = prev * (1 - churn)
        adds = np.maximum(tgt - retained, 0.0) if t < active_years else np.zeros(n)
        end = retained + adds
        arpa_t = draws["arpa_usd"] * (1 + draws["nrr_expansion"]) ** t
        factor = np.where((~regime_ok) & (t + 1 >= break_year), p["regime_break_revenue_factor"], 1.0)
        avg_cust = (prev + end) / 2 if p.get("recurring", True) else adds
        rev = avg_cust * arpa_t * factor
        if t == 0:
            rev *= np.clip(1 - delay_frac, 0.0, 1.0)
        revenue[:, t] = rev
        new_logos[:, t] = adds
        customers_end[:, t] = end
        prev = end

    growth = np.array([1.25 ** t for t in range(YEARS)])
    opex = draws["opex_base"][:, None] * growth[None, :] + draws["opex_var"][:, None] * revenue
    gross_profit = revenue * draws["gross_margin"][:, None]
    s_and_m = new_logos * draws["cac_usd"][:, None]
    contribution = gross_profit - s_and_m
    cash_flow = contribution - opex
    disc = np.array([(1 + meta["discount_rate"]) ** -(t + 1) for t in range(YEARS)])
    arr5 = customers_end[:, -1] * draws["arpa_usd"] * (1 + draws["nrr_expansion"]) ** (YEARS - 1)
    arr5 *= np.where(~regime_ok, p["regime_break_revenue_factor"], 1.0)
    if not p.get("recurring", True):
        arr5 = np.zeros(n)
    # Retention-adjusted exit multiple: buyers pay less for leaky revenue.
    mode_churn = p["annual_churn"][1]
    retention_adj = np.clip((1 - churn) / max(1 - mode_churn, 1e-9), 0.6, 1.2)
    terminal = arr5 * draws["exit_multiple"] * retention_adj * disc[-1]
    npv = -draws["launch_investment"] + (cash_flow * disc[None, :]).sum(axis=1) + terminal
    cum = np.cumsum(np.concatenate([-draws["launch_investment"][:, None], cash_flow], axis=1), axis=1)
    capital_required = -np.minimum(cum.min(axis=1), 0)
    return {
        "draws": draws, "npv": npv, "arr5": arr5, "revenue": revenue,
        "capital_required": capital_required, "cash_flow": cash_flow,
        "customers_end": customers_end, "contribution": contribution,
    }


def summarize(label: str, res: dict) -> dict:
    npv, arr5 = res["npv"], res["arr5"]
    sens = {}
    for k, v in res["draws"].items():
        if np.std(v) > 0:
            rho, _ = stats.spearmanr(v, npv)
            sens[k] = round(float(rho), 3)
    sens = dict(sorted(sens.items(), key=lambda kv: -abs(kv[1])))
    q = lambda a, x: float(np.percentile(a, x))
    return {
        "label": label,
        "npv_mean": float(npv.mean()),
        "npv_mean_se": float(npv.std(ddof=1) / np.sqrt(len(npv))),
        "npv_p10": q(npv, 10), "npv_p50": q(npv, 50), "npv_p90": q(npv, 90),
        "p_npv_positive": float((npv > 0).mean()),
        "arr5_p10": q(arr5, 10), "arr5_p50": q(arr5, 50), "arr5_p90": q(arr5, 90),
        "p_arr5_over_10m": float((arr5 > 10e6).mean()),
        "capital_required_p50": q(res["capital_required"], 50),
        "capital_required_p90": q(res["capital_required"], 90),
        "revenue_by_year_p50": [q(res["revenue"][:, t], 50) for t in range(YEARS)],
        "spearman_sensitivity": sens,
    }


def tornado(p: dict, meta: dict, keys: list[str]) -> list[dict]:
    """One-at-a-time swing: each param at lo/hi, others at mode, regime intact,
    no compression (deterministic single-path)."""
    base = {k: (v[1] if isinstance(v, list) and len(v) == 3 else v) for k, v in p.items()}
    mbase = {k: (v[1] if isinstance(v, list) and len(v) == 3 else v) for k, v in meta.items()}

    def run(pp, mm):
        spec = {k: ([v, v, v] if isinstance(v, (int, float)) and not isinstance(v, bool) and k not in (
            "regime_break_revenue_factor", "compression_penetration_factor", "active_years") else v)
                for k, v in pp.items()}
        spec["p_regime_persists"] = [1.0, 1.0, 1.0]
        spec["p_competitive_compression"] = [0.0, 0.0, 0.0]
        mspec = dict(meta)
        for k in ("opex_base_per_year_usd", "opex_variable_share_of_revenue", "launch_investment_usd", "exit_multiple_arr"):
            v = mm[k]
            mspec[k] = [v, v, v]
        r = simulate(spec, mspec, np.random.default_rng(0), n=1)
        return float(r["npv"][0])

    ref = run(base, mbase)
    rows = []
    for k in keys:
        if k in p:
            lo, _, hi = p[k]
            v_lo = run({**base, k: lo}, mbase)
            v_hi = run({**base, k: hi}, mbase)
        else:
            lo, _, hi = meta[k]
            v_lo = run(base, {**mbase, k: lo})
            v_hi = run(base, {**mbase, k: hi})
        rows.append({"param": k, "low_value": lo, "high_value": hi, "npv_at_low": v_lo,
                     "npv_at_high": v_hi, "swing": abs(v_hi - v_lo)})
    rows.sort(key=lambda r: -r["swing"])
    return [{"base_npv": ref}] + rows


def main() -> None:
    cfg = json.loads((HERE / "ev_params.json").read_text())
    meta = cfg["_meta"]
    rng = np.random.default_rng(SEED)
    results = {}
    for cid, p in cfg["candidates"].items():
        results[cid] = summarize(p["label"], simulate(p, meta, rng))
    ranking = sorted(results, key=lambda k: -results[k]["npv_mean"])
    tkeys = ["reachable_accounts", "y5_penetration", "arpa_usd", "gross_margin", "annual_churn",
             "nrr_expansion", "cac_usd", "months_to_first_revenue", "opex_base_per_year_usd",
             "exit_multiple_arr"]
    torn = tornado(cfg["candidates"][ranking[0]], meta, tkeys)
    out = {"seed": SEED, "draws": N_DRAWS, "ranking": ranking, "results": results,
           "tornado_leader": {"candidate": ranking[0], "rows": torn}}
    (HERE / "ev_results.json").write_text(json.dumps(out, indent=2))

    m = lambda x: f"${x/1e6:,.1f}M"
    lines = ["# EV model results", "",
             f"Monte Carlo draws per candidate: {N_DRAWS:,}; seed {SEED}; discount rate "
             f"{meta['discount_rate']:.0%}; horizon {meta['horizon_years']} years + terminal value on Y5 ARR.", "",
             "All inputs are [M] model assumptions tied to benchmarks in `ev_params.json`. Outputs are model results, not forecasts.", "",
             "| Rank | Candidate | Mean NPV (±SE) | P10 | P50 | P90 | P(NPV>0) | Y5 ARR P50 | P(ARR5>$10M) | Capital req. P50 / P90 |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for i, k in enumerate(ranking, 1):
        r = results[k]
        lines.append(f"| {i} | {r['label']} | {m(r['npv_mean'])} (±{m(r['npv_mean_se'])}) | {m(r['npv_p10'])} | "
                     f"{m(r['npv_p50'])} | {m(r['npv_p90'])} | {r['p_npv_positive']:.0%} | {m(r['arr5_p50'])} | "
                     f"{r['p_arr5_over_10m']:.0%} | {m(r['capital_required_p50'])} / {m(r['capital_required_p90'])} |")
    lines += ["", "## Global sensitivity (Spearman rank correlation of input with NPV)", ""]
    for k in ranking:
        top = list(results[k]["spearman_sensitivity"].items())[:5]
        lines.append(f"- **{results[k]['label']}**: " + ", ".join(f"{a} {b:+.2f}" for a, b in top))
    lines += ["", f"## Tornado for leader ({results[ranking[0]]['label']})", "",
              f"Deterministic path at modal values, regime intact, no compression: base NPV {m(torn[0]['base_npv'])}.", "",
              "| Parameter | Low | High | NPV at low | NPV at high | Swing |", "|---|---|---|---|---|---|"]
    for r in torn[1:]:
        lines.append(f"| {r['param']} | {r['low_value']} | {r['high_value']} | {m(r['npv_at_low'])} | "
                     f"{m(r['npv_at_high'])} | {m(r['swing'])} |")
    (HERE / "ev_results.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
