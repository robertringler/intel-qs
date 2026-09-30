"""Fixed-window rate limiting with Redis (multi-instance) or in-memory backends."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Limit:
    name: str
    max_hits: int
    window_seconds: int


LOGIN_IP = Limit("login-ip", 20, 60)
SIGNUP_IP = Limit("signup-ip", 5, 3600)
MFA_SESSION = Limit("mfa-session", 10, 300)
API_KEY = Limit("api-key", 600, 60)
PUBLIC_ATTEST_IP = Limit("attest-ip", 30, 60)
UPLOAD_ORG = Limit("upload-org", 60, 60)
PASSWORD_RESET_IP = Limit("pwreset-ip", 5, 3600)


class Backend(Protocol):
    def hit(self, key: str, window_seconds: int) -> int: ...


class MemoryBackend:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counts: dict[str, tuple[int, float]] = {}

    def hit(self, key: str, window_seconds: int) -> int:
        now = time.monotonic()
        with self._lock:
            count, expires = self._counts.get(key, (0, now + window_seconds))
            if now >= expires:
                count, expires = 0, now + window_seconds
            count += 1
            self._counts[key] = (count, expires)
            if len(self._counts) > 100_000:  # bound memory
                self._counts = {k: v for k, v in self._counts.items() if v[1] > now}
            return count

    def reset(self) -> None:
        with self._lock:
            self._counts.clear()


class RedisBackend:
    def __init__(self, url: str):
        import redis

        self._r = redis.Redis.from_url(url, socket_timeout=0.5, socket_connect_timeout=0.5)

    def hit(self, key: str, window_seconds: int) -> int:
        bucket = int(time.time() // window_seconds)
        k = f"pp:rl:{key}:{bucket}"
        pipe = self._r.pipeline()
        pipe.incr(k)
        pipe.expire(k, window_seconds + 1)
        count, _ = pipe.execute()
        return int(count)


class RateLimiter:
    def __init__(self, backend: Backend):
        self.backend = backend

    def allow(self, limit: Limit, subject: str) -> bool:
        try:
            return self.backend.hit(f"{limit.name}:{subject}", limit.window_seconds) <= limit.max_hits
        except Exception:
            # Fail open on limiter outage only for availability; login lockout (DB-backed)
            # still protects accounts. The failure is logged by the caller's middleware.
            return True
