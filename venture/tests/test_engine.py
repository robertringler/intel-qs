"""Screening engine rules (pure function)."""

from datetime import UTC, datetime, timedelta

from hypothesis import given, settings
from hypothesis import strategies as st

from payeeproof.screening.engine import EntryIn, KnownAccount, ScreenInput, name_similarity, robust_z, screen
from payeeproof.screening.rules import RULES, SEVERITY_ORDER
from payeeproof.services.settings_defaults import DEFAULTS

NOW = datetime(2026, 9, 30, tzinfo=UTC)


def entry(i=0, fp="A", amount=100_00, code="22", name="GLOBEX LLC", routing_valid=True, nfp=None, sec="CCD"):
    credit = code in ("22", "32", "23")
    return EntryIn(
        index=i,
        transaction_code=code,
        is_credit=credit,
        is_debit=not credit,
        is_prenote=code in ("23", "28"),
        sec_code=sec,
        routing="011000015",
        routing_valid=routing_valid,
        account_fp=fp,
        network_fp=nfp,
        amount_cents=amount,
        receiver_name=name,
    )


def known(fp="A", status="verified", verified_days_ago=200, vendor="v1", name="Globex LLC"):
    return {fp: [KnownAccount("ba1", vendor, name, None, status, NOW - timedelta(days=verified_days_ago))]}


def run(entries, known_map=None, history=None, flagged=None, network=None, integrity=None, **st_over):
    st = {**DEFAULTS, **st_over}
    return screen(
        ScreenInput(NOW, entries, known_map or {}, flagged or set(), history or {}, network or {}, integrity or [], st)
    )


def codes(res, i=0):
    return {f["code"] for f in res.entries[i].findings}


def test_clear_when_verified_with_history():
    res = run([entry()], known(), history={"A": [100_00] * 6})
    assert codes(res) == set()
    assert res.status == "clear" and res.required_approvals == 1


def test_unknown_account_blocks():
    res = run([entry()])
    assert "R001" in codes(res) and res.status == "blocked" and res.required_approvals == 2


def test_unverified_account():
    res = run([entry()], known(status="unverified"), history={"A": [100_00] * 6})
    assert "R002" in codes(res) and res.status == "blocked"


def test_recent_change_and_first_payment():
    res = run([entry()], known(verified_days_ago=2))
    assert {"R003", "R004"} <= codes(res)
    assert res.status == "needs_review"


def test_amount_anomaly():
    hist = [1000_00, 1050_00, 980_00, 1010_00, 995_00, 1020_00]
    assert "R005" in codes(run([entry(amount=9000_00)], known(), history={"A": hist}))
    assert "R005" not in codes(run([entry(amount=1030_00)], known(), history={"A": hist}))


def test_anomaly_needs_min_history():
    assert "R005" not in codes(run([entry(amount=9_000_00)], known(), history={"A": [100_00] * 3}))


def test_name_mismatch():
    res = run([entry(name="TOTALLY DIFFERENT")], known(), history={"A": [100_00] * 6})
    assert "R006" in codes(res)
    assert name_similarity("GLOBEX", "Globex LLC") == 1.0
    assert name_similarity("GLOBEX INTERNATIONAL SU", "Globex International Supply Co") == 1.0


def test_duplicates_round_and_threshold():
    res = run([entry(0, amount=6_000_000), entry(1, amount=6_000_000)], known(), history={"A": [6_000_000] * 6})
    assert {"R007", "R009", "R013"} <= codes(res, 0)
    assert res.required_approvals == 2


def test_invalid_routing_and_flagged():
    res = run([entry(routing_valid=False)], known(), history={"A": [100_00] * 6}, flagged={"A"})
    assert {"R008", "R011"} <= codes(res)
    assert res.risk_level == "critical"


def test_shared_account():
    k = {
        "A": [
            KnownAccount("b1", "v1", "Globex", None, "verified", NOW - timedelta(days=100)),
            KnownAccount("b2", "v2", "Initech", None, "verified", NOW - timedelta(days=100)),
        ]
    }
    assert "R010" in codes(run([entry()], k, history={"A": [100_00] * 6}))


def test_retired_account_is_unknown():
    assert "R001" in codes(run([entry()], known(status="retired")))


def test_network_signals():
    assert "R014" in codes(run([entry(nfp="N")], known(), history={"A": [1] * 6}, network={"N": (3, 1)}))
    assert "R015" in codes(run([entry(nfp="N")], known(), history={"A": [100_00] * 6}, network={"N": (3, 0)}))


def test_debit_prenote_iat():
    assert "R012" in codes(run([entry(code="27")]))
    res = run([entry(code="23", amount=0)])
    assert "R018" in codes(res) and "R001" not in codes(res)
    assert "R016" in codes(run([entry(sec="IAT")], known(), history={"A": [100_00] * 6}))


def test_integrity_blocks():
    res = run([entry()], known(), history={"A": [100_00] * 6}, integrity=["totals mismatch"])
    assert res.status == "blocked" and "R017" in res.rule_counts
    res2 = run([entry()], known(), history={"A": [100_00] * 6}, integrity=["x"], block_on_integrity_issues=False)
    assert res2.status == "needs_review"


def test_robust_z():
    assert robust_z(100, [100]) is None
    assert robust_z(200, [100, 100, 100]) > 3.5
    assert abs(robust_z(100, [90, 100, 110])) < 0.01


def test_rule_catalogue_consistent():
    for code, r in RULES.items():
        assert r.code == code and r.severity in SEVERITY_ORDER


@settings(max_examples=200, deadline=None)
@given(
    amounts=st.lists(st.integers(1, 10_000_000), min_size=1, max_size=20),
    statuses=st.lists(st.sampled_from(["verified", "unverified", "retired", None]), min_size=1, max_size=20),
)
def test_property_status_reflects_worst_finding(amounts, statuses):
    ents, km = [], {}
    for i, amt in enumerate(amounts):
        fp = f"fp{i}"
        stt = statuses[i % len(statuses)]
        if stt:
            km[fp] = [KnownAccount(f"b{i}", f"v{i}", "Globex", None, stt, NOW - timedelta(days=100))]
        ents.append(entry(i, fp=fp, amount=amt))
    res = run(ents, km)
    worst = max((SEVERITY_ORDER[f["severity"]] for e in res.entries for f in e.findings), default=-1)
    if worst >= SEVERITY_ORDER["high"]:
        assert res.status == "blocked" and res.required_approvals == 2
    elif worst == SEVERITY_ORDER["medium"]:
        assert res.status == "needs_review"
    else:
        assert res.status == "clear"
    # any credit to a non-verified or unknown account must never be 'clear'
    if any(not km.get(f"fp{i}") or km[f"fp{i}"][0].status != "verified" for i in range(len(ents))):
        assert res.status == "blocked"
