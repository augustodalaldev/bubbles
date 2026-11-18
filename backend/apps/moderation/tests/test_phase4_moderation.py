from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.tests.factories import DEFAULT_PASSWORD, UserFactory
from apps.communities.models import MemberRole
from apps.communities.tests.factories import CommunityFactory, CommunityMemberFactory
from apps.content.tests.factories import BubblegramFactory, CommentFactory
from apps.moderation.models import AuditAction, AuditLog

pytestmark = pytest.mark.django_db


def as_user(user):
    # A real request loads the user from the database; mirror that so status changes show up.
    user.refresh_from_db()
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def staff():
    return UserFactory(is_staff=True)


# ---- users ---------------------------------------------------------------------------------


def test_suspend_stores_reason_and_exposes_banner_data(staff):
    user = UserFactory()
    res = as_user(staff).post(
        f"/api/v1/admin/users/{user.pk}/suspend/",
        {"duration_hours": 48, "reason": "spam"},
        format="json",
    )
    assert res.status_code == 200
    me = as_user(user).get("/api/v1/users/me/").data
    assert me["is_suspended"] is True
    assert me["moderation_reason"] == "spam"
    assert me["suspended_until"]
    assert AuditLog.objects.filter(action=AuditAction.USER_SUSPEND, reason="spam").exists()


def test_suspended_user_can_read_but_not_post_comment_support_or_write_letters(staff):
    user = UserFactory()
    other = UserFactory()
    post = BubblegramFactory(user=other)
    as_user(staff).post(
        f"/api/v1/admin/users/{user.pk}/suspend/",
        {"duration_hours": 24, "reason": "x"},
        format="json",
    )
    client = as_user(user)
    assert client.get("/api/v1/feed/").status_code == 200
    assert client.get(f"/api/v1/bubblegrams/{post.pk}/").status_code == 200
    for res in (
        client.post("/api/v1/bubblegrams/", {"text": "oi", "type": "TEXT"}, format="json"),
        client.post(f"/api/v1/bubblegrams/{post.pk}/comments/", {"text": "oi"}, format="json"),
        client.post(f"/api/v1/bubblegrams/{post.pk}/support/"),
        client.post(
            "/api/v1/letters/", {"recipient_username": other.username, "text": "oi"}, format="json"
        ),
    ):
        assert res.status_code == 403, res.data
        assert res.data["error"]["code"] == "account_suspended"


def test_suspension_expires_by_itself(staff):
    user = UserFactory()
    user.status = "SUSPENDED"
    user.suspended_until = timezone.now() - timedelta(minutes=1)
    user.save()
    assert as_user(user).get("/api/v1/users/me/").data["is_suspended"] is False
    row = next(
        u for u in as_user(staff).get("/api/v1/admin/users/?q=" + user.username).data["results"]
    )
    assert row["status"] == "ACTIVE"


def test_restore_clears_status_and_reason(staff):
    user = UserFactory()
    client = as_user(staff)
    client.post(
        f"/api/v1/admin/users/{user.pk}/suspend/",
        {"duration_hours": 5, "reason": "a"},
        format="json",
    )
    res = client.post(f"/api/v1/admin/users/{user.pk}/unban/", {"reason": "ok"}, format="json")
    assert res.status_code == 200
    me = as_user(user).get("/api/v1/users/me/").data
    assert me["is_suspended"] is False and me["moderation_reason"] == ""


def test_banned_user_login_shows_reason_only_with_correct_password(staff):
    user = UserFactory()
    as_user(staff).post(f"/api/v1/admin/users/{user.pk}/ban/", {"reason": "assédio"}, format="json")
    anon = APIClient()
    ok = anon.post(
        "/api/v1/auth/login/",
        {"identifier": user.username, "password": DEFAULT_PASSWORD},
        format="json",
    )
    assert ok.status_code == 403
    assert ok.data["error"]["code"] == "account_banned"
    assert "assédio" in ok.data["error"]["message"]
    assert ok.data["error"]["message"].startswith("Esta conta foi banida")

    wrong = anon.post(
        "/api/v1/auth/login/", {"identifier": user.username, "password": "errada"}, format="json"
    )
    assert wrong.status_code == 401
    assert wrong.data["error"]["code"] == "invalid_credentials"
    assert "assédio" not in str(wrong.data)


