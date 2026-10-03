#!/usr/bin/env python3
"""
WATTFLOCK five-year model. Curtailment-risk quantification -> certification
-> parametric risk transfer for flexible large loads.

Built to test, not to flatter. Key structural question the model answers:
the ASSESSMENT market is one-time-per-site and therefore small; only the
PREMIUM market recurs and scales with MW. Does the business clear $5M?

Throughput note that distinguishes this from an origination business:
one analyst delivers ~16-24 assessments/yr at 50-300 MW each, i.e. ~2,500-
4,000 MW of MW-touched per analyst-year, versus ~110 MW per originator-year
for brokered site transactions. ~25x more MW per FTE, on a 3-6 week cycle
instead of 12-18 months.
"""
from dataclasses import dataclass, replace, field
from typing import List, Dict

YEARS = 5; IDX = range(YEARS)

@dataclass
class S:
    name: str
    # ---- demand side ----
    us_flex_gw_signed: List[float]     # GW/yr of flexible large-load agreements signed nationally
    avg_site_mw: float                 # MW per site (assessment unit)
    cra_share: List[float]             # share of those sites WATTFLOCK assesses
    # ---- delivery capacity ----
    cra_per_analyst: float             # assessments per analyst-FTE-yr
    founder_delivery: List[float]      # founder FTE available for delivery
    # ---- pricing ----
    cra_price: List[int]
    sub_price: List[int]
    sub_count: List[int]               # index/certification subscribers
    study_count: List[int]             # utility / regulatory tariff-design studies
    study_price: List[int]
    # ---- risk transfer ----
    cover_start: int                   # first year cover is placed
    cover_conv: float                  # share of assessed sites that buy cover
    cover_attr: float                  # annual attrition of the covered book
    mga_cost_rate: float               # underwriting, actuarial, claims, policy
                                       # admin, reinsurance broking, as % of commission
    premium_per_mw: List[int]          # $/MW-yr of premium placed
    mga_commission: float              # WATTFLOCK share of premium
    profit_comm_start: int
    profit_comm: List[int]             # $ of profit commission (contingent)
    # ---- costs ----
    hc_analyst: List[float]; hc_uw: List[float]; hc_eng: List[float]; hc_bd: List[float]
    sal: Dict[str,int]; burden: float; founder_pay: List[int]
    data_tools: List[int]; licensing: List[int]; eo_insurance: List[int]
    legal: List[int]; travel: List[int]; admin: List[int]
    cra_direct_rate: float             # subcontract/direct cost as % of CRA revenue
    dso: int; tax: float; seed: int = 1000

BASE = S("BASE",
  us_flex_gw_signed=[8,12,16,20,24], avg_site_mw=150,
  cra_share=[0.055,0.105,0.17,0.24,0.28],
  cra_per_analyst=18, founder_delivery=[0.55,0.40,0.25,0.15,0.10],
  cra_price=[32000,38000,42000,45000,48000],
  sub_price=[0,28000,34000,38000,40000], sub_count=[0,7,18,32,46],
  study_count=[1,2,3,4,5], study_price=[45000,50000,60000,70000,75000],
  cover_start=3, cover_conv=0.30, cover_attr=0.15, mga_cost_rate=0.62,
  premium_per_mw=[0,0,5000,5500,6000], mga_commission=0.15,
  profit_comm_start=5, profit_comm=[0,0,0,0,350000],
  hc_analyst=[0,1,2.5,4,6], hc_uw=[0,0,0.5,1,1.5],
  hc_eng=[0,0,0.5,1,1.5], hc_bd=[0,0,0.5,1,2],
  sal={"analyst":105000,"uw":165000,"eng":155000,"bd":130000},
  burden=0.24, founder_pay=[0,110000,150000,180000,200000],
  data_tools=[2000,18000,55000,95000,130000],
  licensing=[0,3000,22000,38000,48000],
  eo_insurance=[2500,12000,45000,80000,110000],
  legal=[3000,22000,70000,110000,140000],
  travel=[9000,30000,70000,115000,150000],
  admin=[2500,14000,40000,70000,95000],
  cra_direct_rate=0.10, dso=52, tax=0.25)

