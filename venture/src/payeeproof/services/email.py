"""Outbound email. Backends: smtp (production), console (development), memory (tests)."""

from __future__ import annotations

import logging
import smtplib
import ssl
from dataclasses import dataclass
from email.message import EmailMessage

from ..config import get_settings

log = logging.getLogger("payeeproof.email")


@dataclass
class Sent:
    to: str
    subject: str
    text: str


OUTBOX: list[Sent] = []  # memory backend (tests only)


class EmailError(RuntimeError):
    pass


def send(to: str, subject: str, text: str) -> None:
    s = get_settings()
    if "\n" in subject or "\r" in subject or "\n" in to or "\r" in to:
        raise EmailError("header injection attempt")
    if s.email_backend == "memory":
        OUTBOX.append(Sent(to, subject, text))
        return
    if s.email_backend == "console":
        log.info("email (console backend)", extra={"to": to, "subject": subject, "body": text})
        return
    if not s.smtp_host:
        raise EmailError("SMTP host is not configured")
    msg = EmailMessage()
    msg["From"] = s.email_from
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(text)
    try:
        with smtplib.SMTP(s.smtp_host, s.smtp_port, timeout=20) as smtp:
            if s.smtp_starttls:
                smtp.starttls(context=ssl.create_default_context())
            if s.smtp_username and s.smtp_password:
                smtp.login(s.smtp_username, s.smtp_password)
            smtp.send_message(msg)
    except (OSError, smtplib.SMTPException) as exc:
        raise EmailError(f"SMTP delivery failed: {type(exc).__name__}") from exc
