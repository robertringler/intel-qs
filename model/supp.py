#!/usr/bin/env python3
"""Supplementary: wide Monte Carlo, strict-$0 detail, dossier reconciliation."""
import io, contextlib, importlib.util, sys, random, statistics as st_
from dataclasses import replace
spec=importlib.util.spec_from_file_location("fin","final.py")
fin=importlib.util.module_from_spec(spec); sys.modules["fin"]=fin
with contextlib.redirect_stdout(io.StringIO()): spec.loader.exec_module(fin)
BASE,DOWN,UP,run,M,bpm = fin.BASE,fin.DOWN,fin.UP,fin.run,fin.M,fin.bpm

L=lambda n:f"\n{'='*92}\n{n}\n{'='*92}"

# ---------------------------------------------------------------- WIDE MC
print(L("TABLE 6b — WIDE MONTE CARLO (structural + execution variance, 20,000 draws)"))
print("  Table 6 sampled 9 drivers around the BASE business DESIGN, so it measured")
print("  execution variance only and could not reach the upside. This run also samples")
print("  the structural levers (attach rates, headcount plan scale, pricing, delivery")
print("  productivity) across the full downside-to-upside range. [ASSUMPTION] throughout.")
random.seed(7)
tri=lambda a,m,b: random.triangular(a,b,m)
N=20000; revs=[];ebs=[];caps=[];ftes=[]
for _ in range(N):
    hscale=tri(0.35,1.0,1.75)       # headcount plan scale
    s=replace(BASE,
      brk_mils=tri(0.00020,0.00050,0.00095),
      brk_attach=tri(0.14,0.35,0.52),
      brk_attr=tri(0.12,0.22,0.36),
      flex_attach=tri(0.06,0.20,0.34),
      flex_mw_rev=[0,0,round(tri(3000,8000,13000)),round(tri(3500,9000,15000)),
                   round(tri(4000,10000,17000))],
      flex_start=round(tri(2,3,5)),
      mw_per_orig=[0]+[round(tri(.42,1.0,1.60)*v,1) for v in [48,80,100,110]],
      fee_mw=[round(tri(.55,1.0,1.50)*v) for v in [3000,3000,3500,4000,4250]],
      conv=[round(min(.45,tri(.55,1.0,1.50)*v),4) for v in [.12,.16,.18,.19,.20]],
      churn=tri(0.18,0.30,0.48),
      price_screen=[round(tri(.7,1.0,1.35)*v) for v in [12000,14000,15000,15500,16000]],
      ret_annual=[0]+[round(tri(.7,1.0,1.3)*v) for v in [132000,144000,150000,156000]],
      screens_per_del_fte=tri(9,13,17),
      retainers_per_del_fte=tri(1.5,2.2,2.9),
      hc_orig=[round(v*hscale,2) for v in BASE.hc_orig],
      hc_anl=[round(v*hscale,2) for v in BASE.hc_anl],
      hc_ops=[round(v*hscale,2) for v in BASE.hc_ops],
      hc_cmp=[round(v*hscale,2) for v in BASE.hc_cmp],
      flex_cost_per_mw=round(tri(2200,3600,5400)),
      subcontract_rate=tri(0.09,0.14,0.20))
    r=run(s,mode="ebitda")
    revs.append(r[4]["revenue"]); ebs.append(r[4]["ebitda"]); ftes.append(r[4]["fte"])
    caps.append(max(0,-min(x["cum_fcf"] for x in r)))
revs.sort();ebs.sort();caps.sort();ftes.sort()
q=lambda a,p:a[int(p*(len(a)-1))]
print("\n  Year-5 REVENUE")
for p in [.05,.10,.25,.50,.75,.90,.95,.99]: print(f"    P{int(p*100):>2}  {M(q(revs,p)):>12}")
print(f"    mean {M(st_.mean(revs)):>12}")
print("\n  Year-5 EBITDA")
for p in [.05,.10,.25,.50,.75,.90,.95]: print(f"    P{int(p*100):>2}  {M(q(ebs,p)):>12}")
print("\n  Peak capital requirement")
for p in [.10,.25,.50,.75,.90,.95]: print(f"    P{int(p*100):>2}  {M(q(caps,p)):>12}")
print(f"\n  Year-5 FTE  P50 {q(ftes,.5):.0f}   P90 {q(ftes,.9):.0f}")
pr=lambda c:sum(1 for v in revs if c(v))/N*100
print(f"\n  P(Yr5 revenue >= $1M)     {pr(lambda v:v>=1e6):5.1f}%")
print(f"  P(Yr5 revenue >= $5M)     {pr(lambda v:v>=5e6):5.1f}%")
print(f"  P(Yr5 revenue >= $10M)    {pr(lambda v:v>=1e7):5.1f}%")
print(f"  P(Yr5 revenue >= $25M)    {pr(lambda v:v>=2.5e7):5.1f}%")
print(f"  P(Yr5 revenue >= $55M)    {pr(lambda v:v>=5.5e7):5.1f}%   <- dossier base case")
print(f"  P(Yr5 revenue >= $100M)   {pr(lambda v:v>=1e8):5.1f}%")
print(f"  P(Yr5 EBITDA > 0)         {sum(1 for v in ebs if v>0)/N*100:5.1f}%")
print(f"  P(peak capital < $50k)    {sum(1 for v in caps if v<5e4)/N*100:5.1f}%")
print(f"  P(peak capital < $250k)   {sum(1 for v in caps if v<2.5e5)/N*100:5.1f}%")
print(f"  P(peak capital > $1M)     {sum(1 for v in caps if v>1e6)/N*100:5.1f}%")

