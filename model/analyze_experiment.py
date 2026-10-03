#!/usr/bin/env python3
"""
Experiment 01 analysis: originator throughput (MW closed per originator-year).

Reads responses.csv, computes the decision statistic, applies the no-brand
haircut, tests it against the PRE-REGISTERED thresholds, then re-runs the
five-year model at the measured value and prints the revised Year-5 outcome.

Usage:  python3 analyze_experiment.py [responses.csv]
Run from the model/ directory (final.py loads model4.py by relative path).
"""
import csv, sys, random, statistics as st, io, contextlib, importlib.util
from dataclasses import replace

# ---------------------------------------------------------------- PRE-REGISTERED
# These were fixed BEFORE any data was collected. Do not edit after collection.
KILL_BELOW      = 60     # MW/originator-yr (planning-adjusted): business is a consultancy
CAUTION_BAND    = (60, 90)
MODEL_BASE_MW   = 110    # the assumption under test (BASE mw_per_orig steady state)
HAIRCUT_RANGE   = (0.50, 0.70)   # no-brand startup vs established-firm originator
MIN_VALID_N     = 10
# -------------------------------------------------------------------------------

PATH = sys.argv[1] if len(sys.argv) > 1 else "responses.csv"

def f(row, key, default=None):
    v = (row.get(key) or "").strip()
    if v == "" or v.lower() in ("na", "n/a", "unknown", "-1"): return default
    try: return float(v)
    except ValueError: return default

def load(path):
    rows = []
    with open(path, newline="") as fh:
        for r in csv.DictReader(fh):
            if not (r.get("id") or "").strip(): continue
            if (r.get("id") or "").strip().startswith("#"): continue
            rows.append(r)
    return rows

def classify(rows):
    valid, excluded = [], []
    for r in rows:
        why = []
        if f(r, "is_individual") != 1: why.append("team-level not individual")
        if (f(r, "yrs_experience") or 0) < 2: why.append("<2 yrs experience")
        yc = f(r, "years_covered")
        mw = f(r, "mw_closed_total")
        if yc is None or yc < 1: why.append("no period given")
        if mw is None: why.append("no MW figure")
        if why: excluded.append((r.get("id"), "; ".join(why)))
        else:
            r["_mw_yr"] = mw / yc
            valid.append(r)
    return valid, excluded

def boot_ci(xs, stat=st.median, n=20000, lo=5, hi=95, seed=11):
    random.seed(seed)
    s = sorted(stat(random.choices(xs, k=len(xs))) for _ in range(n))
    return s[int(lo/100*(n-1))], s[int(hi/100*(n-1))]

def pct(xs, p):
    s = sorted(xs); k = (len(s)-1)*p/100
    i = int(k); frac = k-i
    return s[i] if i+1 >= len(s) else s[i]*(1-frac)+s[i+1]*frac

def money(x):
    neg = x < 0; v = abs(x)
    t = f"${v/1e6:,.2f}M" if v>=1e6 else (f"${v/1e3:,.0f}k" if v>=1000 else f"${v:,.0f}")
    return f"({t})" if neg else t

def rerun_model(mw_steady):
    """Re-run the five-year model with measured originator throughput."""
    spec = importlib.util.spec_from_file_location("fin", "final.py")
    fin = importlib.util.module_from_spec(spec); sys.modules["fin"] = fin
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(fin)
    scale = mw_steady / MODEL_BASE_MW
    s = replace(fin.BASE, mw_per_orig=[round(v*scale, 1) for v in fin.BASE.mw_per_orig])
    disciplined = fin.run(s, mode="ebitda")
    strict      = fin.run(s, mode="cash")
    return disciplined, strict, fin

# ============================================================== REPORT
print("="*84)
print("EXPERIMENT 01 — ORIGINATOR THROUGHPUT: ANALYSIS")
print("="*84)
print(f"Pre-registered kill threshold : < {KILL_BELOW} MW/originator-yr (planning-adjusted)")
print(f"Pre-registered caution band   : {CAUTION_BAND[0]}-{CAUTION_BAND[1]} MW")
print(f"Assumption under test         : {MODEL_BASE_MW} MW (model BASE steady state)")
print(f"No-brand haircut              : x{HAIRCUT_RANGE[0]:.2f} to x{HAIRCUT_RANGE[1]:.2f}")

