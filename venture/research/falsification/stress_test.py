"""Falsification stress test: does the leading candidate survive adverse
assumptions that a hostile reviewer would impose?

Scenarios (applied only to the leader, #1):
  S1 "SMB pricing": ARPA cut ~40% (buyers anchor to cheap AP-suite features)
  S2 "Bundling wins": P(competitive compression) raised to 0.55-0.8
  S3 "Paper compliance": rule satisfied by written policy -> penetration halved
  S4 "All of the above"
Also reports P(NPV_leader > NPV_runner_up) from independent draws.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "statistics"))
import ev_model as ev  # noqa: E402

cfg = json.loads((Path(ev.HERE) / "ev_params.json").read_text())
meta = cfg["_meta"]
lead = cfg["candidates"]["C001_payee_assurance"]
runner = cfg["candidates"]["C012_idr_automation"]


def scaled(spec, f):
    return [x * f for x in spec]


scenarios = {
    "S0 base": dict(lead),
    "S1 SMB pricing (ARPA x0.6)": {**lead, "arpa_usd": scaled(lead["arpa_usd"], 0.6)},
    "S2 bundling wins (P compression 0.55-0.8)": {**lead, "p_competitive_compression": [0.55, 0.68, 0.8]},
    "S3 paper compliance (penetration x0.5)": {**lead, "y5_penetration": scaled(lead["y5_penetration"], 0.5)},
    "S4 all adverse": {**lead, "arpa_usd": scaled(lead["arpa_usd"], 0.6),
                        "p_competitive_compression": [0.55, 0.68, 0.8],
                        "y5_penetration": scaled(lead["y5_penetration"], 0.5)},
}
rng = np.random.default_rng(7)
runner_res = ev.simulate(runner, meta, rng)
rows = []
for name, p in scenarios.items():
    r = ev.simulate(p, meta, rng)
    rows.append({
        "scenario": name,
        "npv_mean": float(r["npv"].mean()),
        "npv_p50": float(np.median(r["npv"])),
        "p_npv_positive": float((r["npv"] > 0).mean()),
        "arr5_p50": float(np.median(r["arr5"])),
        "p_beats_runner_up": float((r["npv"] > runner_res["npv"]).mean()),
    })
out = Path(__file__).parent
(out / "stress_results.json").write_text(json.dumps(rows, indent=2))
lines = ["# Stress test of leader (#1) vs runner-up (#12 IDR automation)", "",
         f"Runner-up mean NPV: ${runner_res['npv'].mean()/1e6:.1f}M", "",
         "| Scenario | Mean NPV | P50 NPV | P(NPV>0) | Y5 ARR P50 | P(beats runner-up draw) |", "|---|---|---|---|---|---|"]
for r in rows:
    lines.append(f"| {r['scenario']} | ${r['npv_mean']/1e6:.1f}M | ${r['npv_p50']/1e6:.1f}M | {r['p_npv_positive']:.0%} | "
                 f"${r['arr5_p50']/1e6:.1f}M | {r['p_beats_runner_up']:.0%} |")
(out / "stress_results.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
