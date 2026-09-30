"""NACHA parsing/writing: unit, property-based and fuzz tests."""

import contextlib
from datetime import date, datetime

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from payeeproof.nacha import NachaFileBuilder, NachaParseError, is_valid_routing, parse_nacha, routing_check_digit

VALID_ROUTINGS = ["021000021", "011000015", "026009593", "121000358", "071000013", "091000019"]


def test_known_routings_valid():
    for r in VALID_ROUTINGS:
        assert is_valid_routing(r), r


@pytest.mark.parametrize("bad", ["021000022", "12345678", "0210000210", "abcdefghi", "000000000", ""])
def test_invalid_routings(bad):
    assert not is_valid_routing(bad)


def _builder():
    return NachaFileBuilder(
        "021000021", "1234567890", "JPMORGAN CHASE", "ACME CORP", "021000021", created=datetime(2026, 9, 30, 10, 15)
    )


def test_roundtrip_simple():
    b = _builder()
    i = b.add_batch("ACME CORP", "1234567890", "CCD", "VENDORPAY", date(2026, 10, 1))
    b.add_entry(i, "22", "011000015", "123456789", 150000, "GLOBEX LLC", "INV1001")
    b.add_entry(i, "27", "026009593", "5555", 250, "REFUND")
    f = parse_nacha(b.build())
    assert f.integrity_issues == []
    assert [e.amount_cents for e in f.entries] == [150000, 250]
    assert f.total_credit_cents == 150000 and f.total_debit_cents == 250
    e = f.entries[0]
    assert (e.rdfi_routing, e.account, e.receiver_name, e.individual_id) == (
        "011000015",
        "123456789",
        "GLOBEX LLC",
        "INV1001",
    )
    assert e.is_credit and not f.entries[1].is_credit
    assert f.batches[0].service_class == "200"


def test_blocking_factor_padding():
    text = _builder().build()
    lines = text.strip("\n").split("\n")
    assert len(lines) % 10 == 0
    assert all(len(ln) == 94 for ln in lines)


def test_crlf_and_single_blob_formats():
    b = _builder()
    i = b.add_batch("ACME", "1", "PPD", "PAYROLL", date(2026, 10, 1))
    b.add_entry(i, "22", "011000015", "42", 100, "A")
    text = b.build()
    assert parse_nacha(text.replace("\n", "\r\n")).entries[0].account == "42"
    blob = text.replace("\n", "")
    assert parse_nacha(blob).entries[0].amount_cents == 100


def test_tampered_amount_detected():
    b = _builder()
    i = b.add_batch("ACME", "1", "CCD", "VENDORPAY", date(2026, 10, 1))
    b.add_entry(i, "22", "011000015", "123456789", 150000, "GLOBEX")
    text = b.build().replace("0000150000", "0000950000", 1)
    issues = parse_nacha(text).integrity_issues
    assert any("total credit" in x for x in issues)


def test_tampered_routing_detected_by_entry_hash():
    b = _builder()
    i = b.add_batch("ACME", "1", "CCD", "VENDORPAY", date(2026, 10, 1))
    b.add_entry(i, "22", "011000015", "123456789", 1000, "GLOBEX")
    text = b.build()
    tampered = text.replace("6220110000151", "6220260095931", 1)
    issues = parse_nacha(tampered).integrity_issues
    assert any("entry hash" in x for x in issues)


def test_missing_file_control_reported():
    b = _builder()
    i = b.add_batch("ACME", "1", "CCD", "X", date(2026, 10, 1))
    b.add_entry(i, "22", "011000015", "1", 1, "A")
    lines = [ln for ln in b.build().splitlines() if not ln.startswith("9")]
    f = parse_nacha("\n".join(lines))
    assert any("missing" in x for x in f.integrity_issues)


@pytest.mark.parametrize(
    "text,msg",
    [
        ("", "empty"),
        ("5" + " " * 93, "file header"),
        ("1" + " " * 93, "094"),
    ],
)
def test_structural_errors(text, msg):
    with pytest.raises(NachaParseError, match=msg):
        parse_nacha(text)