DOWN = replace(BASE, name="DOWNSIDE",
  us_flex_gw_signed=[4,6,8,10,12], cra_share=[0.03,0.055,0.08,0.11,0.13],
  cra_per_analyst=13, cra_price=[22000,26000,28000,30000,30000],
  sub_price=[0,18000,22000,24000,25000], sub_count=[0,3,7,12,16],
  study_count=[0,1,1,2,2], study_price=[35000,38000,42000,48000,50000],
  cover_start=5, cover_conv=0.08, cover_attr=0.28, mga_cost_rate=0.78,
  premium_per_mw=[0,0,0,0,3500], profit_comm_start=9, profit_comm=[0,0,0,0,0],
  hc_analyst=[0,0.5,1,2,2.5], hc_uw=[0,0,0,0.25,0.5],
  hc_eng=[0,0,0,0.5,0.5], hc_bd=[0,0,0.25,0.5,1],
  founder_pay=[0,70000,110000,130000,145000],
  cra_direct_rate=0.16, dso=72,
  data_tools=[2500,20000,48000,78000,100000],
  licensing=[0,4000,18000,30000,38000],
  eo_insurance=[3000,14000,40000,65000,85000],
  legal=[3500,26000,62000,95000,120000])

UP = replace(BASE, name="UPSIDE",
  us_flex_gw_signed=[12,20,28,36,44], cra_share=[0.085,0.15,0.24,0.32,0.38],
  cra_per_analyst=24, cra_price=[42000,50000,56000,62000,68000],
  sub_price=[0,38000,46000,52000,58000], sub_count=[0,12,32,58,84],
  study_count=[2,4,6,8,10], study_price=[55000,65000,78000,90000,100000],
  cover_start=2, cover_conv=0.42, cover_attr=0.10, mga_cost_rate=0.52,
  premium_per_mw=[0,6000,6500,7000,7500], mga_commission=0.175,
  profit_comm_start=4, profit_comm=[0,0,0,600000,2200000],
  hc_analyst=[0,2,4.5,8,12], hc_uw=[0,0.5,1.5,2.5,4],
  hc_eng=[0,0.5,1,2,3], hc_bd=[0,0.5,1.5,3,5],
  founder_pay=[0,140000,185000,220000,250000],
  cra_direct_rate=0.08, dso=42,
  data_tools=[2000,24000,75000,140000,200000],
  licensing=[0,6000,30000,52000,70000],
  eo_insurance=[2500,16000,60000,115000,165000],
  legal=[3000,28000,95000,160000,215000],
  travel=[9000,42000,100000,175000,240000])