try:
    rows = load(PATH)
except FileNotFoundError:
    print(f"\nNo data file at '{PATH}'. Collect responses first; schema is in that file's header.")
    sys.exit(0)

valid, excluded = classify(rows)
print(f"\nResponses logged : {len(rows)}")
print(f"Valid for the statistic : {len(valid)}")
if excluded:
    print(f"Excluded : {len(excluded)}")
    for i, w in excluded[:12]: print(f"    {i}: {w}")

if not valid:
    print("\nNothing valid yet — no statistic computable.")
    sys.exit(0)

xs = [r["_mw_yr"] for r in valid]
med, mean = st.median(xs), st.mean(xs)
p25, p75 = pct(xs, 25), pct(xs, 75)
print(f"\n--- RAW (as reported by established-firm originators) ---")
print(f"  n          {len(xs)}")
print(f"  median     {med:,.0f} MW/originator-yr      <- decision statistic")
print(f"  mean       {mean:,.0f}   (mean/median = {mean/med:.2f}x)")
print(f"  IQR        {p25:,.0f} - {p75:,.0f}")
print(f"  min / max  {min(xs):,.0f} / {max(xs):,.0f}")
if len(xs) >= 4:
    lo, hi = boot_ci(xs)
    print(f"  90% bootstrap CI on median : {lo:,.0f} - {hi:,.0f} MW")
if mean/med > 1.4:
    print("  NOTE: mean >> median — distribution is right-skewed (a few large deals).")
    print("        Use the MEDIAN. Planning on the mean would import tail outcomes")
    print("        that a single new originator cannot rely on.")
if len(xs) < MIN_VALID_N:
    print(f"  WARNING: n={len(xs)} < {MIN_VALID_N}. Treat as directional only.")

h_lo, h_hi = HAIRCUT_RANGE
plan_lo, plan_hi = med*h_lo, med*h_hi
plan_mid = med*((h_lo+h_hi)/2)
print(f"\n--- PLANNING-ADJUSTED (what a no-brand startup should assume) ---")
print(f"  median {med:,.0f} x haircut {h_lo:.2f}-{h_hi:.2f} = {plan_lo:,.0f} - {plan_hi:,.0f} MW")
print(f"  midpoint used for the decision : {plan_mid:,.0f} MW/originator-yr")

print(f"\n--- DECISION ---")
if plan_hi < KILL_BELOW:
    verdict = "KILL"
    print(f"  KILL. Even the favourable end of the planning range ({plan_hi:,.0f} MW) is")
    print(f"  below the {KILL_BELOW} MW threshold. The business cannot exceed roughly $2M of")
    print(f"  Year-5 revenue and is a consultancy, not a platform. Do not proceed on")
    print(f"  the origination thesis; the residual streams never reach scale.")
elif plan_lo < KILL_BELOW <= plan_hi:
    verdict = "INCONCLUSIVE"
    print(f"  INCONCLUSIVE. The planning range straddles the {KILL_BELOW} MW threshold")
    print(f"  ({plan_lo:,.0f}-{plan_hi:,.0f}). Collect 8-10 more interviews, weighted toward the")
    print(f"  segment you would actually hire from, before committing.")
elif plan_mid < CAUTION_BAND[1]:
    verdict = "CAUTION"
    print(f"  CAUTION. {plan_mid:,.0f} MW clears the kill line but sits in the {CAUTION_BAND[0]}-"
          f"{CAUTION_BAND[1]} MW band.")
    print(f"  Viable, materially smaller than the base case. Re-plan at the measured figure.")
else:
    verdict = "PROCEED"
    print(f"  PROCEED. {plan_mid:,.0f} MW clears the caution band. The origination thesis")
    print(f"  survives this test.")
    if plan_mid < MODEL_BASE_MW:
        print(f"  BUT NOTE: {plan_mid:,.0f} MW is still below the {MODEL_BASE_MW} MW the model assumed,")
        print(f"  so re-plan at the measured figure — the base case was optimistic.")

