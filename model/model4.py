#!/usr/bin/env python3
"""
Five-year model v3: located-firm-capacity origination.
Adversarial build from the Strategic Research Dossier.

v3 corrections over v2 (all three were real errors that inflated results):
  1. COGS is now BUILT UP from delivery labour + direct third-party cost,
     not a % of revenue. v2 omitted 70% of analyst payroll from the P&L.
  2. DELIVERY CAPACITY CONSTRAINT added. Screens and retainers are limited
     by delivery FTE-hours, not by demand. This is the governing constraint
     of any services business and v2 had none -> revenue/FTE hit $2.6M.
  3. Founder cash salary is ENDOGENOUS in bootstrap mode. In the downside
     the founder cannot pay themselves; the model now shows that.
"""
import json, math
from dataclasses import dataclass, replace
from typing import List, Dict

HOURS, LF = 8760, 0.85
KWH_MW_YR = HOURS * LF * 1000                 # 7,446,000 kWh per MW-yr
YEARS = 5; IDX = range(YEARS)
def bpm(mils): return KWH_MW_YR * mils        # $/MW-yr of brokerage residual

@dataclass
class S:
    name: str
    inbound: List[int]              # inbound leads from free published artifacts
    conv_per_seller: int            # qualified conversations / selling FTE / yr
    qual: float; conv: List[float]  # conv ramps as track record builds
    churn: float
    # delivery capacity
    screens_per_del_fte: float      # screens one delivery FTE can produce/yr
    retainers_per_del_fte: float    # concurrent retainer clients / delivery FTE
    founder_delivery_fte: List[float]
    # pricing
    price_screen: List[int]; ret_attach: List[float]; ret_annual: List[int]
    # origination
    mw_per_orig: List[float]; fee_mw: List[int]
    # residual streams
    brk_attach: float; brk_mils: float; brk_attr: float
    flex_attach: float; flex_mw_rev: List[int]; flex_start: int; flex_attr: float
    # cost build-up
    subcontract_rate: float         # % of screen+retainer rev paid to subs/engineers
    brk_cost_per_mw: int            # $/MW-yr carrying cost on brokered MW
    flex_cost_per_mw: int           # $/MW-yr ops cost on flexibility MW (telemetry,
                                    # 24/7 dispatch, ISO settlement, M&V)
    mw_per_am_fte: int              # MW under management served per account-mgmt FTE
    orig_ramp: float                # first-year productivity of a new originator
    # headcount plan
    hc_orig: List[float]; hc_anl: List[float]; hc_ops: List[float]
    hc_eng: List[float]; hc_cmp: List[float]
    sal: Dict[str,int]; burden: float; founder_target: List[int]
    travel: List[int]; data_sw: List[int]; legal: List[int]; ins: List[int]
    admin: List[int]; mktg: List[int]; cloud: List[int]
    comm_rate: float; dso: int; collateral: List[int]; capex: List[int]
    tax: float; seed_cash: int = 15000

BASE = S("BASE",
    inbound=[35,95,180,270,340], conv_per_seller=85,
    qual=0.32, conv=[0.12,0.16,0.18,0.19,0.20], churn=0.30,
    screens_per_del_fte=13.0, retainers_per_del_fte=2.2,
    founder_delivery_fte=[0.55,0.40,0.25,0.15,0.10],
    price_screen=[12000,14000,15000,15500,16000],
    ret_attach=[0.0,0.16,0.22,0.24,0.25],
    ret_annual=[0,132000,144000,150000,156000],
    mw_per_orig=[0,48,80,100,110], fee_mw=[3000,3000,3500,4000,4250],
    brk_attach=0.35, brk_mils=0.0005, brk_attr=0.22,
    flex_attach=0.20, flex_mw_rev=[0,0,8000,9000,10000], flex_start=3, flex_attr=0.16,
    subcontract_rate=0.14, brk_cost_per_mw=450, flex_cost_per_mw=3600,
    mw_per_am_fte=260, orig_ramp=0.40,
    hc_orig=[0,0.5,2,4,6], hc_anl=[0,1,2.5,4,6], hc_ops=[0,0,0.5,1,2],
    hc_eng=[0,0,0,1,1], hc_cmp=[0,0,0.5,1,1],
    sal={"orig":120000,"anl":95000,"ops":85000,"eng":160000,"cmp":130000},
    burden=0.24, founder_target=[0,120000,160000,185000,200000],
    travel=[14000,38000,95000,160000,210000], data_sw=[6000,26000,85000,150000,205000],
    legal=[4000,16000,65000,120000,155000], ins=[3500,9000,28000,52000,70000],
    admin=[3000,14000,42000,75000,100000], mktg=[1500,9000,30000,55000,75000],
    cloud=[1200,7000,26000,55000,80000],
    comm_rate=0.10, dso=48, collateral=[0,0,150000,300000,450000],
    capex=[2000,9000,30000,55000,70000], tax=0.25)