def test_banned_user_content_and_profile_are_hidden(staff):
    banned = UserFactory()
    viewer = UserFactory()
    community = CommunityFactory()
    CommunityMemberFactory(community=community, user=viewer)
    CommunityMemberFactory(community=community, user=banned)
    personal = BubblegramFactory(user=banned)
    in_comm = BubblegramFactory(user=banned, community=community)
    other_post = BubblegramFactory(user=viewer)
    CommentFactory(bubblegram=other_post, user=banned, text="comentário do banido")
    as_user(staff).post(f"/api/v1/admin/users/{banned.pk}/ban/", {"reason": "r"}, format="json")

    client = as_user(viewer)
    assert client.get(f"/api/v1/users/{banned.username}/").status_code == 404
    assert client.get(f"/api/v1/bubblegrams/{personal.pk}/").status_code == 404
    assert client.get(f"/api/v1/bubblegrams/{in_comm.pk}/").status_code == 404
    posts = client.get(f"/api/v1/communities/{community.commname}/bubblegrams/").data["results"]
    assert in_comm.pk not in [p["id"] for p in posts]
    comments = client.get(f"/api/v1/bubblegrams/{other_post.pk}/comments/").data["results"]
    assert comments == []
    members = client.get(f"/api/v1/communities/{community.commname}/members/").data["results"]
    assert banned.username not in [m["user"]["username"] for m in members]
    assert client.get("/api/v1/search/?q=" + banned.username).data["users"] == []


def test_non_staff_cannot_moderate_and_staff_cannot_ban_staff_or_self(staff):
    user = UserFactory()
    other = UserFactory(is_staff=True)
    assert (
        as_user(user)
        .post(f"/api/v1/admin/users/{other.pk}/ban/", {"reason": "x"}, format="json")
        .status_code
        == 403
    )
    assert as_user(user).get("/api/v1/admin/users/").status_code == 403
    assert as_user(user).get("/api/v1/admin/communities/").status_code == 403
    for target in (other, staff):
        res = as_user(staff).post(
            f"/api/v1/admin/users/{target.pk}/ban/", {"reason": "x"}, format="json"
        )
        assert res.status_code == 400


def test_reason_is_required(staff):
    user = UserFactory()
    client = as_user(staff)
    assert client.post(f"/api/v1/admin/users/{user.pk}/ban/", {}, format="json").status_code == 400
    assert (
        client.post(f"/api/v1/admin/users/{user.pk}/suspend/", {}, format="json").status_code == 400
    )


def test_admin_user_list_filters_and_hides_deleted(staff):
    active = UserFactory(username="ana_ativa")
    banned = UserFactory(username="beto_banido", status="BANNED", is_active=False)
    susp = UserFactory(
        username="caio_susp", status="SUSPENDED", suspended_until=timezone.now() + timedelta(days=1)
    )
    gone = UserFactory(username="deleted_999", deleted_at=timezone.now(), is_active=False)
    client = as_user(staff)

    def names(qs):
        return {u["username"] for u in client.get("/api/v1/admin/users/" + qs).data["results"]}

    assert {"ana_ativa", "beto_banido", "caio_susp"} <= names("")
    assert gone.username not in names("")
    assert names("?status=BANNED") == {"beto_banido"}
    assert names("?status=SUSPENDED") == {"caio_susp"}
    assert "ana_ativa" in names("?status=ACTIVE") and "beto_banido" not in names("?status=ACTIVE")
    assert names("?q=beto") == {"beto_banido"}
    assert active.pk and susp.pk and banned.pk


# ---- communities ---------------------------------------------------------------------------


def make_comm(commname="comunidade_x"):
    community = CommunityFactory(commname=commname, name="Comunidade X")
    leader = UserFactory()
    member = UserFactory()
    CommunityMemberFactory(community=community, user=leader, role=MemberRole.LEADER)
    CommunityMemberFactory(community=community, user=member)
    return community, leader, member


