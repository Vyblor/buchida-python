class BuchidaError(Exception):
    """Base error for buchida API errors."""

    def __init__(self, message: str, status_code: int, code: str | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code


class AuthenticationError(BuchidaError):
    """401 — Invalid API key."""

    def __init__(self, message: str = "Invalid API key"):
        super().__init__(message, 401, "authentication_error")


class RateLimitError(BuchidaError):
    """429 — Rate limit exceeded."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, 429, "rate_limit_error")


class NotFoundError(BuchidaError):
    """404 — Resource not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404, "not_found")


class ValidationError(BuchidaError):
    """422 — Validation failed."""

    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, 422, "validation_error")