DOWN = replace(BASE, name="DOWNSIDE",
    inbound=[18,45,80,115,140], conv_per_seller=68,
    qual=0.24, conv=[0.07,0.10,0.11,0.12,0.12], churn=0.45,
    screens_per_del_fte=10.0, retainers_per_del_fte=1.7,
    founder_delivery_fte=[0.55,0.45,0.35,0.25,0.20],
    price_screen=[9000,10000,10500,11000,11000],
    ret_attach=[0.0,0.08,0.12,0.13,0.14], ret_annual=[0,96000,105000,108000,114000],
    mw_per_orig=[0,22,38,48,55], fee_mw=[1800,1800,2000,2200,2400],
    brk_attach=0.18, brk_mils=0.00025, brk_attr=0.32,
    flex_attach=0.08, flex_mw_rev=[0,0,0,4000,4500], flex_start=4, flex_attr=0.26,
    subcontract_rate=0.19, brk_cost_per_mw=700, flex_cost_per_mw=5200,
    mw_per_am_fte=180, orig_ramp=0.25,
    hc_orig=[0,0.25,1,2,3], hc_anl=[0,0.5,1.5,2.5,3], hc_ops=[0,0,0,0.5,1],
    hc_eng=[0,0,0,0,1], hc_cmp=[0,0,0.25,0.5,1],
    burden=0.26, founder_target=[0,80000,130000,150000,165000],
    travel=[16000,34000,72000,110000,140000], data_sw=[7000,28000,72000,115000,150000],
    legal=[5000,20000,62000,105000,135000], ins=[4000,10000,25000,42000,58000],
    admin=[3500,15000,38000,62000,82000], mktg=[2000,8000,22000,38000,50000],
    cloud=[1500,7000,20000,40000,58000],
    comm_rate=0.12, dso=68, collateral=[0,0,0,250000,400000],
    capex=[2500,9000,24000,42000,55000])

UP = replace(BASE, name="UPSIDE",
    inbound=[55,150,280,410,530], conv_per_seller=100,
    qual=0.38, conv=[0.17,0.21,0.24,0.25,0.26], churn=0.22,
    screens_per_del_fte=16.0, retainers_per_del_fte=2.8,
    founder_delivery_fte=[0.55,0.35,0.20,0.10,0.05],
    price_screen=[15000,17000,18500,20000,21000],
    ret_attach=[0.0,0.22,0.28,0.30,0.32],
    ret_annual=[0,156000,174000,186000,198000],
    mw_per_orig=[6,75,120,150,170], fee_mw=[4000,4250,5000,5500,6000],
    brk_attach=0.50, brk_mils=0.00085, brk_attr=0.15,
    flex_attach=0.32, flex_mw_rev=[0,9000,12000,14000,16000], flex_start=2, flex_attr=0.11,
    subcontract_rate=0.11, brk_cost_per_mw=320, flex_cost_per_mw=2600,
    mw_per_am_fte=360, orig_ramp=0.55,
    hc_orig=[0,1,3,6,9], hc_anl=[0,1.5,4,7,10], hc_ops=[0,0.5,1,2,3],
    hc_eng=[0,0,1,2,3], hc_cmp=[0,0,1,1,2],
    burden=0.23, founder_target=[0,140000,185000,215000,240000],
    travel=[14000,48000,125000,225000,310000], data_sw=[6000,30000,105000,195000,280000],
    legal=[4000,18000,75000,145000,200000], ins=[3500,11000,34000,65000,92000],
    admin=[3000,16000,52000,95000,135000], mktg=[1500,14000,45000,85000,120000],
    cloud=[1200,9000,38000,80000,120000],
    comm_rate=0.09, dso=40, collateral=[0,100000,250000,450000,650000],
    capex=[2000,12000,42000,80000,110000])