# ---------------------------------------------------------- STRICT $0 DETAIL
print(L("TABLE 4b — STRICT $0 BASE CASE, YEAR BY YEAR (ending cash never < 0)"))
rc=run(BASE,mode="cash")
print(f"{'':<30}{'Yr1':>12}{'Yr2':>12}{'Yr3':>12}{'Yr4':>12}{'Yr5':>12}")
for lbl,k,f in [("Revenue","revenue","m"),("Gross profit","gross_profit","m"),
  ("EBITDA","ebitda","m"),("Free cash flow","fcf","m"),("Ending cash","cash_end","m"),
  ("FTE","fte","n"),("Hiring factor f","f","n2"),("Founder cash pay","founder_pay","m"),
  ("MW closed","mw_closed","n")]:
    cs="".join(f"{M(x[k]):>12}" if f=="m" else f"{x[k]:>12.2f}" if f=="n2"
               else f"{x[k]:>12.1f}" for x in rc)
    print(f"{lbl:<30}{cs}")
print(f"\n  Founder total cash comp over 5 yrs : "
      f"{M(sum(x['founder_pay'] for x in rc))}")
print(f"  Years founder paid nothing         : "
      f"{sum(1 for x in rc if x['founder_pay']==0)} of 5")
print(f"  Peak cash balance low point        : {M(min(x['cash_end'] for x in rc))}")

# ------------------------------------------------------ DOSSIER RECONCILIATION
print(L("TABLE 10 — RECONCILIATION: DOSSIER YEAR-5 BASE ($55M) vs THIS MODEL ($5.81M)"))
d_flex_mw, d_flex_rate = 1500, 30000
d_brk_gw,  d_brk_mils  = 1.5, 0.002
d_cum_mw               = 25000   # dossier Yr10 figure; Yr5 stated 5,000
print("  The dossier's own Year-5 base line items, priced at its own stated rates:")
print(f"    flexibility  1,500 MW x $30,000/MW-yr            = {M(d_flex_mw*d_flex_rate)}")
print(f"    brokerage    1.5 GW  x 2.0 mils "
      f"({M(bpm(d_brk_mils))}/MW-yr)   = {M(1500*bpm(d_brk_mils))}")
print(f"    subtotal of just those two streams               = "
      f"{M(d_flex_mw*d_flex_rate + 1500*bpm(d_brk_mils))}")
print(f"    ...against a stated TOTAL Year-5 revenue of        $55.00M")
print("  => the dossier's two residual streams alone EXCEED its own stated total,")
print("     before origination fees, retainers or screens. The §16 table was")
print("     internally inconsistent with the §8 unit rates. [FACT - arithmetic]")
print("\n  Decomposition of the 9.5x gap to this model:")
mine=run(BASE,mode="ebitda")[4]
steps=[
 ("Dossier stated Yr5 base revenue", 55.0e6),
 ("Brokerage 2.0 -> 0.5 mils (retail C&I rate does not apply to >150MW loads;\n"
  "     such loads register for direct wholesale access)", None),
 ("Flexibility $30k -> $10k/MW-yr (load owner bears curtailment risk and holds\n"
  "     the leverage; Emerald AI at $1.05bn valuation compresses the software share)", None),
 ("MW under management 1,500 -> 182 (origination is limited by originator\n"
  "     headcount x ramp, which the $0 cash constraint caps)", None),
 ("Residual attrition 8% -> 22% (3-5yr supply contracts are re-bid)", None),
 ("Delivery capacity constraint on screens and retainers (none in dossier)", None),
 ("This model's Yr5 base revenue", mine["revenue"]),
]
for lbl,v in steps:
    print(f"    {lbl:<78} {M(v) if v else '':>10}")
print(f"\n  ROOT CAUSE (single sentence):")
print(f"    The dossier's Year-5 revenue required roughly 5,000 MW of cumulative")
print(f"    origination. At ~110 MW per originator-year that is ~45 originator-years,")
print(f"    i.e. ~15 originators on staff by Year 3 — a payroll of roughly")
print(f"    {M(15*120000*1.24)}/yr that its own $0-capital constraint cannot fund.")
print(f"    The model's Yr5 cumulative origination is "
      f"{sum(x['mw_closed'] for x in run(BASE,mode='ebitda')):,.0f} MW.")
print(f"    The dossier modelled revenue per MW but never modelled who closes the MW.")
