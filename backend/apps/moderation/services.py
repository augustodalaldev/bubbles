from datetime import timedelta
from typing import Any

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import UserStatus
from apps.communities.models import Community
from apps.content.models import Bubblegram, Comment
from apps.content.services import delete_bubblegram, delete_comment
from apps.core.exceptions import DomainError
from apps.economy.models import ActionType, Wallet
from apps.economy.services import apply_movements
from apps.moderation.models import AuditAction, AuditLog, Report, ReportStatus, ReportTargetType


def log_audit_action(
    *,
    actor: Any | None,
    action: str,
    target_type: str,
    target_id: Any,
    reason: str = "",
    metadata: dict[str, Any] | None = None,
) -> AuditLog:
    """Create an immutable entry in the administrative audit log."""
    return AuditLog.objects.create(
        actor=actor,
        action=action,
        target_type=target_type,
        target_id=str(target_id),
        reason=reason,
        metadata=metadata or {},
    )


@transaction.atomic
def file_report(
    *,
    reporter: Any,
    target_type: str,
    target_id: Any,
    reason: str,
    description: str = "",
) -> Report:
    """File a user-submitted moderation report."""
    User = get_user_model()
    target_id_str = str(target_id).strip()

    if target_type != ReportTargetType.COMMUNITY and not target_id_str.isdigit():
        raise DomainError(
            "Target id must be a number.",
            code="invalid_target_id",
            http_status=400,
            extra={"fields": {"target_id": ["Target id must be a number."]}},
        )

    if target_type == ReportTargetType.USER:
        if str(reporter.id) == target_id_str:
            raise DomainError("You cannot report yourself.", code="self_report", http_status=400)
        if not User.objects.filter(id=target_id_str).exists():
            raise DomainError("Target user does not exist.", code="user_not_found", http_status=404)

    elif target_type == ReportTargetType.COMMUNITY:
        if not Community.objects.filter(commname=target_id_str).exists():
            raise DomainError(
                "Target community does not exist.",
                code="community_not_found",
                http_status=404,
            )

    elif target_type == ReportTargetType.BUBBLEGRAM:
        if not Bubblegram.objects.filter(id=target_id_str).exists():
            raise DomainError(
                "Target bubblegram does not exist.",
                code="bubblegram_not_found",
                http_status=404,
            )

    elif target_type == ReportTargetType.COMMENT:
        if not Comment.objects.filter(id=target_id_str).exists():
            raise DomainError(
                "Target comment does not exist.",
                code="comment_not_found",
                http_status=404,
            )
    else:
        raise DomainError(
            f"Invalid report target type: {target_type}",
            code="invalid_target_type",
            http_status=400,
        )

    report = Report.objects.create(
        reporter=reporter,
        target_type=target_type,
        target_id=target_id_str,
        reason=reason,
        description=description,
    )
    return report


@transaction.atomic
def review_report(
    *,
    reviewer: Any,
    report: Report,
    status: str,
    resolution_notes: str = "",
) -> Report:
    """Review and update the status of a filed report (staff only)."""
    if not reviewer.is_staff:
        raise DomainError(
            "Only staff administrators can review reports.",
            code="permission_denied",
            http_status=403,
        )

    if status not in [ReportStatus.INVESTIGATING, ReportStatus.RESOLVED, ReportStatus.DISMISSED]:
        raise DomainError(
            f"Invalid review status: {status}",
            code="invalid_status",
            http_status=400,
        )

    report.status = status
    report.reviewed_by = reviewer
    report.reviewed_at = timezone.now()
    report.resolution_notes = resolution_notes
    report.save()

    if status == ReportStatus.INVESTIGATING:
        return report

    audit_action = (
        AuditAction.REPORT_RESOLVE
        if status == ReportStatus.RESOLVED
        else AuditAction.REPORT_DISMISS
    )
    log_audit_action(
        actor=reviewer,
        action=audit_action,
        target_type="REPORT",
        target_id=report.id,
        reason=resolution_notes,
        metadata={
            "new_status": status,
            "target_type": report.target_type,
            "target_id": report.target_id,
        },
    )
    return report