def test_non_ascii_rejected():
    with pytest.raises(NachaParseError, match="ASCII"):
        parse_nacha("1é".encode())


def test_entry_outside_batch_rejected():
    hdr = _builder().build().splitlines()[0]
    with pytest.raises(NachaParseError, match="outside a batch"):
        parse_nacha(hdr + "\n6" + "2" * 93)


def test_prenote_codes():
    b = _builder()
    i = b.add_batch("ACME", "1", "CCD", "PRENOTE", date(2026, 10, 1))
    b.add_entry(i, "23", "011000015", "99887766", 0, "VENDOR")
    e = parse_nacha(b.build()).entries[0]
    assert e.is_prenote and e.is_credit and e.amount_cents == 0


def test_writer_validation():
    b = _builder()
    with pytest.raises(ValueError):
        b.add_batch("ACME", "1", "XXX", "D", date(2026, 1, 1))
    i = b.add_batch("ACME", "1", "CCD", "D", date(2026, 1, 1))
    with pytest.raises(ValueError):
        b.add_entry(i, "99", "011000015", "1", 1, "A")
    with pytest.raises(ValueError):
        b.add_entry(i, "22", "011000015", "bad acct!", 1, "A")
    with pytest.raises(ValueError):
        b.add_entry(i, "22", "011000015", "1", -1, "A")
    with pytest.raises(ValueError):
        NachaFileBuilder("123456789", "1", "X", "Y", "021000021")


def test_check_digit_function():
    assert routing_check_digit("02100002") == 1
    with pytest.raises(ValueError):
        routing_check_digit("123")


entry_st = st.fixed_dictionaries(
    {
        "code": st.sampled_from(["22", "32", "27", "37", "23"]),
        "routing": st.sampled_from(VALID_ROUTINGS),
        "account": st.text(alphabet="0123456789ABCDEF", min_size=1, max_size=17),
        "amount": st.integers(min_value=0, max_value=99_999_999),
        "name": st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ &-", min_size=0, max_size=30),
    }
)


@settings(max_examples=150, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(batches=st.lists(st.lists(entry_st, min_size=0, max_size=12), min_size=1, max_size=4))
def test_property_roundtrip(batches):
    b = _builder()
    expected = []
    for bi, entries in enumerate(batches):
        i = b.add_batch("ACME", "1234567890", "CCD", f"B{bi}", date(2026, 10, 1))
        for e in entries:
            b.add_entry(i, e["code"], e["routing"], e["account"], e["amount"], e["name"])
            expected.append(e)
    f = parse_nacha(b.build())
    assert f.integrity_issues == []
    assert len(f.entries) == len(expected)
    for got, exp in zip(f.entries, expected, strict=True):
        assert got.transaction_code == exp["code"]
        assert got.rdfi_routing == exp["routing"]
        assert got.account == exp["account"]
        assert got.amount_cents == exp["amount"]
        assert got.receiver_name == exp["name"][:22].strip()
    assert f.total_credit_cents == sum(e["amount"] for e in expected if e["code"] in ("22", "32", "23"))


@settings(max_examples=400, deadline=None)
@given(data=st.binary(max_size=3000))
def test_fuzz_bytes_never_crash(data):
    with contextlib.suppress(NachaParseError):
        parse_nacha(data)


@settings(max_examples=300, deadline=None)
@given(
    lines=st.lists(st.text(alphabet="0123456789 ABCDEFGHIJ", min_size=0, max_size=100), max_size=30),
    first=st.sampled_from(["1", "5", "6", "7", "8", "9"]),
)
def test_fuzz_structured_never_crash(lines, first):
    hdr = _builder().build().splitlines()[0]
    text = "\n".join([hdr] + [first + ln for ln in lines])
    with contextlib.suppress(NachaParseError):
        parse_nacha(text)
