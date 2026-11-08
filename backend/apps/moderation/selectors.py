from typing import Any

from django.db.models import QuerySet

from apps.moderation.models import AuditLog, Report


def list_reports(
    *,
    status: str | None = None,
    target_type: str | None = None,
    reporter: Any = None,
) -> QuerySet[Report]:
    """List moderation reports with optional filters."""
    qs = Report.objects.select_related("reporter", "reviewed_by").all()
    if status:
        qs = qs.filter(status=status)
    if target_type:
        qs = qs.filter(target_type=target_type)
    if reporter:
        qs = qs.filter(reporter=reporter)
    return qs.order_by("-created_at")


def list_audit_logs(
    *,
    action: str | None = None,
    target_type: str | None = None,
    actor: Any = None,
) -> QuerySet[AuditLog]:
    """List administrative audit logs with optional filters."""
    qs = AuditLog.objects.select_related("actor").all()
    if action:
        qs = qs.filter(action=action)
    if target_type:
        qs = qs.filter(target_type=target_type)
    if actor:
        qs = qs.filter(actor=actor)
    return qs.order_by("-created_at")