print(f"\n--- FIVE-YEAR MODEL RE-RUN AT {plan_mid:,.0f} MW/ORIGINATOR-YR ---")
try:
    d, s_, fin = rerun_model(plan_mid)
    print(f"{'':<26}{'Yr1':>11}{'Yr2':>11}{'Yr3':>11}{'Yr4':>11}{'Yr5':>11}")
    for lbl, k in [("Revenue","revenue"),("Gross profit","gross_profit"),
                   ("EBITDA","ebitda"),("Free cash flow","fcf"),("Cumulative FCF","cum_fcf")]:
        print(f"{lbl:<26}"+"".join(f"{money(x[k]):>11}" for x in d))
    r5 = d[4]
    resid = (r5["rev_brk"]+r5["rev_flx"])/r5["revenue"] if r5["revenue"] else 0
    rl, rh = (1.0, 2.0) if resid < 0.25 else (2.0, 3.5)
    cap = max(0, -min(x["cum_fcf"] for x in d))
    print(f"\n  Year-5 revenue            {money(r5['revenue'])}   "
          f"(model BASE was {money(5.81e6)})")
    print(f"  Year-5 EBITDA             {money(r5['ebitda'])} "
          f"({r5['ebitda']/r5['revenue']*100:.1f}% margin)")
    print(f"  Year-5 FTE                {r5['fte']:.1f}")
    print(f"  5y cumulative MW          {sum(x['mw_closed'] for x in d):,.0f} MW")
    print(f"  Peak capital required     {money(cap)}")
    print(f"  Residual revenue mix      {resid*100:.0f}%")
    print(f"  Implied EV ({rl}-{rh}x rev)  {money(r5['revenue']*rl)} - {money(r5['revenue']*rh)}")
    print(f"  Strict-$0 Year-5 revenue  {money(s_[4]['revenue'])}")
except Exception as e:
    print(f"  [model re-run unavailable: {e}]")

# ------------------------------------------------- piggybacked falsifiers
print(f"\n--- PIGGYBACKED FALSIFIERS (same conversations, zero marginal cost) ---")
def summarise(key, label, unit="", scale=1.0):
    vals = [f(r, key) for r in rows]
    vals = [v*scale for v in vals if v is not None]
    if not vals:
        print(f"  {label:<44} no data yet"); return
    print(f"  {label:<44} n={len(vals):<3} median {st.median(vals):,.2f}{unit} "
          f"(range {min(vals):,.2f}-{max(vals):,.2f}{unit})")
summarise("q_wtp_screen_usd", "§19.2 Would pay for a screen ($)")
wtp = [f(r,"q_wtp_screen_usd") for r in rows]
wtp = [v for v in wtp if v is not None]
if wtp:
    yes = sum(1 for v in wtp if v > 0)
    print(f"  {'      -> said yes at any price':<44} {yes}/{len(wtp)} "
          f"({yes/len(wtp)*100:.0f}%)")
summarise("q_broker_mils_large", "§19.3 Broker mils paid on >50MW loads", " mils")
summarise("q_broker_cutoff_mw", "§19.3 MW above which no retail broker fee", " MW")
summarise("q_flex_share_pct", "§19.4 Flexibility value conceded to 3rd party", "%")
summarise("q_dso_days", "§19.5 Payment terms to small vendors", " days")
summarise("cycle_months_median", "Sales cycle (origination)", " months")
summarise("close_rate_pct", "Close rate on live opportunities", "%")

seg = {}
for r in valid: seg.setdefault(r.get("segment","?"), []).append(r["_mw_yr"])
print(f"\n--- BY SEGMENT (watch for the sample skewing to one type) ---")
for k, v in sorted(seg.items(), key=lambda x: -len(x[1])):
    print(f"  {k:<20} n={len(v):<3} median {st.median(v):,.0f} MW")
print(f"\nVERDICT: {verdict}")
