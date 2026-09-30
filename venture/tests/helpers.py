"""Shared builders for tests."""

from datetime import date, datetime

from payeeproof.nacha import NachaFileBuilder


def nacha_file(entries, created=datetime(2026, 9, 30, 9, 0)):
    """entries: list of (routing, account, amount_cents, name[, code])."""
    b = NachaFileBuilder("021000021", "1234567890", "JPMORGAN CHASE", "ACME CORP", "021000021", created=created)
    i = b.add_batch("ACME CORP", "1234567890", "CCD", "VENDORPAY", date(2026, 10, 1))
    for e in entries:
        routing, account, amount, name = e[:4]
        code = e[4] if len(e) > 4 else "22"
        b.add_entry(i, code, routing, account, amount, name)
    return b.build().encode()
