"""Performance: screen a 10,000-entry NACHA file (requirement: < 2 s server time)."""

import time

import pytest

from helpers import nacha_file
from payeeproof.models import Organization
from payeeproof.nacha import parse_nacha
from payeeproof.services import screening


@pytest.mark.perf
def test_parse_10k_entries_fast():
    entries = [("011000015", f"{100000 + i}", 1000 + i, f"VENDOR {i}") for i in range(10_000)]
    data = nacha_file(entries)
    t = time.perf_counter()
    f = parse_nacha(data)
    dt = time.perf_counter() - t
    assert len(f.entries) == 10_000 and not f.integrity_issues
    assert dt < 1.0, dt


@pytest.mark.perf
def test_screen_10k_entries_under_2s(svc):
    org = svc.db.get(Organization, svc.org_id)
    org.plan, org.subscription_status = "growth", "active"
    svc.db.flush()
    entries = [("011000015", f"{100000 + i}", 1000 + i, f"VENDOR {i}") for i in range(10_000)]
    data = nacha_file(entries)
    t = time.perf_counter()
    run = screening.screen_file(svc.db, svc.ctx("clerk"), "big.ach", data, "web")
    svc.db.flush()
    dt = time.perf_counter() - t
    print(f"screened 10,000 entries in {dt:.2f}s")
    assert run.entry_count == 10_000
    assert dt < 2.0, dt
