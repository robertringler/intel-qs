#!/usr/bin/env python3
"""
FINAL: five-year model + unit economics + break-even + sensitivity +
Monte Carlo + market share + valuation. Located-firm-capacity origination.
Adversarial build from the Strategic Research Dossier.
"""
import json, random, statistics as st_
from dataclasses import replace
import importlib.util, sys

spec = importlib.util.spec_from_file_location("m4", "model4.py")
m4 = importlib.util.module_from_spec(spec)
sys.modules["m4"] = m4
# suppress m4's own printing
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(m4)

S, BASE, DOWN, UP = m4.S, m4.BASE, m4.DOWN, m4.UP
bpm, YEARS, IDX, M = m4.bpm, m4.YEARS, m4.IDX, m4.M

# ---- fix: reserve 25% of delivery capacity for screens (lead-gen product) ----
_orig_year_pl = m4.year_pl
def year_pl(s, y, f, fsal, st):
    o = _orig_year_pl(s, y, f, fsal, st)
    dfte = o["delivery_fte"]
    if dfte <= 0 or s.retainers_per_del_fte <= 0: return o
    scr_reserved = dfte * 0.25
    ret_cap_fte = dfte - scr_reserved
    ret_c = min(o["ret_demand"], ret_cap_fte * s.retainers_per_del_fte)
    fte_ret = ret_c / s.retainers_per_del_fte
    fte_scr = max(0.0, dfte - fte_ret)
    screens = min(o["scr_demand"], fte_scr * s.screens_per_del_fte)
    # rebuild revenue with corrected allocation
    o["ret_c"], o["screens"] = ret_c, screens
    o["rev_ret"] = ret_c * s.ret_annual[y]
    o["rev_scr"] = screens * s.price_screen[y]
    o["cap_util"] = (fte_ret + screens / s.screens_per_del_fte) / dfte
    rev = o["rev_scr"] + o["rev_ret"] + o["rev_suc"] + o["rev_brk"] + o["rev_flx"]
    o["revenue"] = rev
    B = 1 + s.burden
    o["cogs_sub"] = (o["rev_scr"] + o["rev_ret"]) * s.subcontract_rate
    o["cogs"] = o["cogs_labour"] + o["cogs_sub"] + o["cogs_settle"] + o["cogs_am"]
    o["gross_profit"] = rev - o["cogs"]
    o["commission"] = (o["rev_suc"] + o["rev_brk"]) * s.comm_rate
    nps = 0.15 + 0.85 * f
    pers = {k: o["hc"][k] * s.sal[k] * B for k in o["hc"]}
    o["sm"] = pers["orig"] + o["commission"] + (s.travel[y] + s.mktg[y]) * nps
    o["opex"] = o["sm"] + o["rnd"] + o["opsx"] + o["gna"]
    o["ebitda"] = o["gross_profit"] - o["opex"]
    return o
m4.year_pl = year_pl

def run(s, bootstrap=True, funding=0.0, mode="ebitda"):
    """mode 'ebitda' = hire while EBITDA loss is fundable (ignores WC).
       mode 'cash'   = STRICT $0: ending cash must stay >= 0 every year."""
    state = {"cust":0.,"brk_mw":0.,"flex_mw":0.,"ar":0.,"orig_fte":0.}
    cash = s.seed_cash + funding; rows=[]; cum=0.
    for y in IDX:
        def cashflow(o):
            da = s.capex[y]*o["_f"]*0.45
            ebit = o["ebitda"]-da; tax = max(0.,ebit)*s.tax
            ar = o["revenue"]*s.dso/365; wc = ar-state["ar"]
            coll = (s.collateral[y]-(s.collateral[y-1] if y>0 else 0))*o["_f"]
            cx = s.capex[y]*o["_f"]
            fcf = o["revenue"]-(o["cogs"]+o["opex"]+tax)-wc-cx-coll
            return da, ebit, tax, ar, wc, coll, cx, fcf
        def trial(f, fs):
            o = year_pl(s, y, f, fs, state); o["_f"]=f; return o
        def ok(o):
            if mode=="ebitda": return o["ebitda"] >= -cash
            return cash + cashflow(o)[7] >= 0
        if not bootstrap:
            o = trial(1.0,1.0)
        else:
            o = trial(1.0,1.0)
            if not ok(o):
                lo,hi=0.,1.
                for _ in range(45):
                    mid=(lo+hi)/2
                    if ok(trial(1.0,mid)): lo=mid
                    else: hi=mid
                o = trial(1.0,lo)
                if not ok(o):
                    lo,hi=0.,1.
                    for _ in range(50):
                        mid=(lo+hi)/2
                        if ok(trial(mid,0.)): lo=mid
                        else: hi=mid
                    o = trial(lo,0.)
        da,ebit,tax,ar,wc,coll,cx,fcf = cashflow(o)
        cb=cash; cash=cb+fcf; cum+=fcf
        assert abs((cb+fcf)-cash)<1e-6
        o.update(f=o["_f"], da=da, ebit=ebit, tax=tax, net_income=ebit-tax, ar=ar,
                 wc=wc, coll=coll, capex=cx, fcf=fcf, cash_begin=cb,
                 cash_end=cash, cum_fcf=cum)
        rows.append(o)
        state.update(cust=o["cust_end"], brk_mw=o["brk_mw"], flex_mw=o["flex_mw"],
                     ar=ar, orig_fte=o["hc"]["orig"])
    return rows

