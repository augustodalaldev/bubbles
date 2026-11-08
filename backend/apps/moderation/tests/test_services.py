import pytest
from django.utils import timezone

from apps.accounts.models import UserStatus
from apps.accounts.tests.factories import UserFactory
from apps.communities.models import MemberRole, MemberState
from apps.communities.services import join_community
from apps.communities.tests.factories import CommunityFactory, CommunityMemberFactory
from apps.content.models import Bubblegram, BubblegramType, Comment
from apps.content.services import create_bubblegram, create_comment, support_bubblegram
from apps.content.tests.factories import BubblegramFactory, CommentFactory
from apps.core.exceptions import DomainError
from apps.economy.models import ActionType, Wallet
from apps.moderation.models import (
    AuditAction,
    AuditLog,
    ReportReason,
    ReportStatus,
    ReportTargetType,
)
from apps.moderation.services import (
    admin_adjust_soap,
    admin_delete_content,
    ban_user,
    block_community,
    file_report,
    review_report,
    suspend_user,
    unban_user,
    unblock_community,
)
from apps.social.services import send_letter

pytestmark = pytest.mark.django_db


def test_file_report_valid_and_invalid():
    reporter = UserFactory()
    target_user = UserFactory()

    # Self-report fails
    with pytest.raises(DomainError) as exc:
        file_report(
            reporter=reporter,
            target_type=ReportTargetType.USER,
            target_id=reporter.id,
            reason=ReportReason.HARASSMENT,
        )
    assert exc.value.code == "self_report"

    # Valid report against user
    report = file_report(
        reporter=reporter,
        target_type=ReportTargetType.USER,
        target_id=target_user.id,
        reason=ReportReason.HARASSMENT,
        description="Repeated rude messages",
    )
    assert report.id is not None
    assert report.status == ReportStatus.PENDING
    assert report.target_id == str(target_user.id)


def test_review_report_success_and_permissions():
    staff = UserFactory(is_staff=True)
    regular = UserFactory(is_staff=False)
    reporter = UserFactory()
    target_user = UserFactory()

    report = file_report(
        reporter=reporter,
        target_type=ReportTargetType.USER,
        target_id=target_user.id,
        reason=ReportReason.SPAM,
    )

    # Non-staff cannot review
    with pytest.raises(DomainError) as exc:
        review_report(reviewer=regular, report=report, status=ReportStatus.RESOLVED)
    assert exc.value.code == "permission_denied"

    # Staff reviews successfully
    reviewed = review_report(
        reviewer=staff,
        report=report,
        status=ReportStatus.RESOLVED,
        resolution_notes="Action taken against spammer",
    )
    assert reviewed.status == ReportStatus.RESOLVED
    assert reviewed.reviewed_by == staff
    assert reviewed.resolution_notes == "Action taken against spammer"

    # Audit log entry created
    audit = AuditLog.objects.filter(action=AuditAction.REPORT_RESOLVE, target_id=report.id).first()
    assert audit is not None
    assert audit.actor == staff


def test_suspend_and_unban_user():
    staff = UserFactory(is_staff=True)
    user = UserFactory()

    # Suspend user for 48 hours
    suspended = suspend_user(actor=staff, user=user, duration_hours=48, reason="Toxic behavior")
    assert suspended.status == UserStatus.SUSPENDED
    assert suspended.is_suspended is True
    assert suspended.suspended_until > timezone.now()

    # Verify suspended user cannot post bubblegrams
    with pytest.raises(DomainError) as exc:
        create_bubblegram(author=suspended, text="Hello world", type=BubblegramType.TEXT)
    assert exc.value.code == "account_suspended"

    # Verify suspended user cannot comment
    bg = BubblegramFactory()
    with pytest.raises(DomainError) as exc:
        create_comment(author=suspended, bubblegram=bg, text="My comment")
    assert exc.value.code == "account_suspended"

    # Verify suspended user cannot support
    with pytest.raises(DomainError) as exc:
        support_bubblegram(donor=suspended, bubblegram=bg)
    assert exc.value.code == "account_suspended"

    # Verify suspended user cannot send letters
    with pytest.raises(DomainError) as exc:
        send_letter(sender=suspended, recipient=staff, text="Help")
    assert exc.value.code == "account_suspended"

    # Unban / restore user
    restored = unban_user(actor=staff, user=suspended, reason="Appeal approved")
    assert restored.status == UserStatus.ACTIVE
    assert restored.is_suspended is False


def test_ban_user_deactivates():
    staff = UserFactory(is_staff=True)
    user = UserFactory()

    banned = ban_user(actor=staff, user=user, reason="Severe violations")
    assert banned.status == UserStatus.BANNED
    assert banned.is_active is False
    assert banned.is_banned is True


def test_block_and_unblock_community():
    staff = UserFactory(is_staff=True)
    community = CommunityFactory()
    user = UserFactory()

    blocked = block_community(actor=staff, community=community, reason="Illegal content")
    assert blocked.is_blocked is True
    assert blocked.blocked_at is not None

    # Cannot join blocked community
    with pytest.raises(DomainError) as exc:
        join_community(user=user, community=blocked)
    assert exc.value.code == "community_blocked"

    # Member cannot publish in blocked community
    CommunityMemberFactory(
        community=blocked,
        user=user,
        role=MemberRole.MEMBER,
        current_state=MemberState.ACTIVE,
    )
    with pytest.raises(DomainError) as exc:
        create_bubblegram(author=user, community=blocked, text="Hi", type=BubblegramType.TEXT)
    assert exc.value.code == "community_blocked"

    # Unblock
    unblocked = unblock_community(actor=staff, community=blocked, reason="Reviewed and cleared")
    assert unblocked.is_blocked is False
    assert unblocked.blocked_at is None


def test_admin_delete_content():
    staff = UserFactory(is_staff=True)
    bg = BubblegramFactory()
    comment = CommentFactory(bubblegram=bg)

    # Delete comment
    admin_delete_content(actor=staff, content_type="COMMENT", content_id=comment.id, reason="Spam")
    assert not Comment.objects.filter(id=comment.id).exists()

    # Delete bubblegram
    admin_delete_content(
        actor=staff,
        content_type="BUBBLEGRAM",
        content_id=bg.id,
        reason="Inappropriate",
    )
    assert not Bubblegram.objects.filter(id=bg.id).exists()

    # Admin adjust soap
    wallet = Wallet.objects.create(user=staff, soap_balance=50)

    # Credit +25
    tx_credit = admin_adjust_soap(actor=staff, wallet=wallet, amount=25, reason="Compensation")
    wallet.refresh_from_db()
    assert tx_credit.action_type == ActionType.ADMIN_ADJUSTMENT
    assert tx_credit.amount == 25
    assert wallet.soap_balance == 75

    # Debit -30
    tx_debit = admin_adjust_soap(
        actor=staff,
        wallet=wallet,
        amount=-30,
        reason="Chargeback correction",
    )
    wallet.refresh_from_db()
    assert tx_debit.action_type == ActionType.ADMIN_ADJUSTMENT
    assert tx_debit.amount == -30
    assert wallet.soap_balance == 45
