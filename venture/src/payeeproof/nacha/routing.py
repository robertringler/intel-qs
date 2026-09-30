"""ABA routing number validation."""

from __future__ import annotations

_WEIGHTS = (3, 7, 1, 3, 7, 1, 3, 7)


def routing_check_digit(first8: str) -> int:
    if len(first8) != 8 or not first8.isdigit():
        raise ValueError("routing prefix must be 8 digits")
    total = sum(int(d) * w for d, w in zip(first8, _WEIGHTS, strict=True))
    return (10 - total % 10) % 10


def is_valid_routing(routing: str) -> bool:
    if len(routing) != 9 or not routing.isdigit():
        return False
    if routing == "000000000":
        return False
    return routing_check_digit(routing[:8]) == int(routing[8])