SC={"DOWNSIDE":DOWN,"BASE":BASE,"UPSIDE":UP}
R  ={k:run(v,mode="ebitda") for k,v in SC.items()}      # disciplined bootstrap
RC ={k:run(v,mode="cash")   for k,v in SC.items()}      # strict $0
RF ={k:run(v,bootstrap=False,funding=3_000_000) for k,v in SC.items()}  # funded

L=lambda n:f"\n{'='*92}\n{n}\n{'='*92}"

print(L("TABLE 1 — FIVE-YEAR REVENUE & P&L (disciplined bootstrap, no external capital)"))
for n in ["DOWNSIDE","BASE","UPSIDE"]:
    r=R[n]; s=SC[n]
    print(f"\n--- {n}  (brokerage {s.brk_mils*1000:.2f} mils = {M(bpm(s.brk_mils))}/MW-yr; "
          f"flex from Yr{s.flex_start}) ---")
    print(f"{'':<34}{'Yr1':>11}{'Yr2':>11}{'Yr3':>11}{'Yr4':>11}{'Yr5':>11}")
    for lbl,k,f in [("Customers (end)","cust_end","n1"),("New customers","cust_new","n1"),
        ("Churned","cust_churn","n1"),("MW closed (annual)","mw_closed","n0"),
        ("MW brokered (cum)","brk_mw","n0"),("MW flexibility (cum)","flex_mw","n0"),
        ("1 Screens","rev_scr","m"),("2 Retainers","rev_ret","m"),
        ("3 Success fees","rev_suc","m"),("4 Brokerage residual","rev_brk","m"),
        ("5 Flexibility","rev_flx","m"),("TOTAL REVENUE","revenue","m"),
        ("COGS","cogs","m"),("Gross profit","gross_profit","m"),
        ("S&M","sm","m"),("R&D","rnd","m"),("Operations","opsx","m"),("G&A","gna","m"),
        ("Total OpEx","opex","m"),("EBITDA","ebitda","m"),("D&A","da","m"),
        ("EBIT","ebit","m"),("Taxes","tax","m"),("Net income","net_income","m"),
        ("FTE","fte","n1"),("Free cash flow","fcf","m"),("Cumulative FCF","cum_fcf","m")]:
        cs="".join(f"{M(x[k]):>11}" if f=="m" else f"{x[k]:>11.1f}" if f=="n1"
                   else f"{x[k]:>11.0f}" for x in r)
        print(f"{lbl:<34}{cs}")
    print(f"{'Gross margin':<34}"+"".join(f"{x['gross_profit']/x['revenue']*100:>10.1f}%" for x in r))
    print(f"{'EBITDA margin':<34}"+"".join(f"{x['ebitda']/x['revenue']*100:>10.1f}%" for x in r))
    print(f"{'Revenue / FTE':<34}"+"".join(f"{M(x['revenue']/x['fte']):>11}" for x in r))
    print(f"{'Founder cash pay':<34}"+"".join(f"{M(x['founder_pay']):>11}" for x in r))

