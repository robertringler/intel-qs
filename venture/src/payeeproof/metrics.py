"""Prometheus metrics (exposed at /metrics behind a bearer token)."""

from prometheus_client import Counter, Histogram

HTTP_REQUESTS = Counter("pp_http_requests_total", "HTTP requests", ["method", "route", "status"])
HTTP_LATENCY = Histogram("pp_http_request_seconds", "HTTP request latency", ["method", "route"])
SCREENINGS = Counter("pp_screenings_total", "Screening runs", ["status"])
FINDINGS = Counter("pp_screening_findings_total", "Screening findings by rule", ["rule"])
LOGIN_FAILURES = Counter("pp_login_failures_total", "Failed logins")
JOBS = Counter("pp_jobs_total", "Background jobs processed", ["kind", "result"])
