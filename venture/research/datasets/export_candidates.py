"""Export the candidate universe to CSV/JSON and write the elimination report."""
import csv
import json
from collections import Counter
from pathlib import Path

from candidates import CANDIDATES, FIELDS

HERE = Path(__file__).parent
GATES = {
    "G1": "No measurable economic loss with a traceable source or clear mechanism",
    "G2": "No identifiable buyer with budget authority / recurring trigger",
    "G3": "Target segment already dominated by well-funded incumbents",
    "G4": "Infeasible for a seed-stage team (licensing, data access, procurement cycle)",
    "G5": "Timing window closed or deferred beyond 2027",
    "G6": "Fails AI-commoditization or platform-dependency test",
}
rows = []
for cnd in CANDIDATES:
    r = {}
    for f in FIELDS:
        v = cnd[f]
        if v == "" and f not in ("failed_gate",):
            v = f"not assessed (eliminated at {cnd['failed_gate']})" if cnd["failed_gate"] else "n/a"
        r[f] = v
    rows.append(r)
with open(HERE / "candidates.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=FIELDS)
    w.writeheader()
    w.writerows(rows)
(HERE / "candidates.json").write_text(json.dumps(rows, indent=1))

cnt = Counter(c["failed_gate"] or "SURVIVED" for c in CANDIDATES)
lines = ["# Candidate elimination report", "",
         "100 candidates were screened through six sequential gates (first failure eliminates).",
         "Candidates eliminated at a gate carry abbreviated fields; survivors are fully specified.",
         "Machine-readable data: `candidates.csv`, `candidates.json`; definitions in `candidates.py`.", "",
         "| Gate | Definition | Eliminated |", "|---|---|---|"]
for g, d in GATES.items():
    lines.append(f"| {g} | {d} | {cnt.get(g, 0)} |")
lines += [f"| - | Survived to quantitative model | {cnt['SURVIVED']} |", "",
          "## Survivors (sent to Monte Carlo EV model)", ""]
for c in CANDIDATES:
    if not c["failed_gate"]:
        lines.append(f"- **#{c['id']} {c['name']}** — {c['gate_reason']}")
lines += ["", "Two eliminated candidates (#25 IEEPA refunds, #34 CPG deductions) were also modelled as controls, "
          "to test whether gate elimination hid a higher-EV option. Both scored below every survivor "
          "(see `../statistics/ev_results.md`).", "", "## Eliminated candidates", "",
          "| # | Candidate | Sector | Gate | Reason |", "|---|---|---|---|---|"]
for c in CANDIDATES:
    if c["failed_gate"]:
        lines.append(f"| {c['id']} | {c['name']} | {c['sector']} | {c['failed_gate']} | {c['gate_reason']} |")
(HERE / "elimination.md").write_text("\n".join(lines) + "\n")
print(cnt)
