import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.tests.factories import UserFactory
from apps.communities.models import CommunityMember, MemberRole, MemberState
from apps.communities.tests.factories import CommunityFactory, CommunityMemberFactory
from apps.economy.models import Wallet

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_list_communities_search_and_mine(django_assert_num_queries):
    user = UserFactory()
    client = auth_client(user)

    comm1 = CommunityFactory(commname="astronomy_hub", name="Stargazers")
    CommunityFactory(commname="baking_hub", name="Bread Lovers")
    comm3 = CommunityFactory(commname="coding_hub", name="Python Devs")

    CommunityMemberFactory(community=comm1, user=user)
    CommunityMemberFactory(community=comm3, user=user)

    # Search filter
    res_search = client.get("/api/v1/communities/?search=bread")
    assert res_search.status_code == status.HTTP_200_OK
    assert res_search.data["count"] == 1
    assert res_search.data["results"][0]["commname"] == "baking_hub"

    # Mine filter
    res_mine = client.get("/api/v1/communities/?mine=true")
    assert res_mine.status_code == status.HTTP_200_OK
    assert res_mine.data["count"] == 2
    comms = {c["commname"] for c in res_mine.data["results"]}
    assert comms == {"astronomy_hub", "coding_hub"}

    # Query count check (prevent N+1 on list)
    with django_assert_num_queries(2):  # 1 count query + 1 page query
        res_all = client.get("/api/v1/communities/")
        assert res_all.status_code == status.HTTP_200_OK
        assert res_all.data["count"] == 3


