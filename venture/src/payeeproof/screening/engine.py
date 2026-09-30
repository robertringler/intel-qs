"""Pure screening engine: no I/O. The service layer loads context and persists results."""

from __future__ import annotations

import re
import statistics
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from typing import Any

from .rules import RULES, SEVERITY_ORDER, max_severity

_SUFFIXES = {
    "LLC",
    "INC",
    "CORP",
    "CORPORATION",
    "CO",
    "COMPANY",
    "LTD",
    "LIMITED",
    "LP",
    "LLP",
    "PLLC",
    "PC",
    "THE",
    "INCORPORATED",
    "GROUP",
    "HOLDINGS",
    "USA",
    "US",
    "AND",
}
_NON_WORD = re.compile(r"[^A-Z0-9 ]")


@dataclass
class KnownAccount:
    bank_account_id: str
    vendor_id: str
    vendor_name: str
    vendor_legal_name: str | None
    status: str  # unverified | verified | retired | rejected
    verified_at: datetime | None


@dataclass
class EntryIn:
    index: int
    transaction_code: str
    is_credit: bool
    is_debit: bool
    is_prenote: bool
    sec_code: str
    routing: str
    routing_valid: bool
    account_fp: str
    network_fp: str | None
    amount_cents: int
    receiver_name: str


@dataclass
class ScreenInput:
    now: datetime
    entries: list[EntryIn]
    known: dict[str, list[KnownAccount]]  # account_fp -> registrations
    flagged: set[str]  # org-level flagged fps
    history: dict[str, list[int]]  # account_fp -> released amounts (cents)
    network: dict[str, tuple[int, int]]  # network_fp -> (verified_orgs, flagged_orgs)
    integrity_issues: list[str]
    settings: dict[str, Any]


@dataclass
class EntryResult:
    index: int
    vendor_id: str | None
    bank_account_id: str | None
    severity: str
    findings: list[dict[str, str]] = field(default_factory=list)


@dataclass
class ScreenResult:
    entries: list[EntryResult]
    file_findings: list[dict[str, str]]
    risk_level: str  # none|info|low|medium|high|critical
    status: str  # clear | needs_review | blocked
    rule_counts: dict[str, int]
    required_approvals: int


def _norm_name(s: str) -> list[str]:
    toks = _NON_WORD.sub(" ", s.upper()).split()
    return [t for t in toks if t not in _SUFFIXES]


def name_similarity(receiver: str, vendor: str) -> float:
    a, b = _norm_name(receiver), _norm_name(vendor)
    if not a or not b:
        return 0.0
    sa, sb = " ".join(a), " ".join(b)
    # NACHA truncates names to 22 characters: a prefix match is a full match.
    if sb.startswith(sa) or sa.startswith(sb):
        return 1.0
    jacc = len(set(a) & set(b)) / len(set(a) | set(b))
    ratio = SequenceMatcher(None, sa, sb).ratio()
    return max(jacc, ratio)


def robust_z(x: int, history: list[int]) -> float | None:
    if len(history) < 2:
        return None
    med = statistics.median(history)
    mad = statistics.median(abs(h - med) for h in history)
    if mad == 0:
        # Constant history: express deviation relative to the median instead.
        return None if med == 0 else (x - med) / (0.05 * med) * 0.6745
    return 0.6745 * (x - med) / mad


def _f(code: str, message: str) -> dict[str, str]:
    r = RULES[code]
    return {"code": code, "severity": r.severity, "title": r.title, "message": message}


