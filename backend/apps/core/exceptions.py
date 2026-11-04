from typing import Any

from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler


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


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """DRF exception handler producing uniform error envelopes:

    {"error": {"code": "...", "message": "...", "fields": ...}}
    """
    if isinstance(exc, DomainError):
        fields = exc.extra.get("fields") if exc.extra else None
        error_payload: dict[str, Any] = {
            "code": exc.code,
            "message": exc.message,
            "fields": fields,
        }
        if exc.extra:
            for k, v in exc.extra.items():
                if k != "fields" and k not in error_payload:
                    error_payload[k] = v
        return Response({"error": error_payload}, status=exc.http_status)

    response = exception_handler(exc, context)
    if response is None:
        return None

    code = "api_error"
    message = "An error occurred."
    fields = None

    if isinstance(exc, ValidationError):
        code = "validation_error"
        message = "Invalid input."
        detail = exc.detail
        if isinstance(detail, dict):
            fields = {}
            for k, v in detail.items():
                if k in ("non_field_errors", "detail"):
                    if isinstance(v, list) and v:
                        message = str(v[0])
                    elif isinstance(v, str):
                        message = v
                else:
                    fields[k] = [str(item) for item in v] if isinstance(v, list) else [str(v)]
            if not fields:
                fields = None
        elif isinstance(detail, list):
            message = str(detail[0]) if detail else "Invalid input."
        else:
            message = str(detail)

    elif isinstance(exc, APIException):
        code = getattr(exc, "default_code", "api_error")
        detail = exc.detail
        if hasattr(detail, "code") and detail.code:
            code = str(detail.code)
        if isinstance(detail, str):
            message = detail
        elif isinstance(detail, list) and detail:
            message = str(detail[0])
        elif isinstance(detail, dict):
            message = str(detail.get("detail", "An error occurred."))
            fields = {
                k: [str(i) for i in v] if isinstance(v, list) else [str(v)]
                for k, v in detail.items()
                if k != "detail"
            } or None
        else:
            message = str(detail)
    else:
        message = str(exc)

    return Response(
        {
            "error": {
                "code": code,
                "message": message,
                "fields": fields,
            }
        },
        status=response.status_code,
    )