print(L("TABLE 2 — CORE UNIT ECONOMICS"))
def unit_econ(s, name):
    yi=2  # year 3 steady-ish
    fee=s.fee_mw[yi]
    b_rate=bpm(s.brk_mils); b_life=1/s.brk_attr
    f_rev=s.flex_mw_rev[4]; f_life=1/s.flex_attr
    d=0.15
    def ann(rate, life):            # discounted annuity factor
        return sum(1/(1+d)**t for t in range(1,int(round(life))+1))
    b_npv=s.brk_attach*b_rate*ann(b_rate,b_life)
    f_npv=s.flex_attach*f_rev*ann(f_rev,f_life)
    rev_mw=fee+b_npv+f_npv
    # cost per MW over life
    b_cost=s.brk_attach*s.brk_cost_per_mw*ann(0,b_life)
    f_cost=s.flex_attach*s.flex_cost_per_mw*ann(0,f_life)
    am=((s.brk_attach*b_life+s.flex_attach*f_life)/s.mw_per_am_fte)*s.sal["ops"]*(1+s.burden)
    comm=(fee+b_npv)*s.comm_rate
    cost_mw=b_cost+f_cost+am+comm
    gp_mw=rev_mw-cost_mw
    print(f"\n--- {name} : ECONOMICS PER MW ORIGINATED (NPV @15%) ---")
    print(f"  Success fee (one-time)                       {M(fee):>12}")
    print(f"  + Brokerage residual NPV ({s.brk_attach:.0%} attach x "
          f"{M(b_rate)}/MW-yr x {b_life:.1f}y) {M(b_npv):>12}")
    print(f"  + Flexibility NPV ({s.flex_attach:.0%} attach x "
          f"{M(f_rev)}/MW-yr x {f_life:.1f}y)   {M(f_npv):>12}")
    print(f"  = LIFETIME REVENUE PER MW                    {M(rev_mw):>12}")
    print(f"  - residual carrying + account mgmt + commission {M(cost_mw):>9}")
    print(f"  = LIFETIME GROSS PROFIT PER MW               {M(gp_mw):>12}   "
          f"(margin {gp_mw/rev_mw*100:.0f}%)")
    print(f"  Powered-land benchmark price   $584,000/MW  [VERIFY]")
    print(f"  --> originator captures {rev_mw/584000*100:.2f}% of asset value unlocked")
    # customer-level
    r=R[name]; y5=r[4]
    newc=sum(x["cust_new"] for x in r)
    sm=sum(x["sm"] for x in r)
    cac=sm/newc if newc else 0
    arpu=y5["revenue"]/y5["cust_avg"] if y5["cust_avg"] else 0
    gm=y5["gross_profit"]/y5["revenue"]
    life=1/s.churn
    ltv=arpu*gm*life
    print(f"\n  CAC  = 5y S&M {M(sm)} / {newc:.0f} new customers        = {M(cac)}")
    print(f"  ARPU = Yr5 rev {M(y5['revenue'])} / {y5['cust_avg']:.0f} avg custs  = {M(arpu)}")
    print(f"  Gross margin                                         = {gm*100:.0f}%")
    print(f"  Customer life = 1/churn = 1/{s.churn:.2f}                   = {life:.1f} yrs")
    print(f"  LTV  = ARPU x GM x life                              = {M(ltv)}")
    print(f"  LTV/CAC                                              = {ltv/cac:.1f}x" if cac else "")
    print(f"  CAC payback = CAC / (ARPU x GM)                      = "
          f"{cac/(arpu*gm)*12:.1f} months" if arpu*gm>0 else "")
    return dict(rev_mw=rev_mw, gp_mw=gp_mw, cac=cac, ltv=ltv)
UE={n:unit_econ(SC[n],n) for n in ["DOWNSIDE","BASE","UPSIDE"]}

print(L("TABLE 3 — BREAK-EVEN (Year-5 cost structure, BASE)"))
b=R["BASE"][4]; s=BASE
fixed=b["opex"]-b["commission"]
cm=(b["gross_profit"]-b["commission"])/b["revenue"]
print(f"  Fixed opex (Yr5 OpEx less commission)      = {M(fixed)}")
print(f"  Contribution margin = (GP - commission)/rev = {cm*100:.1f}%")
print(f"  BREAK-EVEN REVENUE = fixed / CM             = {M(fixed/cm)}")
print(f"  Actual Yr5 revenue                          = {M(b['revenue'])}  "
      f"({b['revenue']/(fixed/cm):.2f}x break-even)")
print(f"  Break-even in retainer-equivalents  @{M(s.ret_annual[4])}/yr = "
      f"{fixed/cm/s.ret_annual[4]:.0f} clients")
