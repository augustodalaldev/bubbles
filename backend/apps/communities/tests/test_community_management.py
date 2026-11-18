import pytest
from rest_framework.test import APIClient

from apps.accounts.tests.factories import UserFactory
from apps.communities.models import Community, CommunityMember, MemberRole
from apps.communities.tests.factories import CommunityFactory, CommunityMemberFactory
from apps.content.tests.factories import BubblegramFactory
from apps.economy.models import Wallet

pytestmark = pytest.mark.django_db


def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def make_community(commname="meu_cantinho"):
    leader = UserFactory()
    community = CommunityFactory(commname=commname, name="Meu Cantinho", member_count=3)
    CommunityMemberFactory(community=community, user=leader, role=MemberRole.LEADER)
    member = UserFactory()
    CommunityMemberFactory(community=community, user=member, role=MemberRole.MEMBER)
    return community, leader, member


def test_leader_deletes_community_and_everything_hides():
    community, leader, member = make_community()
    Wallet.objects.create(community=community, soap_balance=40)
    post = BubblegramFactory(user=member, community=community)

    res = auth_client(leader).delete(
        "/api/v1/communities/meu_cantinho/", {"confirm_commname": "Meu_Cantinho"}, format="json"
    )
    assert res.status_code == 204

    community.refresh_from_db()
    assert community.deleted_at is not None
    assert community.commname == f"deleted_{community.pk}"
    assert community.name == "Comunidade excluída"
    assert community.member_count == 0
    assert not CommunityMember.objects.filter(community=community).exists()
    # Row and wallet stay (append-only history); the soap is simply unreachable.
    assert Wallet.objects.get(community=community).soap_balance == 40

    client = auth_client(member)
    assert client.get("/api/v1/communities/meu_cantinho/").status_code == 404
    assert client.get(f"/api/v1/communities/{community.commname}/").status_code == 404
    assert client.get(f"/api/v1/bubblegrams/{post.pk}/").status_code == 404
    listing = client.get("/api/v1/communities/")
    assert all(c["commname"] != community.commname for c in listing.data["results"])
    search = client.get("/api/v1/search/?q=cantinho")
    assert search.data["communities"] == []
    assert client.get("/api/v1/feed/").status_code == 200


def test_handle_is_free_after_delete():
    community, leader, _ = make_community()
    res = auth_client(leader).delete(
        "/api/v1/communities/meu_cantinho/", {"confirm_commname": "meu_cantinho"}, format="json"
    )
    assert res.status_code == 204
    assert not Community.objects.filter(commname="meu_cantinho").exists()
    CommunityFactory(commname="meu_cantinho")


def test_delete_requires_matching_name():
    community, leader, _ = make_community()
    res = auth_client(leader).delete(
        "/api/v1/communities/meu_cantinho/", {"confirm_commname": "outro"}, format="json"
    )
    assert res.status_code == 400
    assert res.data["error"]["code"] == "confirmation_mismatch"
    assert "confirm_commname" in res.data["error"]["fields"]
    community.refresh_from_db()
    assert community.deleted_at is None


def test_delete_requires_confirmation_field():
    _, leader, _ = make_community()
    res = auth_client(leader).delete("/api/v1/communities/meu_cantinho/", {}, format="json")
    assert res.status_code == 400


def test_only_leader_can_delete():
    community, leader, member = make_community()
    admin = UserFactory()
    CommunityMemberFactory(community=community, user=admin, role=MemberRole.COMM_ADMIN)
    outsider = UserFactory()
    staff = UserFactory(is_staff=True)
    for user in (member, admin, outsider, staff):
        res = auth_client(user).delete(
            "/api/v1/communities/meu_cantinho/",
            {"confirm_commname": "meu_cantinho"},
            format="json",
        )
        assert res.status_code == 403, user
    community.refresh_from_db()
    assert community.deleted_at is None


def test_blocked_community_cannot_be_deleted_by_leader():
    from django.utils import timezone

    community, leader, _ = make_community()
    community.blocked_at = timezone.now()
    community.save()
    res = auth_client(leader).delete(
        "/api/v1/communities/meu_cantinho/", {"confirm_commname": "meu_cantinho"}, format="json"
    )
    assert res.status_code in (400, 403)
    community.refresh_from_db()
    assert community.deleted_at is None


def test_can_delete_permission_flag():
    community, leader, member = make_community()
    assert (
        auth_client(leader)
        .get("/api/v1/communities/meu_cantinho/")
        .data["permissions"]["can_delete"]
    )
    assert (
        not auth_client(member)
        .get("/api/v1/communities/meu_cantinho/")
        .data["permissions"]["can_delete"]
    )


def test_deleting_twice_is_404():
    _, leader, _ = make_community()
    client = auth_client(leader)
    body = {"confirm_commname": "meu_cantinho"}
    assert (
        client.delete("/api/v1/communities/meu_cantinho/", body, format="json").status_code == 204
    )
    assert (
        client.delete("/api/v1/communities/meu_cantinho/", body, format="json").status_code == 404
    )


def test_leader_account_deletion_still_requires_transfer_then_works_after_community_delete():
    from apps.accounts.tests.factories import DEFAULT_PASSWORD

    _, leader, _ = make_community()
    client = auth_client(leader)
    res = client.delete("/api/v1/users/me/", {"password": DEFAULT_PASSWORD}, format="json")
    assert res.status_code == 409
    assert res.data["error"]["code"] == "must_transfer_leadership"
    assert res.data["error"]["communities"] == ["meu_cantinho"]

    client.delete(
        "/api/v1/communities/meu_cantinho/", {"confirm_commname": "meu_cantinho"}, format="json"
    )
    res = client.delete("/api/v1/users/me/", {"password": DEFAULT_PASSWORD}, format="json")
    assert res.status_code == 204


def test_transfer_leadership_then_old_leader_can_delete_account():
    from apps.accounts.tests.factories import DEFAULT_PASSWORD

    community, leader, member = make_community()
    res = auth_client(leader).post(
        "/api/v1/communities/meu_cantinho/transfer-leadership/",
        {"new_leader_username": member.username},
        format="json",
    )
    assert res.status_code == 200
    assert (
        auth_client(leader)
        .delete("/api/v1/users/me/", {"password": DEFAULT_PASSWORD}, format="json")
        .status_code
        == 204
    )


def test_remove_community_photos():
    from django.core.files.uploadedfile import SimpleUploadedFile

    from apps.accounts.tests.test_account_management import _png

    community, leader, _ = make_community()
    community.community_photo = SimpleUploadedFile("c.png", _png(), content_type="image/png")
    community.banner_photo = SimpleUploadedFile("b.png", _png(), content_type="image/png")
    community.save()
    res = auth_client(leader).patch(
        "/api/v1/communities/meu_cantinho/",
        {"remove_community_photo": True, "remove_banner_photo": True},
        format="json",
    )
    assert res.status_code == 200
    community.refresh_from_db()
    assert not community.community_photo
    assert not community.banner_photo


def test_leader_edits_name_and_description():
    _, leader, _ = make_community()
    res = auth_client(leader).patch(
        "/api/v1/communities/meu_cantinho/",
        {"name": "Novo nome", "description": "Nova descrição"},
        format="json",
    )
    assert res.status_code == 200
    assert res.data["name"] == "Novo nome"
    assert res.data["description"] == "Nova descrição"
