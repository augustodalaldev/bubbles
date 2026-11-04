from apps.core.exceptions import DomainError


class InsufficientSoap(DomainError):
    default_message = "Insufficient soap balance."
    default_code = "insufficient_soap"
    http_status = 409

    def __init__(
        self,
        message: str | None = None,
        *,
        cost: int | None = None,
        balance: int | None = None,
        **kwargs,
    ):
        extra = kwargs.pop("extra", {})
        if cost is not None:
            extra["cost"] = cost
        if balance is not None:
            extra["balance"] = balance
        super().__init__(message=message, extra=extra, **kwargs)
        self.cost = cost
        self.balance = balance


__all__ = ["DomainError", "InsufficientSoap"]
