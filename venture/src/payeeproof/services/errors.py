"""Domain errors mapped to HTTP responses by the web layer."""


class DomainError(Exception):
    status_code = 400
    code = "bad_request"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFound(DomainError):
    status_code = 404
    code = "not_found"


class Forbidden(DomainError):
    status_code = 403
    code = "forbidden"


class Conflict(DomainError):
    status_code = 409
    code = "conflict"


class ValidationFailed(DomainError):
    status_code = 422
    code = "validation_failed"


class PlanLimit(DomainError):
    status_code = 402
    code = "plan_limit"


class RateLimited(DomainError):
    status_code = 429
    code = "rate_limited"