def year_pl(s, y, f, fsal, st):
    """f scales variable headcount & selling capacity. fsal scales founder pay."""
    o = {}
    hc = {"orig":s.hc_orig[y]*f, "anl":s.hc_anl[y]*f, "ops":s.hc_ops[y]*f,
          "eng":s.hc_eng[y]*f, "cmp":s.hc_cmp[y]*f}
    # founder splits time: delivery + selling
    prev_orig = st.get("orig_fte", 0.0)
    new_orig = max(0.0, hc["orig"] - prev_orig)
    eff_orig = min(hc["orig"], prev_orig) + new_orig*s.orig_ramp
    sellers = (1.0 - s.founder_delivery_fte[y]) + eff_orig
    delivery_fte = s.founder_delivery_fte[y] + hc["anl"]*0.70
    o["hc"], o["sellers"], o["delivery_fte"] = hc, sellers, delivery_fte
    o["eff_orig"] = eff_orig
    o["fte_core"] = 1.0 + sum(hc.values())

    # ---------- FUNNEL (demand) ----------
    leads = s.inbound[y]*(f**0.5) + sellers*s.conv_per_seller
    qualified = leads*s.qual
    new = qualified*s.conv[y]
    begin = st["cust"]; churn = begin*s.churn; end = begin+new-churn
    assert abs((begin+new-churn)-end) < 1e-9, "customer rollforward"
    avg = (begin+end)/2
    o.update(leads=leads, qualified=qualified, cust_begin=begin, cust_new=new,
             cust_churn=churn, cust_end=end, cust_avg=avg)

    # ---------- DELIVERY CAPACITY ALLOCATION ----------
    # Retainers are served first (contractual), screens take residual capacity.
    ret_demand = avg*s.ret_attach[y]
    ret_c = min(ret_demand, delivery_fte*s.retainers_per_del_fte)
    fte_used_ret = (ret_c/s.retainers_per_del_fte) if s.retainers_per_del_fte else 0
    fte_left = max(0.0, delivery_fte - fte_used_ret)
    scr_demand = max(avg, new*0.8)*1.25
    screens = min(scr_demand, fte_left*s.screens_per_del_fte)
    o.update(ret_demand=ret_demand, scr_demand=scr_demand,
             cap_util=(fte_used_ret + (screens/s.screens_per_del_fte))/delivery_fte
                       if delivery_fte > 0 else 0.0)

    # ---------- REVENUE ----------
    rev_scr = screens*s.price_screen[y]
    rev_ret = ret_c*s.ret_annual[y]
    mw_closed = sellers*s.mw_per_orig[y]
    rev_suc = mw_closed*s.fee_mw[y]
    cb_ = st["brk_mw"]*(1-s.brk_attr); nb = mw_closed*s.brk_attach
    brk_mw = cb_+nb; rev_brk = (cb_+nb*0.5)*bpm(s.brk_mils)
    nf = mw_closed*s.flex_attach if (y+1) >= s.flex_start else 0.0
    cf_ = st["flex_mw"]*(1-s.flex_attr)
    flex_mw = cf_+nf; rev_flx = (cf_+nf*0.5)*s.flex_mw_rev[y]
    rev = rev_scr+rev_ret+rev_suc+rev_brk+rev_flx
    o.update(screens=screens, rev_scr=rev_scr, ret_c=ret_c, rev_ret=rev_ret,
             mw_closed=mw_closed, rev_suc=rev_suc, brk_mw=brk_mw, rev_brk=rev_brk,
             flex_mw=flex_mw, rev_flx=rev_flx, revenue=rev)

    B = 1+s.burden
    pers = {k: hc[k]*s.sal[k]*B for k in hc}
    founder_pay = s.founder_target[y]*fsal
    founder_pers = founder_pay*B

    # ---------- COGS (built up from resources, not % of revenue) ----------
    cogs_labour = pers["anl"]*0.70 + founder_pers*s.founder_delivery_fte[y]
    cogs_sub = (rev_scr+rev_ret)*s.subcontract_rate
    cogs_settle = brk_mw*s.brk_cost_per_mw + flex_mw*s.flex_cost_per_mw
    am_fte = (brk_mw+flex_mw)/s.mw_per_am_fte
    cogs_am = am_fte*s.sal["ops"]*B
    cogs = cogs_labour+cogs_sub+cogs_settle+cogs_am
    gp = rev-cogs
    o.update(cogs=cogs, cogs_labour=cogs_labour, cogs_sub=cogs_sub,
             cogs_settle=cogs_settle, cogs_am=cogs_am, am_fte=am_fte,
             gross_profit=gp)

    # ---------- OPEX ----------
    nps = 0.15+0.85*f
    comm = (rev_suc+rev_brk)*s.comm_rate
    sm   = pers["orig"]+comm+(s.travel[y]+s.mktg[y])*nps
    rnd  = pers["eng"]+s.cloud[y]*nps
    opsx = pers["ops"]+pers["anl"]*0.30+s.data_sw[y]*nps
    gna  = (founder_pers*(1-s.founder_delivery_fte[y])+pers["cmp"]
            +(s.legal[y]+s.ins[y]+s.admin[y])*nps)
    opex = sm+rnd+opsx+gna
    o["fte"] = o["fte_core"] + am_fte
    o.update(sm=sm, rnd=rnd, opsx=opsx, gna=gna, opex=opex,
             ebitda=gp-opex, commission=comm, founder_pay=founder_pay,
             personnel=founder_pers+sum(pers.values()))
    return o