def test_community_suspension_hides_it_and_makes_it_read_only(staff):
    community, leader, member = make_comm()
    outsider = UserFactory()
    post = BubblegramFactory(user=member, community=community)
    res = as_user(staff).post(
        f"/api/v1/admin/communities/{community.commname}/suspend/",
        {"duration_hours": 72, "reason": "regras"},
        format="json",
    )
    assert res.status_code == 200
    assert res.data["status"] == "SUSPENDED"
    assert AuditLog.objects.filter(action=AuditAction.COMMUNITY_SUSPEND).exists()

    # hidden from lists, search and outsiders
    for user in (outsider, member):
        names = [c["commname"] for c in as_user(user).get("/api/v1/communities/").data["results"]]
        assert community.commname not in names
        assert as_user(user).get("/api/v1/search/?q=comunidade").data["communities"] == []
    assert as_user(outsider).get(f"/api/v1/communities/{community.commname}/").status_code == 404
    assert (
        as_user(outsider).get(f"/api/v1/communities/{community.commname}/bubblegrams/").status_code
        == 404
    )
    # members and the leader still open the read-only page with the reason
    for user in (leader, member):
        detail = as_user(user).get(f"/api/v1/communities/{community.commname}/")
        assert detail.status_code == 200
        assert detail.data["moderation"]["status"] == "SUSPENDED"
        assert detail.data["moderation"]["reason"] == "regras"
        assert detail.data["moderation"]["suspended_until"]
        assert detail.data["permissions"]["can_edit"] is False
        assert detail.data["permissions"]["can_leave"] is False
    # read-only: cannot post or support
    res = as_user(member).post(
        "/api/v1/bubblegrams/",
        {"text": "oi", "type": "TEXT", "commname": community.commname},
        format="json",
    )
    assert res.status_code == 403 and res.data["error"]["code"] == "community_blocked"
    assert (
        as_user(leader)
        .patch(f"/api/v1/communities/{community.commname}/", {"name": "novo"}, format="json")
        .status_code
        == 403
    )
    assert post.pk
    # the feed leaves its posts out
    feed = as_user(member).get("/api/v1/feed/").data["results"]
    assert post.pk not in [p["id"] for p in feed]


def test_suspension_expiry_makes_community_visible_again(staff):
    community, _, member = make_comm()
    community.suspended_until = timezone.now() - timedelta(minutes=1)
    community.moderation_reason = "velho"
    community.save()
    names = [c["commname"] for c in as_user(member).get("/api/v1/communities/").data["results"]]
    assert community.commname in names
    detail = as_user(member).get(f"/api/v1/communities/{community.commname}/").data
    assert detail["moderation"] is None


def test_community_ban_and_restore(staff):
    community, leader, _ = make_comm()
    client = as_user(staff)
    res = client.post(
        f"/api/v1/admin/communities/{community.commname}/block/",
        {"reason": "ilegal"},
        format="json",
    )
    assert res.status_code == 200
    assert as_user(leader).get(f"/api/v1/communities/{community.commname}/").data["moderation"] == {
        "status": "BANNED",
        "reason": "ilegal",
        "suspended_until": None,
    }
    # a suspended community cannot be "re-suspended" over a ban
    res = client.post(
        f"/api/v1/admin/communities/{community.commname}/suspend/",
        {"duration_hours": 1, "reason": "x"},
        format="json",
    )
    assert res.status_code == 400 and res.data["error"]["code"] == "already_banned"
    res = client.post(
        f"/api/v1/admin/communities/{community.commname}/unblock/", {"reason": "ok"}, format="json"
    )
    assert res.status_code == 200
    detail = as_user(leader).get(f"/api/v1/communities/{community.commname}/").data
    assert detail["moderation"] is None


def test_restore_also_lifts_a_suspension(staff):
    community, leader, _ = make_comm()
    client = as_user(staff)
    client.post(
        f"/api/v1/admin/communities/{community.commname}/suspend/",
        {"duration_hours": 10, "reason": "x"},
        format="json",
    )
    client.post(
        f"/api/v1/admin/communities/{community.commname}/unblock/", {"reason": "ok"}, format="json"
    )
    community.refresh_from_db()
    assert community.suspended_until is None and community.moderation_reason == ""


def test_admin_community_list_filters(staff):
    ok, _, _ = make_comm("saudavel_a")
    susp = CommunityFactory(
        commname="suspensa_b", suspended_until=timezone.now() + timedelta(days=1)
    )
    banned = CommunityFactory(commname="banida_c", blocked_at=timezone.now())
    gone = CommunityFactory(commname="deleted_77", deleted_at=timezone.now())
    client = as_user(staff)

    def names(qs):
        return {
            c["commname"] for c in client.get("/api/v1/admin/communities/" + qs).data["results"]
        }

    assert {"saudavel_a", "suspensa_b", "banida_c"} <= names("")
    assert gone.commname not in names("")
    assert names("?status=SUSPENDED") == {"suspensa_b"}
    assert names("?status=BANNED") == {"banida_c"}
    assert "saudavel_a" in names("?status=ACTIVE")
    assert names("?q=banida") == {"banida_c"}
    assert ok.pk and susp.pk and banned.pk


def test_leader_cannot_delete_a_suspended_community(staff):
    community, leader, _ = make_comm()
    as_user(staff).post(
        f"/api/v1/admin/communities/{community.commname}/suspend/",
        {"duration_hours": 5, "reason": "x"},
        format="json",
    )
    res = as_user(leader).delete(
        f"/api/v1/communities/{community.commname}/",
        {"confirm_commname": community.commname},
        format="json",
    )
    assert res.status_code == 403