print(f"  Break-even in MW originated (success fee only @{M(s.fee_mw[4])}/MW) = "
      f"{fixed/cm/s.fee_mw[4]:,.0f} MW/yr")
print(f"  Break-even in screens @{M(s.price_screen[4])} = {fixed/cm/s.price_screen[4]:,.0f}/yr")

print(L("TABLE 4 — CAPITAL REQUIREMENT: disciplined bootstrap vs STRICT $0 vs funded"))
print(f"{'':<40}{'Downside':>17}{'Base':>17}{'Upside':>17}")
def cr(l,fn,src):
    print(f"{l:<40}"+"".join(f"{fn(src[n]):>17}" for n in ["DOWNSIDE","BASE","UPSIDE"]))
print("  [A] DISCIPLINED BOOTSTRAP (hires while EBITDA loss fundable)")
cr("    Yr5 revenue",lambda r:M(r[4]["revenue"]),R)
cr("    Max cumulative cash deficit",lambda r:M(min(x['cum_fcf'] for x in r)),R)
cr("    => MINIMUM CAPITAL NEEDED",lambda r:M(max(0,-min(x['cum_fcf'] for x in r))),R)
cr("    FCF-positive from year",lambda r:str(next((i+1 for i,x in enumerate(r) if x['fcf']>0),'never')),R)
print("  [B] STRICT $0 (ending cash never negative; no financing at all)")
cr("    Yr5 revenue",lambda r:M(r[4]["revenue"]),RC)
cr("    Yr5 EBITDA",lambda r:M(r[4]["ebitda"]),RC)
cr("    Yr5 FTE",lambda r:f"{r[4]['fte']:.1f}",RC)
cr("    5y cumulative MW",lambda r:f"{sum(x['mw_closed'] for x in r):,.0f}",RC)
cr("    Revenue lost vs [A]",lambda r:"",RC)
for n in ["DOWNSIDE","BASE","UPSIDE"]:
    print(f"      {n:<12} strict-$0 Yr5 {M(RC[n][4]['revenue']):>10} vs disciplined "
          f"{M(R[n][4]['revenue']):>10}  = "
          f"{(RC[n][4]['revenue']/R[n][4]['revenue']-1)*100:+.0f}%")
print("  [C] FUNDED ($3.0M at inception, full hiring plan from Yr1)")
cr("    Yr5 revenue",lambda r:M(r[4]["revenue"]),RF)
cr("    Yr5 EBITDA",lambda r:M(r[4]["ebitda"]),RF)
cr("    Max cumulative cash deficit",lambda r:M(min(x['cum_fcf'] for x in r)),RF)
cr("    Yr5 FTE",lambda r:f"{r[4]['fte']:.1f}",RF)

print(L("TABLE 5 — ONE-WAY SENSITIVITY ON YEAR-5 REVENUE & EBITDA (from BASE)"))
def flex_year5(**kw):
    s=replace(BASE,**kw); r=run(s,mode="ebitda"); return r[4]["revenue"], r[4]["ebitda"]
b5r,b5e=R["BASE"][4]["revenue"],R["BASE"][4]["ebitda"]
print(f"  BASE Yr5: revenue {M(b5r)}   EBITDA {M(b5e)}")
print(f"\n{'Variable':<38}{'Low':>22}{'High':>22}")
tests=[
 ("Brokerage rate (mils)",
  dict(brk_mils=0.00025), dict(brk_mils=0.00100), "0.25 mil","1.00 mil"),
 ("Flexibility $/MW-yr (Yr5)",
  dict(flex_mw_rev=[0,0,4000,4500,5000]), dict(flex_mw_rev=[0,0,14000,16000,18000]),
  "$5k","$18k"),
 ("MW per originator / yr",
  dict(mw_per_orig=[0,24,40,50,55]), dict(mw_per_orig=[0,72,120,150,165]), "-50%","+50%"),
 ("Success fee $/MW",
  dict(fee_mw=[1500,1500,1750,2000,2125]), dict(fee_mw=[4500,4500,5250,6000,6375]),
  "-50%","+50%"),
 ("Customer conversion rate",
  dict(conv=[.06,.08,.09,.10,.10]), dict(conv=[.18,.24,.27,.29,.30]), "-50%","+50%"),
 ("Logo churn",
  dict(churn=0.15), dict(churn=0.50), "15%","50%"),
 ("Residual attrition (brokerage)",
  dict(brk_attr=0.10), dict(brk_attr=0.40), "10%","40%"),
 ("Flexibility start year",
  dict(flex_start=2), dict(flex_start=5), "Yr2","Yr5"),
 ("Screen price",
  dict(price_screen=[6000,7000,7500,7750,8000]),
  dict(price_screen=[18000,21000,22500,23250,24000]), "-50%","+50%"),
 ("Delivery productivity",
  dict(screens_per_del_fte=9.0,retainers_per_del_fte=1.5),
  dict(screens_per_del_fte=18.0,retainers_per_del_fte=3.0), "-30%","+36%"),
]
impact=[]
for name,lo,hi,llab,hlab in tests:
    lr,le=flex_year5(**lo); hr,he=flex_year5(**hi)
    impact.append((name,lr,hr,le,he,abs(hr-lr)))
    print(f"{name:<38}{llab+': '+M(lr):>22}{hlab+': '+M(hr):>22}")
