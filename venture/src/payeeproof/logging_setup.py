"""JSON structured logging with request correlation and secret redaction."""

from __future__ import annotations

import contextvars
import json
import logging
import re
import sys
from datetime import UTC, datetime

request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("request_id", default=None)

_REDACT_KEYS = {
    "password",
    "token",
    "secret",
    "authorization",
    "cookie",
    "account",
    "account_number",
    "totp",
    "csrf_token",
    "api_key",
    "body",
}
_KEY_PATTERN = re.compile(r"pp_[a-z0-9]{12}_[A-Za-z0-9_\-]+")
_STD = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__) | {"message", "asctime"}


class JsonFormatter(logging.Formatter):
    def __init__(self, env: str):
        super().__init__()
        self.env = env

    def format(self, record: logging.LogRecord) -> str:
        out = {
            "ts": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": _KEY_PATTERN.sub("pp_[redacted]", record.getMessage()),
            "request_id": request_id_var.get(),
        }
        for k, v in record.__dict__.items():
            if k in _STD or k.startswith("_"):
                continue
            if k.lower() in _REDACT_KEYS and not (self.env == "development" and k == "body"):
                out[k] = "[redacted]"
            else:
                safe = isinstance(v, (int, float, bool, type(None)))
                out[k] = v if safe else _KEY_PATTERN.sub("pp_[redacted]", str(v))
        if record.exc_info:
            out["exc"] = self.formatException(record.exc_info)
        return json.dumps(out, default=str)


def setup(level: str, env: str) -> None:
    root = logging.getLogger()
    root.handlers.clear()
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(JsonFormatter(env))
    root.addHandler(h)
    root.setLevel(level.upper())
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
