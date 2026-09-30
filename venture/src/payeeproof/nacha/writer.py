"""Builder for NACHA files (used for prenote generation and test fixtures)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime

from .parser import CREDIT_CODES, DEBIT_CODES, RECORD_LEN
from .routing import is_valid_routing

_ALLOWED = re.compile(r"[^A-Z0-9 &\-.,/'#()]")


def _alpha(value: str, width: int) -> str:
    v = _ALLOWED.sub(" ", value.upper())[:width]
    return v.ljust(width)


def _numf(value: int, width: int) -> str:
    s = str(value)
    if len(s) > width or value < 0:
        raise ValueError(f"numeric field overflow: {value} into {width}")
    return s.rjust(width, "0")


@dataclass
class _Entry:
    transaction_code: str
    routing: str
    account: str
    amount_cents: int
    individual_id: str
    name: str


@dataclass
class _Batch:
    company_name: str
    company_id: str
    sec_code: str
    description: str
    effective_date: date
    entries: list[_Entry] = field(default_factory=list)


class NachaFileBuilder:
    def __init__(
        self,
        immediate_destination: str,
        immediate_origin: str,
        destination_name: str,
        origin_name: str,
        odfi_routing: str,
        created: datetime | None = None,
        file_id_modifier: str = "A",
    ):
        if not is_valid_routing(immediate_destination):
            raise ValueError("immediate destination must be a valid routing number")
        if not is_valid_routing(odfi_routing):
            raise ValueError("ODFI routing must be a valid routing number")
        if not re.fullmatch(r"[0-9A-Za-z ]{1,10}", immediate_origin):
            raise ValueError("immediate origin must be 1-10 alphanumeric characters")
        if not re.fullmatch(r"[A-Z0-9]", file_id_modifier):
            raise ValueError("file id modifier must be A-Z or 0-9")
        self.dest = immediate_destination
        self.origin = immediate_origin
        self.dest_name = destination_name
        self.origin_name = origin_name
        self.odfi = odfi_routing
        self.created = created or datetime.now()
        self.modifier = file_id_modifier
        self.batches: list[_Batch] = []

    def add_batch(
        self, company_name: str, company_id: str, sec_code: str, description: str, effective_date: date
    ) -> int:
        if sec_code not in {"PPD", "CCD", "CTX", "WEB", "TEL"}:
            raise ValueError("unsupported SEC code")
        if not re.fullmatch(r"[0-9A-Za-z ]{1,10}", company_id):
            raise ValueError("company id must be 1-10 alphanumeric characters")
        self.batches.append(_Batch(company_name, company_id, sec_code, description, effective_date))
        return len(self.batches) - 1

    def add_entry(
        self,
        batch: int,
        transaction_code: str,
        routing: str,
        account: str,
        amount_cents: int,
        name: str,
        individual_id: str = "",
    ) -> None:
        if transaction_code not in CREDIT_CODES | DEBIT_CODES:
            raise ValueError("unsupported transaction code")
        if not (len(routing) == 9 and routing.isdigit()):
            raise ValueError("routing must be 9 digits")
        if not re.fullmatch(r"[0-9A-Za-z\-]{1,17}", account):
            raise ValueError("account must be 1-17 alphanumeric characters")
        if amount_cents < 0 or amount_cents > 99_999_999_99:
            raise ValueError("amount out of range")
        self.batches[batch].entries.append(
            _Entry(transaction_code, routing, account, amount_cents, individual_id, name)
        )

    def build(self) -> str:
        recs: list[str] = []
        recs.append(
            "1"
            + "01"
            + (" " + self.dest)
            + self.origin.rjust(10)
            + self.created.strftime("%y%m%d")
            + self.created.strftime("%H%M")
            + self.modifier
            + "094"
            + "10"
            + "1"
            + _alpha(self.dest_name, 23)
            + _alpha(self.origin_name, 23)
            + " " * 8
        )
        total_entries = 0
        total_hash = 0
        total_debit = 0
        total_credit = 0
        for bno, b in enumerate(self.batches, start=1):
            has_c = any(e.transaction_code in CREDIT_CODES for e in b.entries)
            has_d = any(e.transaction_code in DEBIT_CODES for e in b.entries)
            scc = "200" if (has_c and has_d) or not b.entries else ("220" if has_c else "225")
            recs.append(
                "5"
                + scc
                + _alpha(b.company_name, 16)
                + " " * 20
                + b.company_id.rjust(10)
                + b.sec_code
                + _alpha(b.description, 10)
                + " " * 6
                + b.effective_date.strftime("%y%m%d")
                + "   "
                + "1"
                + self.odfi[:8]
                + _numf(bno, 7)
            )
            bhash = 0
            bdebit = 0
            bcredit = 0
            for seq, e in enumerate(b.entries, start=1):
                trace = self.odfi[:8] + _numf(seq + total_entries, 7)
                recs.append(
                    "6"
                    + e.transaction_code
                    + e.routing[:8]
                    + e.routing[8]
                    + e.account.ljust(17)
                    + _numf(e.amount_cents, 10)
                    + _alpha(e.individual_id, 15)
                    + _alpha(e.name, 22)
                    + "  "
                    + "0"
                    + trace
                )
                bhash += int(e.routing[:8])
                if e.transaction_code in DEBIT_CODES:
                    bdebit += e.amount_cents
                else:
                    bcredit += e.amount_cents
            recs.append(
                "8"
                + scc
                + _numf(len(b.entries), 6)
                + _numf(bhash % 10**10, 10)
                + _numf(bdebit, 12)
                + _numf(bcredit, 12)
                + b.company_id.rjust(10)
                + " " * 19
                + " " * 6
                + self.odfi[:8]
                + _numf(bno, 7)
            )
            total_entries += len(b.entries)
            total_hash += bhash
            total_debit += bdebit
            total_credit += bcredit
        n_records = len(recs) + 1
        blocks = (n_records + 9) // 10
        recs.append(
            "9"
            + _numf(len(self.batches), 6)
            + _numf(blocks, 6)
            + _numf(total_entries, 8)
            + _numf(total_hash % 10**10, 10)
            + _numf(total_debit, 12)
            + _numf(total_credit, 12)
            + " " * 39
        )
        while len(recs) % 10:
            recs.append("9" * RECORD_LEN)
        for r in recs:
            if len(r) != RECORD_LEN:
                raise AssertionError(f"internal error: record length {len(r)}")
        return "\n".join(recs) + "\n"
