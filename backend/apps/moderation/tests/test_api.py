import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.tests.factories import UserFactory
from apps.communities.tests.factories import CommunityFactory
from apps.economy.models import Wallet
from apps.moderation.models import ReportReason, ReportStatus, ReportTargetType
from apps.moderation.tests.factories import ReportFactory

pytestmark = pytest.mark.django_db


def test_file_report_api():
    reporter = UserFactory()
    target_user = UserFactory()
    client = APIClient()

    # Unauthenticated
    payload = {
        "target_type": ReportTargetType.USER,
        "target_id": str(target_user.id),
        "reason": ReportReason.HARASSMENT,
        "description": "Harassing in comments",
    }
    assert client.post("/api/v1/reports/", payload).status_code == status.HTTP_401_UNAUTHORIZED

    # Authenticated
    client.force_authenticate(user=reporter)
    res = client.post("/api/v1/reports/", payload)
    assert res.status_code == status.HTTP_201_CREATED
    assert res.data["target_id"] == str(target_user.id)
    assert res.data["status"] == ReportStatus.PENDING


def test_admin_reports_list_and_review_api():
    staff = UserFactory(is_staff=True)
    regular = UserFactory(is_staff=False)
    report = ReportFactory(status=ReportStatus.PENDING)

    client = APIClient()
    client.force_authenticate(user=regular)

    # Regular user cannot access admin reports
    assert client.get("/api/v1/admin/reports/").status_code == status.HTTP_403_FORBIDDEN

    # Staff user can list
    client.force_authenticate(user=staff)
    res_list = client.get("/api/v1/admin/reports/")
    assert res_list.status_code == status.HTTP_200_OK
    assert res_list.data["count"] == 1

    # Staff user can review report
    patch_payload = {
        "status": ReportStatus.RESOLVED,
        "resolution_notes": "Handled by moderation",
    }
    res_patch = client.patch(f"/api/v1/admin/reports/{report.id}/", patch_payload)
    assert res_patch.status_code == status.HTTP_200_OK
    assert res_patch.data["status"] == ReportStatus.RESOLVED
    assert res_patch.data["resolution_notes"] == "Handled by moderation"


def test_admin_user_suspend_ban_unban_api():
    staff = UserFactory(is_staff=True)
    target_user = UserFactory()
    client = APIClient()
    client.force_authenticate(user=staff)

    # Suspend
    res_suspend = client.post(
        f"/api/v1/admin/users/{target_user.id}/suspend/",
        {"duration_hours": 72, "reason": "Rule violation"},
    )
    assert res_suspend.status_code == status.HTTP_200_OK
    assert res_suspend.data["user_status"] == "SUSPENDED"

    # Ban
    res_ban = client.post(
        f"/api/v1/admin/users/{target_user.id}/ban/",
        {"reason": "Permanent violation"},
    )
    assert res_ban.status_code == status.HTTP_200_OK
    assert res_ban.data["user_status"] == "BANNED"

    # Unban
    res_unban = client.post(
        f"/api/v1/admin/users/{target_user.id}/unban/",
        {"reason": "Pardon granted"},
    )
    assert res_unban.status_code == status.HTTP_200_OK
    assert res_unban.data["user_status"] == "ACTIVE"


def test_admin_community_block_unblock_api():
    staff = UserFactory(is_staff=True)
    community = CommunityFactory()
    client = APIClient()
    client.force_authenticate(user=staff)

    # Block
    res_block = client.post(
        f"/api/v1/admin/communities/{community.commname}/block/",
        {"reason": "TOS violation"},
    )
    assert res_block.status_code == status.HTTP_200_OK
    assert res_block.data["blocked_at"] is not None

    # Unblock
    res_unblock = client.post(
        f"/api/v1/admin/communities/{community.commname}/unblock/",
        {"reason": "Fixed issues"},
    )
    assert res_unblock.status_code == status.HTTP_200_OK
    assert res_unblock.data["blocked_at"] is None