def run(s, bootstrap=True):
    cash=float(s.seed); rows=[]; cum=0.0; prev_ar=0.0; carry_cov=0.0
    for y in IDX:
        def build(f, fs):
            o={}
            hc={"analyst":s.hc_analyst[y]*f,"uw":s.hc_uw[y]*f,
                "eng":s.hc_eng[y]*f,"bd":s.hc_bd[y]*f}
            o["hc"]=hc; o["fte"]=1.0+sum(hc.values())
            # ---- CRA: demand vs delivery capacity ----
            sites_national = s.us_flex_gw_signed[y]*1000/s.avg_site_mw
            cra_demand = sites_national*s.cra_share[y]*(0.30+0.70*f)
            delivery = s.founder_delivery[y]+hc["analyst"]
            cra_capacity = delivery*s.cra_per_analyst
            cra = min(cra_demand, cra_capacity)
            o.update(sites_national=sites_national, cra_demand=cra_demand,
                     cra_capacity=cra_capacity, cra=cra,
                     cap_bound="capacity" if cra_capacity<cra_demand else "demand",
                     mw_assessed=cra*s.avg_site_mw)
            rev_cra = cra*s.cra_price[y]
            # ---- subscriptions & studies ----
            subs = s.sub_count[y]*(0.30+0.70*f)
            rev_sub = subs*s.sub_price[y]
            studies = s.study_count[y]*(0.30+0.70*f)
            rev_study = studies*s.study_price[y]
            # ---- risk transfer ----
            if (y+1)>=s.cover_start:
                new_cov = cra*s.cover_conv*s.avg_site_mw
                cmw = carry_cov*(1-s.cover_attr) + new_cov
                billable = carry_cov*(1-s.cover_attr) + new_cov*0.5
            else:
                new_cov = cmw = billable = 0.0
            premium = billable*s.premium_per_mw[y]
            rev_comm = premium*s.mga_commission
            rev_pc = s.profit_comm[y]*f if (y+1)>=s.profit_comm_start else 0.0
            rev = rev_cra+rev_sub+rev_study+rev_comm+rev_pc
            o.update(subs=subs, rev_cra=rev_cra, rev_sub=rev_sub, studies=studies,
                     rev_study=rev_study, cover_mw=cmw, new_cov=new_cov, premium=premium,
                     rev_comm=rev_comm, rev_pc=rev_pc, revenue=rev)
            # ---- COGS: delivery labour + direct ----
            B=1+s.burden
            pers={k:hc[k]*s.sal[k]*B for k in hc}
            fpay=s.founder_pay[y]*fs; fpers=fpay*B
            cogs = (pers["analyst"]*0.75 + fpers*s.founder_delivery[y]
                    + rev_cra*s.cra_direct_rate + rev_study*0.12
                    + rev_comm*s.mga_cost_rate)
            o.update(cogs=cogs, gross_profit=rev-cogs, founder_pay=fpay)
            nps=0.15+0.85*f
            o["sm"]=pers["bd"]+(s.travel[y])*nps
            o["rnd"]=pers["eng"]+(s.data_tools[y])*nps
            o["opsx"]=pers["uw"]+pers["analyst"]*0.25+(s.licensing[y])*nps
            o["gna"]=(fpers*(1-s.founder_delivery[y])
                      +(s.eo_insurance[y]+s.legal[y]+s.admin[y])*nps)
            o["opex"]=o["sm"]+o["rnd"]+o["opsx"]+o["gna"]
            o["ebitda"]=o["gross_profit"]-o["opex"]
            return o
        if bootstrap:
            o=build(1.0,1.0)
            if o["ebitda"] < -cash:
                lo,hi=0.0,1.0
                for _ in range(45):
                    m=(lo+hi)/2
                    if build(1.0,m)["ebitda"]>=-cash: lo=m
                    else: hi=m
                o=build(1.0,lo)
                if o["ebitda"] < -cash:
                    lo,hi=0.0,1.0
                    for _ in range(50):
                        m=(lo+hi)/2
                        if build(m,0.0)["ebitda"]>=-cash: lo=m
                        else: hi=m
                    o=build(lo,0.0)
        else:
            o=build(1.0,1.0)
        tax=max(0.0,o["ebitda"])*s.tax
        ar=o["revenue"]*s.dso/365; wc=ar-prev_ar
        fcf=o["revenue"]-o["cogs"]-o["opex"]-tax-wc
        cb=cash; cash=cb+fcf; cum+=fcf
        assert abs((cb+fcf)-cash)<1e-6, "cash rollforward"
        o.update(tax=tax, net=o["ebitda"]-tax, ar=ar, wc=wc, fcf=fcf,
                 cash_begin=cb, cash_end=cash, cum_fcf=cum)
        rows.append(o); prev_ar=ar; carry_cov=o["cover_mw"]
    return rows

def M(x):
    n=x<0; v=abs(x)
    t=f"${v/1e6:,.2f}M" if v>=1e6 else (f"${v/1e3:,.0f}k" if v>=1000 else f"${v:,.0f}")
    return f"({t})" if n else t

R={s.name:run(s) for s in [DOWN,BASE,UP]}

print("#"*92)
print("# WATTFLOCK — FIVE-YEAR MODEL (bootstrap, $1,000 seed)")
print("#"*92)

