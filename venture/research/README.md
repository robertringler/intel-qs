# Research repository

Institutional-style research behind the selection of **PayeeProof**. Evidence discipline:

| Tag | Meaning |
|---|---|
| [F] | Direct fact from a cited source |
| [D] | Dataset-derived (arithmetic on cited data) |
| [E] | Evidence-backed estimate |
| [M] | Model assumption |
| [I] | Inference |
| [S] | Speculation |

- `sources.csv` is the source registry (93 entries): URL, dates, claim, reliability, primary or secondary, bias, access method.
- **Access limitation (important).** This work ran in a sandbox whose egress policy blocked direct fetches of
  census.gov, sba.gov, nacha.org, advocacy.sba.gov and most bank sites. Evidence was gathered through a web-search
  service that returns summaries of the cited pages. Every source is marked `web search summary` in the
  registry. Figures should be re-verified against the primary documents before external use.
- No customer interviews were conducted, and none are claimed. Customer evidence comes from surveys (AFP, Greenhouse)
  and published bank and insurer guidance. The 90-day validation plan is in `customers/icp-and-jtbd.md`.

| Folder | Contents |
|---|---|
| market/ | Bottom-up sizing for the selected opportunity |
| competitors/ | Landscape, competitor table, "why not solved" |
| customers/ | ICP, jobs-to-be-done, validation plan |
| pricing/ | Competitor pricing evidence, value-based WTP |
| economics/ | Leakage analysis across finalists |
| trends/ | Structural vs cyclical trends |
| regulation/ | Nacha rules, insurance conditions, privacy/security duties |
| technology/ | NACHA format, validation methods, provider landscape |
| datasets/ | 100-candidate universe (py/csv/json) + elimination report |
| statistics/ | Monte Carlo EV model, parameters, results, Bayesian prevalence |
| falsification/ | Attacks on the thesis, stress test |