print(f"\n  Ranked by Yr5 revenue swing:")
for i,(n,lr,hr,le,he,sw) in enumerate(sorted(impact,key=lambda x:-x[5])[:5],1):
    print(f"   {i}. {n:<36} swing {M(sw):>10}  "
          f"({(lr/b5r-1)*100:+.0f}% to {(hr/b5r-1)*100:+.0f}%)   "
          f"EBITDA {M(le)} -> {M(he)}")

print(L("TABLE 6 — MONTE CARLO (20,000 draws; triangular on 9 drivers)"))
print("  NOTE: input ranges are the DOWNSIDE/BASE/UPSIDE bounds set above. These are")
print("  modelling assumptions, not empirical distributions. The output therefore")
print("  measures assumption sensitivity, NOT real-world probability. [ASSUMPTION]")
random.seed(42)
def tri(a,m,b): return random.triangular(a,b,m)
N=20000; revs=[];ebs=[];caps=[]
for _ in range(N):
    s=replace(BASE,
        brk_mils=tri(0.00020,0.00050,0.00100),
        flex_mw_rev=[0,0,round(tri(3000,8000,14000)),round(tri(3500,9000,16000)),
                     round(tri(4000,10000,18000))],
        mw_per_orig=[0]+[round(tri(.45,1.0,1.55)*v,1) for v in [48,80,100,110]],
        fee_mw=[round(tri(.55,1.0,1.5)*v) for v in [3000,3000,3500,4000,4250]],
        conv=[round(tri(.55,1.0,1.45)*v,4) for v in [.12,.16,.18,.19,.20]],
        churn=tri(0.18,0.30,0.48),
        brk_attr=tri(0.12,0.22,0.38),
        flex_start=round(tri(2,3,5)),
        screens_per_del_fte=tri(9,13,17))
    r=run(s,mode="ebitda")
    revs.append(r[4]["revenue"]); ebs.append(r[4]["ebitda"])
    caps.append(max(0,-min(x["cum_fcf"] for x in r)))
revs.sort(); ebs.sort(); caps.sort()
q=lambda a,p:a[int(p*(len(a)-1))]
print(f"\n  Year-5 REVENUE distribution")
for p in [.05,.10,.25,.50,.75,.90,.95]:
    print(f"    P{int(p*100):>2}  {M(q(revs,p)):>12}")
print(f"    mean {M(st_.mean(revs)):>12}")
print(f"\n  Year-5 EBITDA distribution")
for p in [.05,.25,.50,.75,.95]:
    print(f"    P{int(p*100):>2}  {M(q(ebs,p)):>12}")
print(f"\n  Peak capital requirement distribution")
for p in [.50,.75,.90,.95]:
    print(f"    P{int(p*100):>2}  {M(q(caps,p)):>12}")
pr=lambda c:sum(1 for v in revs if c(v))/N
print(f"\n  P(Yr5 revenue >= $1M)      {pr(lambda v:v>=1e6)*100:5.1f}%")
print(f"  P(Yr5 revenue >= $5M)      {pr(lambda v:v>=5e6)*100:5.1f}%")
print(f"  P(Yr5 revenue >= $10M)     {pr(lambda v:v>=1e7)*100:5.1f}%")
print(f"  P(Yr5 revenue >= $25M)     {pr(lambda v:v>=2.5e7)*100:5.1f}%")
print(f"  P(Yr5 revenue >= $100M)    {pr(lambda v:v>=1e8)*100:5.1f}%")
print(f"  P(Yr5 EBITDA > 0)          {sum(1 for v in ebs if v>0)/N*100:5.1f}%")
print(f"  P(peak capital < $100k)    {sum(1 for v in caps if v<1e5)/N*100:5.1f}%")
print(f"  P(peak capital > $500k)    {sum(1 for v in caps if v>5e5)/N*100:5.1f}%")