for n in ["DOWNSIDE","BASE","UPSIDE"]:
    rows=R[n]; s={"DOWNSIDE":DOWN,"BASE":BASE,"UPSIDE":UP}[n]
    print(f"\n{'='*92}\n{n}   (cover from Yr{s.cover_start}, MGA commission {s.mga_commission:.1%})\n{'='*92}")
    print(f"{'':<34}{'Yr1':>11}{'Yr2':>11}{'Yr3':>11}{'Yr4':>11}{'Yr5':>11}")
    def row(lbl,k,f="m"):
        print(f"{lbl:<34}"+"".join(
            f"{M(x[k]):>11}" if f=="m" else f"{x[k]:>11.1f}" if f=="n1"
            else f"{x[k]:>11,.0f}" if f=="n0" else f"{x[k]:>11}" for x in rows))
    row("US flexible sites signed/yr","sites_national","n0")
    row("  CRA demand (engagements)","cra_demand","n1")
    row("  CRA delivery capacity","cra_capacity","n1")
    row("  CRAs DELIVERED","cra","n1")
    row("  binding constraint","cap_bound","s")
    row("MW assessed in year","mw_assessed","n0")
    row("  new MW covered in year","new_cov","n0")
    row("MW under cover (cum)","cover_mw","n0")
    row("Premium placed","premium","m")
    print("-"*92)
    row("1 Assessments (CRA)","rev_cra")
    row("2 Index subscriptions","rev_sub")
    row("3 Utility/reg studies","rev_study")
    row("4 Cover commission","rev_comm")
    row("5 Profit commission","rev_pc")
    row("TOTAL REVENUE","revenue")
    row("COGS (incl. MGA operating cost)","cogs"); row("Gross profit","gross_profit")
    row("S&M","sm"); row("R&D","rnd"); row("Operations","opsx"); row("G&A","gna")
    row("Total OpEx","opex"); row("EBITDA","ebitda")
    row("Taxes","tax"); row("Net income","net")
    print(f"{'Gross margin':<34}"+"".join(f"{x['gross_profit']/max(1.0,x['revenue'])*100:>10.1f}%" for x in rows))
    print(f"{'EBITDA margin':<34}"+"".join(f"{x['ebitda']/max(1.0,x['revenue'])*100:>10.1f}%" for x in rows))
    row("FTE","fte","n1")
    print(f"{'Revenue / FTE':<34}"+"".join(f"{M(x['revenue']/max(0.01,x['fte'])):>11}" for x in rows))
    row("Founder cash pay","founder_pay")
    row("Free cash flow","fcf"); row("Cumulative FCF","cum_fcf")
    mn=min(x["cum_fcf"] for x in rows)
    be=next((i+1 for i,x in enumerate(rows) if x["ebitda"]>0),None)
    r5=rows[4]
    print(f"\n  Max cumulative cash deficit : {M(mn)}  -> capital needed {M(max(0,-mn))}")
    print(f"  EBITDA-positive from year   : {be or 'never in 5y'}")
    print(f"  Yr5 revenue mix: CRA {r5['rev_cra']/max(1.0,r5['revenue'])*100:.0f}% | "
          f"subs {r5['rev_sub']/max(1.0,r5['revenue'])*100:.0f}% | studies {r5['rev_study']/max(1.0,r5['revenue'])*100:.0f}% | "
          f"commission {r5['rev_comm']/max(1.0,r5['revenue'])*100:.0f}% | profit comm {r5['rev_pc']/max(1.0,r5['revenue'])*100:.0f}%")
    print(f"  Yr5 recurring share (subs+comm+pc) : "
          f"{(r5['rev_sub']+r5['rev_comm']+r5['rev_pc'])/max(1.0,r5['revenue'])*100:.0f}%")
    print(f"  5y MW assessed (cumulative) : {sum(x['mw_assessed'] for x in rows):,.0f} MW")
    print(f"  Yr5 MW assessed per analyst-FTE : "
          f"{r5['mw_assessed']/max(0.01,(s.founder_delivery[4]+r5['hc']['analyst'])):,.0f} MW")

# ---------------------------------------------------------------- market ceiling
print(f"\n{'='*92}\nMARKET CEILING TEST — is the assessment market big enough on its own?\n{'='*92}")
for gw in [10,20,40]:
    sites=gw*1000/150
    for price in [35000,50000]:
        print(f"  {gw} GW/yr flexible load signed = {sites:,.0f} sites/yr "
              f"x {M(price)} = {M(sites*price)}/yr TOTAL assessment market")
print("\n  => The one-time assessment market is single-digit millions even at")
print("     national scale and 100% share. ASSESSMENT ALONE CANNOT BE THE BUSINESS.")
print("     Only premium (recurring, scales with MW) and the index subscription")
print("     reach meaningful size. This is the model's central structural finding.\n")
for cum_gw, pen, ppm in [(40,0.10,5000),(60,0.15,6000),(80,0.25,7000)]:
    ins=cum_gw*1000*pen
    prem=ins*ppm
    print(f"  {cum_gw} GW cumulative flexible x {pen:.0%} insured = {ins:,.0f} MW "
          f"x {M(ppm)}/MW = {M(prem)} premium -> MGA @15% = {M(prem*0.15)}")

print(f"\n{'='*92}\nSUMMARY\n{'='*92}")
print(f"{'Metric':<34}{'Downside':>18}{'Base':>18}{'Upside':>18}")
def sr(l,fn): print(f"{l:<34}"+"".join(f"{fn(R[n]):>18}" for n in ["DOWNSIDE","BASE","UPSIDE"]))
for i,lbl in enumerate(["Yr1","Yr2","Yr3","Yr4","Yr5"]):
    sr(f"{lbl} revenue", lambda r,i=i: M(r[i]["revenue"]))