def test_create_community_api_success():
    user = UserFactory()
    Wallet.objects.create(user=user, soap_balance=500)
    client = auth_client(user)

    payload = {
        "commname": "cozy_bubble",
        "name": "Cozy Bubble",
        "description": "A very cozy place.",
        "guidelines": "Keep it calm and kind.",
    }
    response = client.post("/api/v1/communities/", data=payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["commname"] == "cozy_bubble"
    assert response.data["member_count"] == 1
    assert response.data["my_membership"]["role"] == MemberRole.LEADER
    assert response.data["permissions"]["can_edit"] is True
    assert response.data["permissions"]["can_archive"] is True


def test_create_community_api_insufficient_soap():
    user = UserFactory()
    Wallet.objects.create(user=user, soap_balance=50)  # founding cost is 300
    client = auth_client(user)

    payload = {
        "commname": "too_expensive",
        "name": "Too Expensive",
    }
    response = client.post("/api/v1/communities/", data=payload, format="json")
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.data["error"]["code"] == "insufficient_soap"


def test_community_detail_api():
    community = CommunityFactory(commname="detail_test")
    leader = UserFactory()
    CommunityMemberFactory(community=community, user=leader, role=MemberRole.LEADER)
    client = auth_client(leader)

    response = client.get(f"/api/v1/communities/{community.commname}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["commname"] == "detail_test"
    assert response.data["my_membership"]["role"] == MemberRole.LEADER
    assert response.data["permissions"]["can_edit"] is True
    assert response.data["permissions"]["can_edit_guidelines"] is True
    assert response.data["permissions"]["can_transfer_leadership"] is True


def test_community_members_list_api(django_assert_num_queries):
    community = CommunityFactory()
    users = [UserFactory() for _ in range(5)]
    for u in users:
        CommunityMemberFactory(community=community, user=u)

    users[0].last_seen_at = timezone.now()
    users[0].save(update_fields=["last_seen_at"])
    client = auth_client(users[0])

    # Ensure select_related on user prevents N+1 queries:
    # 1 to lookup community, 1 count query for pagination, 1 query with user joined
    with django_assert_num_queries(3):
        res = client.get(f"/api/v1/communities/{community.commname}/members/")
        assert res.status_code == status.HTTP_200_OK
        assert res.data["count"] == 5
        assert len(res.data["results"]) == 5
        assert "user" in res.data["results"][0]
        assert "username" in res.data["results"][0]["user"]


def test_community_join_and_leave_api():
    community = CommunityFactory(member_count=1)
    user = UserFactory()
    client = auth_client(user)

    # Join
    res_join = client.post(f"/api/v1/communities/{community.commname}/join/")
    assert res_join.status_code == status.HTTP_201_CREATED
    assert res_join.data["role"] == MemberRole.MEMBER
    community.refresh_from_db()
    assert community.member_count == 2

    # Leave
    res_leave = client.post(f"/api/v1/communities/{community.commname}/leave/")
    assert res_leave.status_code == status.HTTP_200_OK
    community.refresh_from_db()
    assert community.member_count == 1


def test_community_moderate_member_api():
    community = CommunityFactory(member_count=2)
    leader = UserFactory()
    member = UserFactory()
    CommunityMemberFactory(community=community, user=leader, role=MemberRole.LEADER)
    CommunityMemberFactory(community=community, user=member, role=MemberRole.MEMBER)

    client = auth_client(leader)
    url = f"/api/v1/communities/{community.commname}/members/{member.username}/"

    # Silence
    res_silence = client.patch(url, data={"current_state": MemberState.SILENCED}, format="json")
    assert res_silence.status_code == status.HTTP_200_OK
    assert res_silence.data["current_state"] == MemberState.SILENCED

    # Ban
    res_ban = client.patch(url, data={"current_state": MemberState.BANNED}, format="json")
    assert res_ban.status_code == status.HTTP_200_OK
    assert res_ban.data["current_state"] == MemberState.BANNED


def test_community_promote_and_demote_api():
    community = CommunityFactory()
    leader = UserFactory()
    member = UserFactory()
    CommunityMemberFactory(community=community, user=leader, role=MemberRole.LEADER)
    CommunityMemberFactory(
        community=community, user=member, role=MemberRole.MEMBER, current_state=MemberState.ACTIVE
    )

    client = auth_client(leader)

    # Promote
    res_promote = client.post(
        f"/api/v1/communities/{community.commname}/members/{member.username}/promote/"
    )
    assert res_promote.status_code == status.HTTP_200_OK
    assert res_promote.data["role"] == MemberRole.COMM_ADMIN

    # Demote
    res_demote = client.post(
        f"/api/v1/communities/{community.commname}/members/{member.username}/demote/"
    )
    assert res_demote.status_code == status.HTTP_200_OK
    assert res_demote.data["role"] == MemberRole.MEMBER


def test_community_transfer_leadership_api():
    community = CommunityFactory()
    leader = UserFactory()
    member = UserFactory()
    CommunityMemberFactory(community=community, user=leader, role=MemberRole.LEADER)
    CommunityMemberFactory(
        community=community, user=member, role=MemberRole.MEMBER, current_state=MemberState.ACTIVE
    )

    client = auth_client(leader)
    res = client.post(
        f"/api/v1/communities/{community.commname}/transfer-leadership/",
        data={"new_leader_username": member.username},
        format="json",
    )
    assert res.status_code == status.HTTP_200_OK
    assert res.data["role"] == MemberRole.LEADER

    assert CommunityMember.objects.filter(
        community=community, user=leader, role=MemberRole.COMM_ADMIN
    ).exists()


def test_community_archive_api():
    community = CommunityFactory()
    leader = UserFactory()
    CommunityMemberFactory(community=community, user=leader, role=MemberRole.LEADER)

    client = auth_client(leader)
    res = client.post(f"/api/v1/communities/{community.commname}/archive/")
    assert res.status_code == status.HTTP_200_OK
    assert res.data["is_archived"] is True
    assert res.data["archived_at"] is not None


def test_community_wallet_api():
    community = CommunityFactory()
    leader = UserFactory()
    CommunityMemberFactory(community=community, user=leader, role=MemberRole.LEADER)
    Wallet.objects.create(community=community, soap_balance=350)

    client = auth_client(leader)
    res = client.get(f"/api/v1/communities/{community.commname}/wallet/")
    assert res.status_code == status.HTTP_200_OK
    assert res.data["soap_balance"] == 350


def test_community_blocked_listing_and_permissions():
    active_comm = CommunityFactory(name="Active Comm")
    blocked_comm = CommunityFactory(name="Blocked Comm", blocked_at=timezone.now())

    user = UserFactory()
    client = auth_client(user)

    # Regular user does not see blocked community in list
    res = client.get("/api/v1/communities/")
    assert res.status_code == status.HTTP_200_OK
    comm_names = [c["commname"] for c in res.data["results"]]
    assert active_comm.commname in comm_names
    assert blocked_comm.commname not in comm_names

    # Permissions on blocked community disallow join
    res_detail = client.get(f"/api/v1/communities/{blocked_comm.commname}/")
    assert res_detail.status_code == status.HTTP_200_OK
    assert res_detail.data["permissions"]["can_join"] is False
    assert res_detail.data["permissions"]["can_edit"] is False


def test_members_list_returns_absolute_profile_photo_urls():
    from apps.accounts.models import User

    viewer = UserFactory()
    member = UserFactory()
    User.objects.filter(pk=member.pk).update(profile_photo="profile_photos/m.png")
    community = CommunityFactory()
    CommunityMemberFactory(community=community, user=member)

    res = auth_client(viewer).get(f"/api/v1/communities/{community.commname}/members/")
    assert res.status_code == status.HTTP_200_OK
    assert res.data["results"][0]["user"]["profile_photo"].startswith("http://testserver/media/")