print(L("TABLE 7 — MARKET SHARE REQUIRED"))
SAM_REV_LO, SAM_REV_HI = 15e9, 60e9      # dossier SAM revenue pool, US  [INFERENCE]
SAM_MW = 100_000                          # US MW/yr origination flow     [INFERENCE]
US_RETAIL = 514.8e9                        # EIA 2024 US retail elec rev   [FACT][VERIFY]
for n in ["DOWNSIDE","BASE","UPSIDE"]:
    r5=R[n][4]
    print(f"\n  {n}: Yr5 revenue {M(r5['revenue'])}, MW closed {r5['mw_closed']:,.0f}/yr")
    print(f"    share of US origination revenue pool ($15-60B): "
          f"{r5['revenue']/SAM_REV_HI*100:.4f}% - {r5['revenue']/SAM_REV_LO*100:.4f}%")
    print(f"    share of US MW origination flow (100 GW/yr):    "
          f"{r5['mw_closed']/SAM_MW*100:.3f}%")
    print(f"    share of US retail electricity revenue:         "
          f"{r5['revenue']/US_RETAIL*100:.5f}%")

print(L("TABLE 8 — IMPLIED ENTERPRISE VALUE (Year 5)"))
print("  Multiples chosen from the LEAST flattering defensible comparable set:")
print("   - origination/advisory services: 1.0-2.0x revenue, 6-9x EBITDA")
print("   - mixed services + contracted residual book: 2.0-3.5x rev, 8-12x EBITDA")
print("   - LandGate (closest real comparable): $12.2M revenue after ~10 yrs [ESTIMATE]")
for n in ["DOWNSIDE","BASE","UPSIDE"]:
    r5=R[n][4]; rev,eb=r5["revenue"],r5["ebitda"]
    resid=(r5["rev_brk"]+r5["rev_flx"])/rev
    rl,rh=(1.0,2.0) if resid<0.25 else (2.0,3.5)
    el,eh=(6,9) if resid<0.25 else (8,12)
    print(f"\n  {n}: Yr5 rev {M(rev)}, EBITDA {M(eb)}, residual mix {resid*100:.0f}%")
    print(f"    Revenue multiple {rl}-{rh}x  -> EV {M(rev*rl)} - {M(rev*rh)}")
    if eb>0:
        print(f"    EBITDA multiple {el}-{eh}x -> EV {M(eb*el)} - {M(eb*eh)}")
    else:
        print(f"    EBITDA multiple: N/A (EBITDA negative) - no defensible earnings multiple")

print(L("TABLE 9 — $0 -> $1M PATH (BASE, disciplined bootstrap)"))
cum=0
for i,x in enumerate(R["BASE"]):
    cum+=x["revenue"]
    print(f"  Yr{i+1}: revenue {M(x['revenue']):>9}  cumulative {M(cum):>9}  "
          f"FTE {x['fte']:4.1f}  founder pay {M(x['founder_pay']):>8}  "
          f"cash {M(x['cash_end']):>9}")
print("\n  Milestones (base):")
cum=0; done=set()
for i,x in enumerate(R["BASE"]):
    cum+=x["revenue"]
    for t,lab in [(1,"first $1"),(1e4,"$10k cumulative"),(1e5,"$100k cumulative"),
                  (1e6,"$1M cumulative"),(5e6,"$5M cumulative")]:
        if cum>=t and lab not in done:
            done.add(lab); print(f"    {lab:<20} reached in Year {i+1}")
for i,x in enumerate(R["BASE"]):
    if x["revenue"]>=1e6: print(f"    {'$1M ANNUAL revenue':<20} reached in Year {i+1}"); break

json.dump({"disciplined":{n:[{k:v for k,v in x.items() if not isinstance(v,(dict,))}
    for x in R[n]] for n in R},"strict":{n:[{k:v for k,v in x.items()
    if not isinstance(v,(dict,))} for x in RC[n]] for n in RC},
    "mc":{"rev_p50":q(revs,.5),"rev_p90":q(revs,.9),"rev_p10":q(revs,.1)}},
    open("final.json","w"),indent=1)
print("\n[final.json written]")