def screen(inp: ScreenInput) -> ScreenResult:
    st = inp.settings
    recent = timedelta(days=int(st["recent_change_days"]))
    dual = int(st["dual_approval_threshold_cents"])
    round_min = int(st["large_round_amount_cents"])
    min_hist = int(st["anomaly_min_history"])
    zthr = float(st["anomaly_z"])
    name_thr = float(st["name_match_threshold"])

    dup_counter = Counter((e.account_fp, e.amount_cents) for e in inp.entries if e.is_credit and e.amount_cents > 0)
    results: list[EntryResult] = []
    counts: Counter[str] = Counter()

    for e in inp.entries:
        f: list[dict[str, str]] = []
        regs = [k for k in inp.known.get(e.account_fp, []) if k.status != "retired"]
        active = [k for k in regs if k.status in ("verified", "unverified")]
        chosen = next((k for k in active if k.status == "verified"), active[0] if active else None)

        if e.is_prenote:
            f.append(_f("R018", "Zero-dollar prenote entry."))
        if e.sec_code == "IAT":
            f.append(_f("R016", "International entry: only the foreign account field is screened."))
        if not e.routing_valid:
            f.append(_f("R008", f"Routing {e.routing} fails the ABA check digit."))
        if e.account_fp in inp.flagged or any(k.status == "rejected" for k in regs):
            f.append(_f("R011", "This account was previously rejected as suspected fraud."))
        if e.network_fp and e.network_fp in inp.network:
            v, fl = inp.network[e.network_fp]
            if fl > 0:
                f.append(_f("R014", f"Flagged as suspected fraud by {fl} other organisation(s)."))
            elif v > 0:
                f.append(_f("R015", f"Independently verified by {v} other organisation(s)."))
        if e.is_debit:
            f.append(_f("R012", "Debit entry in a payment file."))

        if not e.is_prenote and e.is_credit:
            if not active:
                if not any(x["code"] == "R011" for x in f):
                    f.append(_f("R001", "Account is not registered to any vendor."))
            else:
                if chosen and chosen.status != "verified":
                    f.append(_f("R002", f"Account registered to {chosen.vendor_name} but not verified."))
                if len({k.vendor_id for k in active}) > 1:
                    names = ", ".join(sorted({k.vendor_name for k in active}))
                    f.append(_f("R010", f"Account registered to multiple vendors: {names}."))
                if (
                    chosen
                    and chosen.status == "verified"
                    and chosen.verified_at
                    and inp.now - chosen.verified_at < recent
                ):
                    days = (inp.now - chosen.verified_at).days
                    f.append(_f("R003", f"Account verified {days} day(s) ago."))
                hist = inp.history.get(e.account_fp, [])
                if not hist:
                    f.append(_f("R004", "No previously released payment to this account."))
                elif len(hist) >= min_hist and e.amount_cents > 0:
                    z = robust_z(e.amount_cents, hist)
                    biggest = max(hist)
                    if (z is not None and z > zthr) or e.amount_cents > 3 * biggest:
                        med = statistics.median(hist)
                        f.append(
                            _f(
                                "R005",
                                f"Amount ${e.amount_cents / 100:,.2f} vs historical median "
                                f"${med / 100:,.2f} (max ${biggest / 100:,.2f}).",
                            )
                        )
                if chosen:
                    best = max(
                        name_similarity(e.receiver_name, chosen.vendor_name),
                        name_similarity(e.receiver_name, chosen.vendor_legal_name or ""),
                    )
                    if e.receiver_name and best < name_thr:
                        f.append(_f("R006", f"Receiver '{e.receiver_name}' vs vendor '{chosen.vendor_name}'."))
            if dup_counter[(e.account_fp, e.amount_cents)] > 1:
                f.append(_f("R007", "Same account and amount appear more than once in this file."))
            if e.amount_cents >= round_min and e.amount_cents % 100_000 == 0:
                f.append(_f("R009", f"Round amount ${e.amount_cents / 100:,.0f}."))
            if dual and e.amount_cents >= dual:
                f.append(_f("R013", f"Amount at/above dual-approval threshold ${dual / 100:,.0f}."))

        for x in f:
            counts[x["code"]] += 1
        sev = max_severity([x["severity"] for x in f])
        results.append(
            EntryResult(
                e.index, chosen.vendor_id if chosen else None, chosen.bank_account_id if chosen else None, sev, f
            )
        )

    block_integrity = bool(st.get("block_on_integrity_issues", True))
    file_findings = [
        {**_f("R017", issue), "severity": "high" if block_integrity else "medium"} for issue in inp.integrity_issues
    ]
    for x in file_findings:
        counts[x["code"]] += 1
    all_sev = [r.severity for r in results if r.severity != "none"] + [x["severity"] for x in file_findings]
    risk = max_severity(all_sev) if all_sev else "none"
    if risk in ("high", "critical"):
        status = "blocked"
    elif risk == "medium":
        status = "needs_review"
    else:
        status = "clear"
    total_credit = sum(e.amount_cents for e in inp.entries if e.is_credit)
    required = 2 if (SEVERITY_ORDER.get(risk, -1) >= SEVERITY_ORDER["high"] or (dual and total_credit >= dual)) else 1
    return ScreenResult(results, file_findings, risk, status, dict(counts), required)