def solve_year(s, y, st, cash, bootstrap, tol):
    if not bootstrap:
        return year_pl(s, y, 1.0, 1.0, st)
    budget = cash + tol
    # 1) try full plan with full founder pay
    o = year_pl(s, y, 1.0, 1.0, st)
    if o["ebitda"] >= -budget: return o
    # 2) cut founder pay first (founder absorbs the shortfall)
    lo, hi = 0.0, 1.0
    for _ in range(50):
        mid = (lo+hi)/2
        if year_pl(s, y, 1.0, mid, st)["ebitda"] >= -budget: lo = mid
        else: hi = mid
    if lo > 0.0 or year_pl(s, y, 1.0, 0.0, st)["ebitda"] >= -budget:
        o = year_pl(s, y, 1.0, lo, st)
        if o["ebitda"] >= -budget: return o
    # 3) founder pay at zero AND scale back hiring
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo+hi)/2
        if year_pl(s, y, mid, 0.0, st)["ebitda"] >= -budget: lo = mid
        else: hi = mid
    return year_pl(s, y, lo, 0.0, st)


def run(s, bootstrap=True, funding=0.0, tol=0.0):
    st = {"cust":0.0,"brk_mw":0.0,"flex_mw":0.0,"ar":0.0,"orig_fte":0.0}
    cash = s.seed_cash+funding; rows=[]; cum=0.0
    for y in IDX:
        o = solve_year(s, y, st, cash, bootstrap, tol)
        f = 1.0 if not bootstrap else (o["hc"]["orig"]/s.hc_orig[y] if s.hc_orig[y] else 1.0)
        o["f"] = f
        da = s.capex[y]*f*0.45
        ebit = o["ebitda"]-da; tax = max(0.0,ebit)*s.tax; ni = ebit-tax
        ar = o["revenue"]*s.dso/365; wc = ar-st["ar"]
        coll = (s.collateral[y]-(s.collateral[y-1] if y>0 else 0))*f
        cx = s.capex[y]*f
        fcf = o["revenue"]-(o["cogs"]+o["opex"]+tax)-wc-cx-coll
        cb = cash; cash = cb+fcf; cum += fcf
        assert abs((cb+fcf)-cash) < 1e-6, "cash rollforward"
        o.update(da=da, ebit=ebit, tax=tax, net_income=ni, ar=ar, wc=wc,
                 coll=coll, capex=cx, fcf=fcf, cash_begin=cb, cash_end=cash,
                 cum_fcf=cum)
        rows.append(o)
        st.update(cust=o["cust_end"], brk_mw=o["brk_mw"], flex_mw=o["flex_mw"],
                  ar=ar, orig_fte=o["hc"]["orig"])
    return rows

def M(x):
    n=x<0; v=abs(x)
    t=f"${v/1e6:,.2f}M" if v>=1e6 else (f"${v/1e3:,.0f}k" if v>=1000 else f"${v:,.0f}")
    return f"({t})" if n else t

