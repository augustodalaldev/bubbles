import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.tests.factories import UserFactory
from apps.communities.models import MemberRole, MemberState
from apps.communities.tests.factories import CommunityFactory, CommunityMemberFactory
from apps.economy.models import Wallet

pytestmark = pytest.mark.django_db


@pytest.fixture
def community_roles():
    community = CommunityFactory()
    Wallet.objects.create(community=community, soap_balance=500)

    leader = UserFactory()
    CommunityMemberFactory(community=community, user=leader, role=MemberRole.LEADER)

    admin = UserFactory()
    CommunityMemberFactory(community=community, user=admin, role=MemberRole.COMM_ADMIN)

    regular_member = UserFactory()
    CommunityMemberFactory(community=community, user=regular_member, role=MemberRole.MEMBER)

    silenced_member = UserFactory()
    CommunityMemberFactory(
        community=community,
        user=silenced_member,
        role=MemberRole.MEMBER,
        current_state=MemberState.SILENCED,
    )

    banned_member = UserFactory()
    CommunityMemberFactory(
        community=community,
        user=banned_member,
        role=MemberRole.MEMBER,
        current_state=MemberState.BANNED,
    )

    non_member = UserFactory()
    staff_user = UserFactory(is_staff=True)

    return {
        "community": community,
        "leader": leader,
        "admin": admin,
        "regular_member": regular_member,
        "silenced_member": silenced_member,
        "banned_member": banned_member,
        "non_member": non_member,
        "staff": staff_user,
    }


def make_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_permission_edit_community_matrix(community_roles):
    commname = community_roles["community"].commname
    url = f"/api/v1/communities/{commname}/"
    payload = {"description": "Updated description"}

    # Disallowed roles
    for role in ["non_member", "banned_member", "silenced_member", "regular_member"]:
        res = make_client(community_roles[role]).patch(url, data=payload, format="json")
        assert res.status_code == status.HTTP_403_FORBIDDEN, f"Failed for role {role}"

    # Allowed roles
    for role in ["admin", "leader", "staff"]:
        res = make_client(community_roles[role]).patch(url, data=payload, format="json")
        assert res.status_code == status.HTTP_200_OK, f"Failed for role {role}"


def test_permission_edit_guidelines_matrix(community_roles):
    commname = community_roles["community"].commname
    url = f"/api/v1/communities/{commname}/guidelines/"
    payload = {"guidelines": "New guidelines"}

    # Disallowed roles (admins cannot edit guidelines, only leader/staff)
    for role in [
        "non_member",
        "banned_member",
        "silenced_member",
        "regular_member",
        "admin",
    ]:
        res = make_client(community_roles[role]).patch(url, data=payload, format="json")
        assert res.status_code == status.HTTP_403_FORBIDDEN, f"Failed for role {role}"

    # Allowed roles
    for role in ["leader", "staff"]:
        res = make_client(community_roles[role]).patch(url, data=payload, format="json")
        assert res.status_code == status.HTTP_200_OK, f"Failed for role {role}"


def test_permission_archive_matrix(community_roles):
    comm = community_roles["community"]
    url = f"/api/v1/communities/{comm.commname}/archive/"

    # Disallowed roles
    for role in [
        "non_member",
        "banned_member",
        "silenced_member",
        "regular_member",
        "admin",
    ]:
        res = make_client(community_roles[role]).post(url)
        assert res.status_code == status.HTTP_403_FORBIDDEN, f"Failed for role {role}"

    # Leader can archive
    res = make_client(community_roles["leader"]).post(url)
    assert res.status_code == status.HTTP_200_OK


def test_permission_view_wallet_matrix(community_roles):
    commname = community_roles["community"].commname
    url = f"/api/v1/communities/{commname}/wallet/"

    # Disallowed roles
    for role in ["non_member", "banned_member", "silenced_member", "regular_member"]:
        res = make_client(community_roles[role]).get(url)
        assert res.status_code == status.HTTP_403_FORBIDDEN, f"Failed for role {role}"

    # Allowed roles
    for role in ["admin", "leader", "staff"]:
        res = make_client(community_roles[role]).get(url)
        assert res.status_code == status.HTTP_200_OK, f"Failed for role {role}"
        assert res.data["soap_balance"] == 500
