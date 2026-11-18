from typing import Any

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

from .messages import MESSAGES, message_for


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


def _flatten_errors(detail: Any, prefix: str = "") -> dict[str, list[str]]:
    """Flatten DRF error details (nested dicts/lists, ListField indexes) into field -> messages.

    Keys use dotted paths for nested serializers and `[n]` for list items, e.g.
    `media_files[0]` or `slots.avatar_frame`.
    """
    out: dict[str, list[str]] = {}
    if isinstance(detail, dict):
        for key, value in detail.items():
            if isinstance(key, int):
                path = f"{prefix}[{key}]"
            else:
                path = f"{prefix}.{key}" if prefix else str(key)
            out.update(_flatten_errors(value, path))
    elif isinstance(detail, list | tuple):
        messages = [str(item) for item in detail if not isinstance(item, dict | list | tuple)]
        if messages:
            out[prefix or "non_field_errors"] = messages
        for index, item in enumerate(detail):
            if isinstance(item, dict | list | tuple):
                out.update(_flatten_errors(item, f"{prefix}[{index}]"))
    else:
        out[prefix or "non_field_errors"] = [str(detail)]
    return out


def _envelope(code: str, message: str, fields: dict[str, list[str]] | None = None) -> dict:
    return {"error": {"code": code, "message": message, "fields": fields or None}}


def _validation_envelope(detail: Any) -> dict:
    flat = _flatten_errors(detail)
    message = message_for("validation_error")
    for key in ("non_field_errors", "detail"):
        messages = flat.pop(key, None)
        if messages:
            message = messages[0]
    return _envelope("validation_error", message, flat)


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """DRF exception handler producing uniform error envelopes:

    {"error": {"code": "...", "message": "...", "fields": ...}}

    Anything that is not handled here returns None and becomes a 500 (rendered as JSON for
    /api/ paths by `apps.core.views.api_server_error`).
    """
    if isinstance(exc, DomainError):
        fields = exc.extra.get("fields") if exc.extra else None
        message = message_for(exc.code, exc.message, exc.extra)
        if fields and exc.code in MESSAGES:
            fields = {name: [message] for name in fields}
        error_payload: dict[str, Any] = {
            "code": exc.code,
            "message": message,
            "fields": fields,
        }
        if exc.extra:
            for k, v in exc.extra.items():
                if k != "fields" and k not in error_payload:
                    error_payload[k] = v
        return Response({"error": error_payload}, status=exc.http_status)

    if isinstance(exc, DjangoValidationError):
        detail = exc.message_dict if hasattr(exc, "error_dict") else list(exc.messages)
        return Response(_validation_envelope(detail), status=status.HTTP_400_BAD_REQUEST)

    if isinstance(exc, IntegrityError):
        return Response(
            _envelope("conflict", message_for("conflict")),
            status=status.HTTP_409_CONFLICT,
        )

    response = exception_handler(exc, context)
    if response is None:
        return None

    # Mutate the response (instead of building a new one) so headers such as
    # Retry-After and WWW-Authenticate survive.
    if isinstance(exc, ValidationError):
        response.data = _validation_envelope(exc.detail)
    elif isinstance(exc, Http404):
        response.data = _envelope("not_found", message_for("not_found"))
    elif isinstance(exc, DjangoPermissionDenied):
        response.data = _envelope("permission_denied", message_for("permission_denied"))
    elif isinstance(exc, APIException):
        detail = exc.detail
        code = str(getattr(detail, "code", None) or exc.default_code)
        if code in ("token_not_valid", "not_authenticated") and isinstance(detail, dict):
            # simplejwt adds noisy `messages`/`code` keys: keep only the clean message.
            response.data = _envelope(code, message_for(code, str(detail.get("detail", ""))))
        elif isinstance(detail, dict):
            flat = _flatten_errors({k: v for k, v in detail.items() if k != "detail"})
            main = detail.get("detail")
            message = str(main) if main else "An error occurred."
            response.data = _envelope(code, message, flat)
        elif isinstance(detail, list):
            response.data = _envelope(code, str(detail[0]) if detail else "An error occurred.")
        else:
            response.data = _envelope(code, str(detail))
    else:
        response.data = _envelope("api_error", message_for("api_error", str(exc)))

    return response
