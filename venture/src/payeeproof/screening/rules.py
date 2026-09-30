"""Screening rule catalogue. Codes are stable identifiers used in evidence exports."""

from __future__ import annotations

from dataclasses import dataclass

SEVERITY_ORDER = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


@dataclass(frozen=True)
class Rule:
    code: str
    severity: str
    title: str
    rationale: str


RULES: dict[str, Rule] = {
    r.code: r
    for r in [
        Rule(
            "R001",
            "high",
            "Unknown account",
            "The receiving account is not in the vendor master. Payments to unregistered accounts are the core "
            "signature of vendor-impersonation fraud.",
        ),
        Rule(
            "R002",
            "high",
            "Unverified account",
            "The account is registered but has not passed out-of-band verification and independent approval.",
        ),
        Rule(
            "R003",
            "medium",
            "Recently changed account",
            "The account was verified within the recent-change window; fraudsters strike the first payment "
            "run after a successful change.",
        ),
        Rule("R004", "medium", "First payment to account", "No previously released payment has gone to this account."),
        Rule(
            "R005",
            "medium",
            "Amount anomaly",
            "Amount is far above this payee's history (robust z-score on median/MAD).",
        ),
        Rule(
            "R006",
            "low",
            "Receiver name mismatch",
            "The receiver name in the file does not resemble the vendor name registered for the account.",
        ),
        Rule(
            "R007",
            "medium",
            "Duplicate payment in file",
            "The same account and amount appear more than once in this file.",
        ),
        Rule("R008", "high", "Invalid routing number", "The receiving routing number fails the ABA check-digit test."),
        Rule("R009", "low", "Large round amount", "A large, round-dollar amount (common in fabricated invoices)."),
        Rule(
            "R010", "high", "Account shared across vendors", "The same account is registered to more than one vendor."
        ),
        Rule(
            "R011",
            "critical",
            "Previously flagged account",
            "This account was previously rejected as suspected fraud in your organisation.",
        ),
        Rule("R012", "info", "Debit entry in payment file", "Debit entries are unusual in vendor payment files."),
        Rule(
            "R013",
            "info",
            "At or above dual-approval threshold",
            "The entry amount meets the organisation's dual-approval threshold.",
        ),
        Rule(
            "R014",
            "critical",
            "Account flagged by the PayeeProof network",
            "Another participating organisation rejected this account as suspected fraud.",
        ),
        Rule(
            "R015",
            "info",
            "Account verified elsewhere in the network",
            "Other participating organisations have independently verified this account.",
        ),
        Rule(
            "R016",
            "medium",
            "International (IAT) entry",
            "IAT entries are parsed but payee verification is limited to the foreign account field.",
        ),
        Rule(
            "R017",
            "high",
            "File integrity: control totals mismatch",
            "Batch/file control totals do not match the entries - the file may have been altered after it "
            "was generated.",
        ),
        Rule("R018", "info", "Prenote entry", "Zero-dollar prenote entry."),
    ]
}


def max_severity(severities: list[str]) -> str:
    if not severities:
        return "none"
    return max(severities, key=lambda s: SEVERITY_ORDER[s])