@transaction.atomic
def suspend_user(
    *,
    actor: Any,
    user: Any,
    duration_hours: int,
    reason: str = "",
) -> Any:
    """Temporarily suspend a user account (staff only)."""
    if not actor.is_staff:
        raise DomainError(
            "Only staff administrators can suspend users.",
            code="permission_denied",
            http_status=403,
        )
    if user.is_staff or user.is_superuser:
        raise DomainError(
            "Staff and superusers cannot be suspended.",
            code="cannot_suspend_staff",
            http_status=400,
        )
    if actor.id == user.id:
        raise DomainError(
            "You cannot suspend yourself.",
            code="self_action",
            http_status=400,
        )
    if duration_hours <= 0:
        raise DomainError(
            "Suspension duration must be at least 1 hour.",
            code="invalid_duration",
            http_status=400,
        )

    suspended_until = timezone.now() + timedelta(hours=duration_hours)
    user.status = UserStatus.SUSPENDED
    user.suspended_until = suspended_until
    user.moderation_reason = reason.strip()
    user.save(update_fields=["status", "suspended_until", "moderation_reason"])

    log_audit_action(
        actor=actor,
        action=AuditAction.USER_SUSPEND,
        target_type="USER",
        target_id=user.id,
        reason=reason,
        metadata={
            "duration_hours": duration_hours,
            "suspended_until": suspended_until.isoformat(),
        },
    )
    return user


@transaction.atomic
def ban_user(
    *,
    actor: Any,
    user: Any,
    reason: str = "",
) -> Any:
    """Permanently ban a user account (staff only)."""
    if not actor.is_staff:
        raise DomainError(
            "Only staff administrators can ban users.",
            code="permission_denied",
            http_status=403,
        )
    if user.is_staff or user.is_superuser:
        raise DomainError(
            "Staff and superusers cannot be banned.",
            code="cannot_ban_staff",
            http_status=400,
        )
    if actor.id == user.id:
        raise DomainError(
            "You cannot ban yourself.",
            code="self_action",
            http_status=400,
        )

    user.status = UserStatus.BANNED
    user.is_active = False
    user.suspended_until = None
    user.moderation_reason = reason.strip()
    user.save(update_fields=["status", "is_active", "suspended_until", "moderation_reason"])

    log_audit_action(
        actor=actor,
        action=AuditAction.USER_BAN,
        target_type="USER",
        target_id=user.id,
        reason=reason,
    )
    return user


@transaction.atomic
def unban_user(
    *,
    actor: Any,
    user: Any,
    reason: str = "",
) -> Any:
    """Restore a banned or suspended user account to active status (staff only)."""
    if not actor.is_staff:
        raise DomainError(
            "Only staff administrators can restore users.",
            code="permission_denied",
            http_status=403,
        )

    if user.deleted_at is not None:
        raise DomainError("User not found.", code="user_not_found", http_status=404)
    user.status = UserStatus.ACTIVE
    user.is_active = True
    user.suspended_until = None
    user.moderation_reason = ""
    user.save(update_fields=["status", "is_active", "suspended_until", "moderation_reason"])

    log_audit_action(
        actor=actor,
        action=AuditAction.USER_UNBAN,
        target_type="USER",
        target_id=user.id,
        reason=reason,
    )
    return user


@transaction.atomic
def suspend_community(
    *,
    actor: Any,
    community: Community,
    duration_hours: int,
    reason: str = "",
) -> Community:
    """Temporarily suspend a community: hidden from lists and read-only (staff only)."""
    if not actor.is_staff:
        raise DomainError(
            "Only staff administrators can suspend communities.",
            code="permission_denied",
            http_status=403,
        )
    if duration_hours <= 0:
        raise DomainError(
            "Suspension duration must be at least 1 hour.",
            code="invalid_duration",
            http_status=400,
        )
    if community.is_blocked:
        raise DomainError(
            "This community is already banned.",
            code="already_banned",
            http_status=400,
        )
    community.suspended_until = timezone.now() + timedelta(hours=duration_hours)
    community.moderation_reason = reason.strip()
    community.save(update_fields=["suspended_until", "moderation_reason"])

    log_audit_action(
        actor=actor,
        action=AuditAction.COMMUNITY_SUSPEND,
        target_type="COMMUNITY",
        target_id=community.commname,
        reason=reason,
        metadata={
            "duration_hours": duration_hours,
            "suspended_until": community.suspended_until.isoformat(),
        },
    )
    return community


