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


def list_admin_users(*, query: str = "", status: str = "") -> QuerySet:
    """Users for the moderation screen. Deleted (anonymized) accounts are left out."""
    from django.contrib.auth import get_user_model
    from django.db.models import Q
    from django.utils import timezone

    qs = get_user_model().objects.filter(deleted_at__isnull=True)
    if query:
        qs = qs.filter(Q(username__icontains=query) | Q(name__icontains=query))
    now = timezone.now()
    if status == "BANNED":
        qs = qs.filter(status="BANNED")
    elif status == "SUSPENDED":
        qs = qs.filter(status="SUSPENDED").filter(
            Q(suspended_until__isnull=True) | Q(suspended_until__gt=now)
        )
    elif status == "ACTIVE":
        qs = qs.exclude(status="BANNED").exclude(
            Q(status="SUSPENDED") & (Q(suspended_until__isnull=True) | Q(suspended_until__gt=now))
        )
    return qs.order_by("username")


def list_admin_communities(*, query: str = "", status: str = "") -> QuerySet:
    """Communities for the moderation screen. Deleted communities are left out."""
    from django.db.models import Q

    from apps.communities.models import Community, not_moderated_q

    qs = Community.objects.filter(deleted_at__isnull=True)
    if query:
        qs = qs.filter(Q(commname__icontains=query) | Q(name__icontains=query))
    if status == "BANNED":
        qs = qs.filter(blocked_at__isnull=False)
    elif status == "SUSPENDED":
        qs = qs.filter(blocked_at__isnull=True, suspended_until__isnull=False).exclude(
            not_moderated_q()
        )
    elif status == "ACTIVE":
        qs = qs.filter(not_moderated_q())
    return qs.order_by("commname")


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