def show(t, rows, keys):
    if t: print(f"\n{'-'*90}\n{t}\n{'-'*90}")
    print(f"{'':<38}{'Yr1':>10}{'Yr2':>10}{'Yr3':>10}{'Yr4':>10}{'Yr5':>10}")
    for lbl,k,fmt in keys:
        cs="".join(f"{M(r[k]):>10}" if fmt=="m" else
                   f"{r[k]:>10.1f}" if fmt=="n1" else
                   f"{r[k]:>10.0f}" if fmt=="n0" else
                   f"{r[k]*100:>9.1f}%" for r in rows)
        print(f"{lbl:<38}{cs}")

SC={"DOWNSIDE":DOWN,"BASE":BASE,"UPSIDE":UP}
RES={k:run(v) for k,v in SC.items()}

print("#"*90)
print("# LOCATED FIRM CAPACITY ORIGINATION — 5-YEAR MODEL v4 (BOOTSTRAP)")
print(f"# 1.00 mil brokerage = {M(bpm(0.001))}/MW-yr  (8,760h x 0.85 x 1,000 kWh)")
print("#"*90)

for n in ["DOWNSIDE","BASE","UPSIDE"]:
    rows=RES[n]; s=SC[n]
    print(f"\n\n{'#'*90}\n# {n}   brokerage {s.brk_mils*1000:.2f} mils = "
          f"{M(bpm(s.brk_mils))}/MW-yr   flex from Yr{s.flex_start}\n{'#'*90}")
    print(f"{'Hiring factor f (1.0 = full plan)':<38}"+"".join(f"{r['f']:>10.2f}" for r in rows))
    print(f"{'Founder cash pay':<38}"+"".join(f"{M(r['founder_pay']):>10}" for r in rows))
    show(f"{n}: FUNNEL & CAPACITY", rows, [
        ("Leads","leads","n0"),("Qualified","qualified","n0"),
        ("Customers begin","cust_begin","n1"),("  + New","cust_new","n1"),
        ("  - Churn","cust_churn","n1"),("Customers end","cust_end","n1"),
        ("Delivery FTE","delivery_fte","n1"),
        ("Effective originator FTE","eff_orig","n1"),
        ("Account-mgmt FTE (MW-driven)","am_fte","n1"),
        ("Screen demand (units)","scr_demand","n1"),
        ("Screens DELIVERED","screens","n1"),
        ("Retainer demand","ret_demand","n1"),
        ("Retainers SERVED","ret_c","n1"),
        ("Delivery utilisation","cap_util","pct")])
    show(f"{n}: REVENUE BY STREAM", rows, [
        ("1 Screens","rev_scr","m"),("2 Retainers","rev_ret","m"),
        ("MW closed (annual)","mw_closed","n0"),("3 Success fees","rev_suc","m"),
        ("MW brokered (cum)","brk_mw","n0"),("4 Brokerage residual","rev_brk","m"),
        ("MW flexibility (cum)","flex_mw","n0"),("5 Flexibility","rev_flx","m"),
        ("TOTAL REVENUE","revenue","m")])
    print(f"{'YoY growth':<38}"+f"{'n/a':>10}"+
          "".join(f"{(rows[i]['revenue']/rows[i-1]['revenue']-1)*100:>9.0f}%" for i in range(1,YEARS)))
    show(f"{n}: P&L", rows, [
        ("Revenue","revenue","m"),
        ("  COGS: delivery labour","cogs_labour","m"),
        ("  COGS: subcontract","cogs_sub","m"),
        ("  COGS: residual carrying","cogs_settle","m"),
        ("  COGS: account mgmt","cogs_am","m"),
        ("COGS total","cogs","m"),("Gross profit","gross_profit","m"),
        ("Sales & marketing","sm","m"),("R&D","rnd","m"),
        ("Operations","opsx","m"),("G&A","gna","m"),("Total OpEx","opex","m"),
        ("EBITDA","ebitda","m"),("D&A","da","m"),("EBIT","ebit","m"),
        ("Taxes","tax","m"),("Net income","net_income","m")])
    print(f"{'Gross margin':<38}"+"".join(f"{r['gross_profit']/r['revenue']*100:>9.1f}%" for r in rows))
    print(f"{'EBITDA margin':<38}"+"".join(f"{r['ebitda']/r['revenue']*100:>9.1f}%" for r in rows))
    print(f"{'Headcount FTE':<38}"+"".join(f"{r['fte']:>10.1f}" for r in rows))
    print(f"{'Revenue per FTE':<38}"+"".join(f"{M(r['revenue']/r['fte']):>10}" for r in rows))
    show(f"{n}: CASH FLOW", rows, [
        ("Beginning cash","cash_begin","m"),("Revenue (cash basis)","revenue","m"),
        ("COGS","cogs","m"),("OpEx","opex","m"),("Taxes","tax","m"),
        ("Working capital (AR)","wc","m"),("ISO collateral","coll","m"),
        ("CapEx","capex","m"),("FREE CASH FLOW","fcf","m"),
        ("Ending cash","cash_end","m"),("Cumulative FCF","cum_fcf","m")])
    mn=min(r["cum_fcf"] for r in rows)
    be=next((i+1 for i,r in enumerate(rows) if r["ebitda"]>0),None)
    bf=next((i+1 for i,r in enumerate(rows) if r["fcf"]>0),None)
    r5=rows[4]
    print(f"\n  Max cumulative cash deficit : {M(mn)}")
    print(f"  EBITDA-positive from year   : {be or 'never in 5y'}")
    print(f"  FCF-positive from year      : {bf or 'never in 5y'}")
    print(f"  Yr5 mix  scr {r5['rev_scr']/r5['revenue']*100:4.0f}% | ret {r5['rev_ret']/r5['revenue']*100:4.0f}%"
          f" | suc {r5['rev_suc']/r5['revenue']*100:4.0f}% | brk {r5['rev_brk']/r5['revenue']*100:4.0f}%"
          f" | flx {r5['rev_flx']/r5['revenue']*100:4.0f}%")
    print(f"  5y cumulative MW originated : {sum(r['mw_closed'] for r in rows):,.0f} MW")