@transaction.atomic
def block_community(
    *,
    actor: Any,
    community: Community,
    reason: str = "",
) -> Community:
    """Block a community permanently from interactions (staff only)."""
    if not actor.is_staff:
        raise DomainError(
            "Only staff administrators can block communities.",
            code="permission_denied",
            http_status=403,
        )

    community.blocked_at = timezone.now()
    community.suspended_until = None
    community.moderation_reason = reason.strip()
    community.save(update_fields=["blocked_at", "suspended_until", "moderation_reason"])

    log_audit_action(
        actor=actor,
        action=AuditAction.COMMUNITY_BLOCK,
        target_type="COMMUNITY",
        target_id=community.commname,
        reason=reason,
    )
    return community


@transaction.atomic
def unblock_community(
    *,
    actor: Any,
    community: Community,
    reason: str = "",
) -> Community:
    """Unblock a previously blocked community (staff only)."""
    if not actor.is_staff:
        raise DomainError(
            "Only staff administrators can unblock communities.",
            code="permission_denied",
            http_status=403,
        )

    community.blocked_at = None
    community.suspended_until = None
    community.moderation_reason = ""
    community.save(update_fields=["blocked_at", "suspended_until", "moderation_reason"])

    log_audit_action(
        actor=actor,
        action=AuditAction.COMMUNITY_UNBLOCK,
        target_type="COMMUNITY",
        target_id=community.commname,
        reason=reason,
    )
    return community


@transaction.atomic
def admin_delete_content(
    *,
    actor: Any,
    content_type: str,
    content_id: int,
    reason: str = "",
) -> None:
    """Delete offensive or illegal content by an administrator or moderator."""
    if not actor.is_staff:
        raise DomainError(
            "Only staff administrators can use global content moderation delete.",
            code="permission_denied",
            http_status=403,
        )

    if content_type == "BUBBLEGRAM":
        try:
            bubblegram = Bubblegram.objects.get(id=content_id)
        except Bubblegram.DoesNotExist:
            raise DomainError(
                "Bubblegram does not exist.",
                code="not_found",
                http_status=404,
            ) from None
        delete_bubblegram(actor=actor, bubblegram=bubblegram)

    elif content_type == "COMMENT":
        try:
            comment = Comment.objects.get(id=content_id)
        except Comment.DoesNotExist:
            raise DomainError(
                "Comment does not exist.",
                code="not_found",
                http_status=404,
            ) from None
        delete_comment(actor=actor, comment=comment)

    else:
        raise DomainError(
            f"Unknown content type: {content_type}",
            code="invalid_type",
            http_status=400,
        )

    log_audit_action(
        actor=actor,
        action=AuditAction.CONTENT_DELETE,
        target_type=content_type,
        target_id=content_id,
        reason=reason,
    )


@transaction.atomic
def admin_adjust_soap(
    *,
    actor: Any,
    wallet: Wallet,
    amount: int,
    reason: str = "",
) -> Any:
    """Manually credit or debit soap on a wallet with mandatory audit logging (RF018)."""
    if not actor.is_staff:
        raise DomainError(
            "Only staff administrators can adjust soap balances.",
            code="permission_denied",
            http_status=403,
        )
    if amount == 0:
        raise DomainError(
            "Adjustment amount must be a non-zero integer.",
            code="invalid_amount",
            http_status=400,
        )

    txs = apply_movements([(wallet, amount, ActionType.ADMIN_ADJUSTMENT)])
    tx = txs[0]

    target_desc = f"user:{wallet.user_id}" if wallet.user_id else f"comm:{wallet.community_id}"
    log_audit_action(
        actor=actor,
        action=AuditAction.ECONOMY_ADJUSTMENT,
        target_type="WALLET",
        target_id=wallet.id,
        reason=reason,
        metadata={
            "target": target_desc,
            "amount": amount,
            "balance_before": tx.balance_after - amount,
            "balance_after": tx.balance_after,
        },
    )
    return tx
