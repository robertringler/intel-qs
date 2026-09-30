"""Strict parser for NACHA (ACH) files.

Validates record structure and order, numeric fields and control totals. Control
total mismatches are *not* fatal: they are reported as integrity findings, since
a file modified after generation (e.g. an altered amount) is precisely what the
screen must surface rather than reject silently.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .routing import is_valid_routing

RECORD_LEN = 94
MAX_ENTRIES = 100_000

CREDIT_CODES = {"22", "23", "24", "32", "33", "34", "42", "43", "44", "52", "53", "54"}
DEBIT_CODES = {"27", "28", "29", "37", "38", "39", "47", "48", "49", "55", "56"}
PRENOTE_CODES = {"23", "28", "33", "38", "43", "48", "53"}
RETURN_CODES = {"21", "26", "31", "36", "41", "46", "51", "56"}
SAVINGS_CODES = {"32", "33", "34", "37", "38", "39"}


class NachaParseError(ValueError):
    def __init__(self, message: str, line: int | None = None):
        self.line = line
        super().__init__(f"line {line}: {message}" if line else message)


@dataclass
class Entry:
    index: int  # 0-based index across the file
    line: int
    batch_number: int
    sec_code: str
    transaction_code: str
    rdfi_routing: str  # 9 digits incl. check digit (as found in the file)
    rdfi_routing_valid: bool
    account: str  # raw account (trimmed)
    amount_cents: int
    individual_id: str
    receiver_name: str
    trace_number: str
    addenda: list[str] = field(default_factory=list)

    @property
    def is_credit(self) -> bool:
        return self.transaction_code in CREDIT_CODES

    @property
    def is_debit(self) -> bool:
        return self.transaction_code in DEBIT_CODES

    @property
    def is_prenote(self) -> bool:
        return self.transaction_code in PRENOTE_CODES

    @property
    def account_type(self) -> str:
        return "savings" if self.transaction_code in SAVINGS_CODES else "checking"


@dataclass
class Batch:
    number: int
    line: int
    service_class: str
    company_name: str
    company_id: str
    sec_code: str
    entry_description: str
    effective_date: str
    odfi: str
    entries: list[Entry] = field(default_factory=list)
    control: dict[str, int] | None = None


@dataclass
class NachaFile:
    immediate_destination: str
    immediate_origin: str
    creation_date: str
    destination_name: str
    origin_name: str
    batches: list[Batch]
    integrity_issues: list[str]
    file_control: dict[str, int] | None

    @property
    def entries(self) -> list[Entry]:
        return [e for b in self.batches for e in b.entries]

    @property
    def total_credit_cents(self) -> int:
        return sum(e.amount_cents for e in self.entries if e.is_credit)

    @property
    def total_debit_cents(self) -> int:
        return sum(e.amount_cents for e in self.entries if e.is_debit)


def _split_records(data: str) -> list[str]:
    data = data.replace("\r\n", "\n").replace("\r", "\n")
    lines = data.split("\n")
    if len(lines) == 1 and len(lines[0]) > RECORD_LEN and len(lines[0].rstrip()) % RECORD_LEN == 0:
        blob = lines[0].rstrip()
        lines = [blob[i : i + RECORD_LEN] for i in range(0, len(blob), RECORD_LEN)]
    out: list[str] = []
    for ln in lines:
        if ln.strip() == "":
            continue
        out.append(ln)
    return out


def _num(value: str, what: str, line: int) -> int:
    v = value.strip()
    if not v:
        return 0
    if not v.isdigit():
        raise NachaParseError(f"{what} is not numeric: {value!r}", line)
    return int(v)


def parse_nacha(raw: bytes | str) -> NachaFile:
    if isinstance(raw, bytes):
        try:
            text = raw.decode("ascii")
        except UnicodeDecodeError as exc:
            raise NachaParseError("file is not ASCII (NACHA files must be ASCII)") from exc
    else:
        text = raw
    records = _split_records(text)
    if not records:
        raise NachaParseError("file is empty")

    header: dict[str, str] | None = None
    batches: list[Batch] = []
    current: Batch | None = None
    last_entry: Entry | None = None
    integrity: list[str] = []
    file_control: dict[str, int] | None = None
    entry_index = 0
    seen_file_control = False

    for lineno, raw_rec in enumerate(records, start=1):
        if len(raw_rec) > RECORD_LEN and raw_rec[RECORD_LEN:].strip():
            raise NachaParseError(f"record longer than {RECORD_LEN} characters", lineno)
        rec = raw_rec[:RECORD_LEN].ljust(RECORD_LEN)
        if any(ord(ch) < 32 or ord(ch) > 126 for ch in rec):
            raise NachaParseError("record contains non-printable characters", lineno)
        rtype = rec[0]

        if seen_file_control:
            if rtype == "9" and set(rec) == {"9"}:
                continue  # block padding
            raise NachaParseError("records after file control record", lineno)

        if rtype == "1":
            if header is not None:
                raise NachaParseError("duplicate file header", lineno)
            if rec[34:37] != "094":
                raise NachaParseError("record size field must be 094", lineno)
            header = {
                "dest": rec[3:13].strip(),
                "origin": rec[13:23].strip(),
                "date": rec[23:29],
                "dest_name": rec[40:63].strip(),
                "origin_name": rec[63:86].strip(),
            }
        elif header is None:
            raise NachaParseError("file must start with a file header (record type 1)", lineno)
        elif rtype == "5":
            if current is not None:
                raise NachaParseError("batch header before previous batch control", lineno)
            current = Batch(
                number=_num(rec[87:94], "batch number", lineno),
                line=lineno,
                service_class=rec[1:4],
                company_name=rec[4:20].strip(),
                company_id=rec[40:50].strip(),
                sec_code=rec[50:53].strip(),
                entry_description=rec[53:63].strip(),
                effective_date=rec[69:75].strip(),
                odfi=rec[79:87].strip(),
            )
            last_entry = None
        elif rtype == "6":
            if current is None:
                raise NachaParseError("entry detail outside a batch", lineno)
            if entry_index >= MAX_ENTRIES:
                raise NachaParseError(f"more than {MAX_ENTRIES} entries", lineno)
            tcode = rec[1:3]
            if not tcode.isdigit():
                raise NachaParseError("transaction code not numeric", lineno)
            rdfi8 = rec[3:11]
            chk = rec[11]
            routing = rdfi8 + chk
            if not routing.isdigit():
                raise NachaParseError("receiving DFI routing not numeric", lineno)
            if current.sec_code == "IAT":
                account = rec[39:74].strip()
                name = ""
                indiv = ""
            else:
                account = rec[12:29].strip()
                indiv = rec[39:54].strip()
                name = rec[54:76].strip()
            amount = _num(rec[29:39], "amount", lineno)
            last_entry = Entry(
                index=entry_index,
                line=lineno,
                batch_number=current.number,
                sec_code=current.sec_code,
                transaction_code=tcode,
                rdfi_routing=routing,
                rdfi_routing_valid=is_valid_routing(routing),
                account=account,
                amount_cents=amount,
                individual_id=indiv,
                receiver_name=name,
                trace_number=rec[79:94].strip(),
            )
            current.entries.append(last_entry)
            entry_index += 1
        elif rtype == "7":
            if last_entry is None:
                raise NachaParseError("addenda without preceding entry", lineno)
            last_entry.addenda.append(rec[3:83].rstrip())
            if current is not None and current.sec_code == "IAT" and rec[1:3] == "10":
                last_entry.receiver_name = rec[46:81].strip()
        elif rtype == "8":
            if current is None:
                raise NachaParseError("batch control without batch header", lineno)
            ctrl = {
                "entry_addenda_count": _num(rec[4:10], "entry/addenda count", lineno),
                "entry_hash": _num(rec[10:20], "entry hash", lineno),
                "total_debit": _num(rec[20:32], "total debit", lineno),
                "total_credit": _num(rec[32:44], "total credit", lineno),
            }
            current.control = ctrl
            _check_batch(current, integrity)
            batches.append(current)
            current = None
            last_entry = None
        elif rtype == "9":
            if current is not None:
                raise NachaParseError("file control inside an open batch", lineno)
            file_control = {
                "batch_count": _num(rec[1:7], "batch count", lineno),
                "entry_addenda_count": _num(rec[13:21], "entry/addenda count", lineno),
                "entry_hash": _num(rec[21:31], "entry hash", lineno),
                "total_debit": _num(rec[31:43], "total debit", lineno),
                "total_credit": _num(rec[43:55], "total credit", lineno),
            }
            seen_file_control = True
        else:
            raise NachaParseError(f"unknown record type {rtype!r}", lineno)

    if header is None:
        raise NachaParseError("missing file header")
    if current is not None:
        raise NachaParseError("file ended inside an open batch (missing batch control)")
    if file_control is None:
        integrity.append("File control record (type 9) is missing.")
    else:
        _check_file(batches, file_control, integrity)

    return NachaFile(
        immediate_destination=header["dest"],
        immediate_origin=header["origin"],
        creation_date=header["date"],
        destination_name=header["dest_name"],
        origin_name=header["origin_name"],
        batches=batches,
        integrity_issues=integrity,
        file_control=file_control,
    )


def _entry_hash(entries: list[Entry]) -> int:
    return sum(int(e.rdfi_routing[:8]) for e in entries) % 10**10


def _check_batch(b: Batch, issues: list[str]) -> None:
    if b.control is None:
        return
    count = len(b.entries) + sum(len(e.addenda) for e in b.entries)
    debit = sum(e.amount_cents for e in b.entries if e.is_debit)
    credit = sum(e.amount_cents for e in b.entries if e.is_credit)
    if b.control["entry_addenda_count"] != count:
        issues.append(f"Batch {b.number}: entry/addenda count {b.control['entry_addenda_count']} != actual {count}.")
    if b.control["entry_hash"] != _entry_hash(b.entries):
        issues.append(f"Batch {b.number}: entry hash does not match receiving routing numbers.")
    if b.control["total_debit"] != debit:
        issues.append(f"Batch {b.number}: control total debit {b.control['total_debit']} != entries {debit}.")
    if b.control["total_credit"] != credit:
        issues.append(f"Batch {b.number}: control total credit {b.control['total_credit']} != entries {credit}.")


def _check_file(batches: list[Batch], fc: dict[str, int], issues: list[str]) -> None:
    entries = [e for b in batches for e in b.entries]
    count = len(entries) + sum(len(e.addenda) for e in entries)
    if fc["batch_count"] != len(batches):
        issues.append(f"File control batch count {fc['batch_count']} != actual {len(batches)}.")
    if fc["entry_addenda_count"] != count:
        issues.append(f"File control entry/addenda count {fc['entry_addenda_count']} != actual {count}.")
    if fc["entry_hash"] != _entry_hash(entries):
        issues.append("File control entry hash does not match.")
    debit = sum(e.amount_cents for e in entries if e.is_debit)
    credit = sum(e.amount_cents for e in entries if e.is_credit)
    if fc["total_debit"] != debit:
        issues.append(f"File control total debit {fc['total_debit']} != entries {debit}.")
    if fc["total_credit"] != credit:
        issues.append(f"File control total credit {fc['total_credit']} != entries {credit}.")