sr("Yr5 gross profit", lambda r:M(r[4]["gross_profit"]))
sr("Yr5 EBITDA", lambda r:M(r[4]["ebitda"]))
sr("Yr5 EBITDA margin", lambda r:f"{r[4]['ebitda']/max(1.0,r[4]['revenue'])*100:.1f}%")
sr("Yr5 FTE", lambda r:f"{r[4]['fte']:.1f}")
sr("Yr5 revenue/FTE", lambda r:M(r[4]["revenue"]/max(0.01,r[4]["fte"])))
sr("Yr5 recurring share", lambda r:f"{(r[4]['rev_sub']+r[4]['rev_comm']+r[4]['rev_pc'])/max(1.0,r[4]['revenue'])*100:.0f}%")
sr("Yr5 MW under cover", lambda r:f"{r[4]['cover_mw']:,.0f}")
sr("Capital required", lambda r:M(max(0,-min(x['cum_fcf'] for x in r))))
sr("5y cumulative FCF", lambda r:M(r[4]["cum_fcf"]))
sr("Founder paid by Yr5?", lambda r:"yes" if r[4]["founder_pay"]>0 else "NO")
# valuation
print(f"\n{'Yr5 implied EV':<34}", end="")
for n in ["DOWNSIDE","BASE","UPSIDE"]:
    r5=R[n][4]; rec=(r5['rev_sub']+r5['rev_comm']+r5['rev_pc'])/max(1.0,r5['revenue'])
    lo,hi=(1.5,3.0) if rec<0.4 else (3.0,5.5)
    print(f"{M(r5['revenue']*lo)+'-'+M(r5['revenue']*hi):>18}", end="")
print("\n  (1.5-3.0x revenue when recurring <40%; 3.0-5.5x when recurring >=40%,")
print("   the MGA/specialty-distribution range. Lower of revenue and EBITDA methods.)")

# ------------------------------------------------- one-way sensitivity
print(f"\n{'='*92}\nSENSITIVITY ON YEAR-5 REVENUE (from BASE)\n{'='*92}")
b5=R["BASE"][4]["revenue"]; b5e=R["BASE"][4]["ebitda"]
print(f"  BASE Yr5 revenue {M(b5)}  EBITDA {M(b5e)}\n")
tests=[
 ("WATTFLOCK share of US flexible sites",
  dict(cra_share=[0.028,0.053,0.085,0.12,0.14]), dict(cra_share=[0.083,0.158,0.255,0.36,0.42]), "half","1.5x"),
 ("US flexible GW signed/yr",
  dict(us_flex_gw_signed=[4,6,8,10,12]), dict(us_flex_gw_signed=[12,18,24,30,36]), "half","1.5x"),
 ("Cover conversion (assessed -> insured)",
  dict(cover_conv=0.12), dict(cover_conv=0.45), "12%","45%"),
 ("Premium per MW-yr",
  dict(premium_per_mw=[0,0,2500,2750,3000]), dict(premium_per_mw=[0,0,8000,9000,10000]), "half","1.7x"),
 ("Assessment price",
  dict(cra_price=[16000,19000,21000,22500,24000]), dict(cra_price=[48000,57000,63000,67500,72000]), "half","1.5x"),
 ("Cover start year",
  dict(cover_start=2), dict(cover_start=5), "Yr2","Yr5"),
 ("Covered-book attrition",
  dict(cover_attr=0.08), dict(cover_attr=0.30), "8%","30%"),
 ("Index subscribers",
  dict(sub_count=[0,3,9,16,23]), dict(sub_count=[0,11,27,48,69]), "half","1.5x"),
 ("MGA operating cost rate",
  dict(mga_cost_rate=0.45), dict(mga_cost_rate=0.80), "45%","80%"),
]
imp=[]
for n_,lo,hi,ll,hl in tests:
    rl=run(replace(BASE,**lo))[4]; rh=run(replace(BASE,**hi))[4]
    imp.append((n_,rl["revenue"],rh["revenue"],rl["ebitda"],rh["ebitda"],abs(rh["revenue"]-rl["revenue"])))
    print(f"  {n_:<40}{ll+': '+M(rl['revenue']):>20}{hl+': '+M(rh['revenue']):>20}")
print(f"\n  Ranked by Yr5 revenue swing:")
for i,(n_,rl,rh,el,eh,sw) in enumerate(sorted(imp,key=lambda x:-x[5])[:5],1):
    print(f"   {i}. {n_:<40} swing {M(sw):>9}  EBITDA {M(el)} -> {M(eh)}")