def test_admin_soap_adjustment_and_audit_log_api():
    staff = UserFactory(is_staff=True)
    user = UserFactory()
    wallet = Wallet.objects.create(user=user, soap_balance=10)

    client = APIClient()
    client.force_authenticate(user=staff)

    # Adjust soap
    res_adj = client.post(
        f"/api/v1/admin/wallets/{wallet.id}/adjust/",
        {"amount": 50, "reason": "Contest winner bonus"},
    )
    assert res_adj.status_code == status.HTTP_200_OK
    assert res_adj.data["balance_after"] == 60

    # Read audit logs
    res_audit = client.get("/api/v1/admin/audit-logs/")
    assert res_audit.status_code == status.HTTP_200_OK
    assert res_audit.data["count"] >= 1
    assert res_audit.data["results"][0]["action"] == "ECONOMY_ADJUSTMENT"


def test_report_with_non_numeric_target_id_is_a_400_not_a_500():
    client = APIClient()
    client.force_authenticate(user=UserFactory())
    payload = {
        "target_type": ReportTargetType.BUBBLEGRAM,
        "target_id": "abc",
        "reason": ReportReason.SPAM,
    }
    res = client.post("/api/v1/reports/", payload)
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert res.data["error"]["code"] == "invalid_target_id"


def test_report_on_community_still_uses_commname():
    community = CommunityFactory(commname="some_comm")
    client = APIClient()
    client.force_authenticate(user=UserFactory())
    payload = {
        "target_type": ReportTargetType.COMMUNITY,
        "target_id": "some_comm",
        "reason": ReportReason.SPAM,
    }
    assert community.commname == "some_comm"
    assert client.post("/api/v1/reports/", payload).status_code == status.HTTP_201_CREATED


def test_admin_delete_content_with_non_numeric_id_is_a_400():
    client = APIClient()
    client.force_authenticate(user=UserFactory(is_staff=True))
    res = client.post(
        "/api/v1/admin/content/delete/?type=bubblegram&id=abc", {"reason": "x"}, format="json"
    )
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert res.data["error"]["code"] == "invalid_content_id"


def test_investigating_report_does_not_write_a_dismiss_audit_entry():
    from apps.moderation.models import AuditLog

    staff = UserFactory(is_staff=True)
    report = ReportFactory(status=ReportStatus.PENDING)
    client = APIClient()
    client.force_authenticate(user=staff)
    res = client.patch(
        f"/api/v1/admin/reports/{report.id}/", {"status": ReportStatus.INVESTIGATING}
    )
    assert res.status_code == status.HTTP_200_OK
    assert res.data["status"] == ReportStatus.INVESTIGATING
    assert not AuditLog.objects.exists()


def test_report_json_keeps_reviewed_by_username_key_as_null_when_unreviewed():
    staff = UserFactory(is_staff=True)
    ReportFactory(status=ReportStatus.PENDING)
    client = APIClient()
    client.force_authenticate(user=staff)
    res = client.get("/api/v1/admin/reports/")
    assert res.status_code == status.HTTP_200_OK
    assert "reviewed_by_username" in res.data["results"][0]
    assert res.data["results"][0]["reviewed_by_username"] is None


def test_soap_adjustment_audit_records_balance_before_and_after():
    from apps.moderation.models import AuditLog

    staff = UserFactory(is_staff=True)
    target = UserFactory()
    wallet = Wallet.objects.create(user=target, soap_balance=15)
    client = APIClient()
    client.force_authenticate(user=staff)
    res = client.post(
        f"/api/v1/admin/wallets/{wallet.id}/adjust/", {"amount": 5, "reason": "gift"}, format="json"
    )
    assert res.status_code == status.HTTP_200_OK
    metadata = AuditLog.objects.get().metadata
    assert metadata["balance_before"] == 15
    assert metadata["balance_after"] == 20


def test_audit_log_actor_username_is_null_not_missing():
    from apps.moderation.tests.factories import AuditLogFactory

    AuditLogFactory(actor=None)
    client = APIClient()
    client.force_authenticate(user=UserFactory(is_staff=True))
    res = client.get("/api/v1/admin/audit-logs/")
    assert res.data["results"][0]["actor_username"] is None