print("\n\n"+"#"*90); print("# SCENARIO SUMMARY (bootstrap, no external capital)"); print("#"*90)
print(f"{'Metric':<34}{'Downside':>18}{'Base':>18}{'Upside':>18}")
def sr(l,fn): print(f"{l:<34}"+"".join(f"{fn(RES[n]):>18}" for n in ["DOWNSIDE","BASE","UPSIDE"]))
sr("Yr1 revenue", lambda r:M(r[0]["revenue"]))
sr("Yr2 revenue", lambda r:M(r[1]["revenue"]))
sr("Yr3 revenue", lambda r:M(r[2]["revenue"]))
sr("Yr4 revenue", lambda r:M(r[3]["revenue"]))
sr("Yr5 revenue", lambda r:M(r[4]["revenue"]))
sr("Yr5 gross profit", lambda r:M(r[4]["gross_profit"]))
sr("Yr5 EBITDA", lambda r:M(r[4]["ebitda"]))
sr("Yr5 EBITDA margin", lambda r:f"{r[4]['ebitda']/r[4]['revenue']*100:.1f}%")
sr("Yr5 gross margin", lambda r:f"{r[4]['gross_profit']/r[4]['revenue']*100:.1f}%")
sr("Yr5 customers", lambda r:f"{r[4]['cust_end']:.0f}")
sr("Yr5 FTE", lambda r:f"{r[4]['fte']:.1f}")
sr("Yr5 revenue/FTE", lambda r:M(r[4]["revenue"]/r[4]["fte"]))
sr("Yr5 MW closed", lambda r:f"{r[4]['mw_closed']:,.0f}")
sr("5y cumulative MW", lambda r:f"{sum(x['mw_closed'] for x in r):,.0f}")
sr("Max cash deficit", lambda r:M(min(x["cum_fcf"] for x in r)))
sr("5y cumulative FCF", lambda r:M(r[4]["cum_fcf"]))
sr("Founder paid by Yr5?", lambda r:"yes" if r[4]["founder_pay"]>0 else "NO")

json.dump({n:[{k:v for k,v in r.items() if not isinstance(v,dict)} for r in RES[n]] for n in RES},
          open("results4.json","w"), indent=1)
print("\n[results4.json written]")
