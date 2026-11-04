from typing import Any


class DomainError(Exception):
    """Base class for domain-level business rule violations.

    Services raise DomainError (or a subclass) instead of leaking raw database
    errors, ValidationError, or framework-specific HTTP exceptions.
    """

    default_message: str = "A domain error occurred."
    default_code: str = "domain_error"
    http_status: int = 400

    def __init__(
        self,
        message: str | None = None,
        *,
        code: str | None = None,
        http_status: int | None = None,
        extra: dict[str, Any] | None = None,
    ):
        self.message = message or self.default_message
        self.code = code or self.default_code
        if http_status is not None:
            self.http_status = http_status
        self.extra = extra or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "code": self.code,
            "message": self.message,
        }
        if self.extra:
            data.update(self.extra)
        return data
