"""TOTP (RFC 6238) multi-factor authentication helpers."""

from __future__ import annotations

import io
import re
from datetime import UTC, datetime

import pyotp
import qrcode
import qrcode.image.svg

_CODE = re.compile(r"^\d{6}$")


def new_secret() -> str:
    return pyotp.random_base32()


def provisioning_uri(secret: str, email: str, issuer: str) -> str:
    return pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer)


def verify(secret: str, code: str, last_used_step: int | None) -> int | None:
    """Verify a code allowing +/-1 step of clock drift.

    Returns the matched time step, or None. A step equal to or earlier than
    ``last_used_step`` is rejected to prevent replay of an observed code.
    """
    code = code.strip().replace(" ", "")
    if not _CODE.match(code):
        return None
    totp = pyotp.TOTP(secret)
    now_step = int(totp.timecode(datetime.now(UTC)))
    for step in (now_step - 1, now_step, now_step + 1):
        if last_used_step is not None and step <= last_used_step:
            continue
        if pyotp.utils.strings_equal(totp.generate_otp(step), code):
            return step
    return None


def qr_svg(uri: str) -> str:
    img = qrcode.make(uri, image_factory=qrcode.image.svg.SvgPathImage, box_size=8, border=2)
    buf = io.BytesIO()
    img.save(buf)
    svg = buf.getvalue().decode()
    # Strip XML declaration so it can be inlined in HTML.
    return svg.split("?>", 1)[-1].strip()
