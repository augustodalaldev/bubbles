import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.tests.factories import UserFactory
from apps.communities.models import MemberRole, MemberState
from apps.communities.selectors import compute_community_permissions
from apps.communities.tests.factories import CommunityFactory, CommunityMemberFactory
from apps.core.exceptions import DomainError
from apps.customization.models import (
    CommunityInventoryItem,
    CustomizationScope,
    CustomizationType,
)
from apps.customization.services import (
    equip_community_customization,
    purchase_community_item,
    purchase_customization_item,
)
from apps.customization.tests.factories import CustomizationItemFactory
from apps.economy.exceptions import InsufficientSoap
from apps.economy.models import ActionType, SoapTransaction, Wallet

pytestmark = pytest.mark.django_db


def auth(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def community_with_soap(balance=100, **kwargs):
    community = CommunityFactory(**kwargs)
    Wallet.objects.create(community=community, soap_balance=balance)
    return community


def member(community, role=MemberRole.MEMBER, state=MemberState.ACTIVE):
    user = UserFactory()
    CommunityMemberFactory(community=community, user=user, role=role, current_state=state)
    return user


def community_item(**kwargs):
    kwargs.setdefault("scope", CustomizationScope.COMMUNITY)
    kwargs.setdefault("price", 30)
    return CustomizationItemFactory(**kwargs)


def balance(community):
    return Wallet.objects.get(community=community).soap_balance


# ----------------------------------------------------------------------------- purchase


@pytest.mark.parametrize("role", [MemberRole.LEADER, MemberRole.COMM_ADMIN])
def test_leader_and_admin_buy_with_the_community_wallet(role):
    community = community_with_soap(100)
    actor = member(community, role)
    item = community_item(price=30)

    holding = purchase_community_item(actor=actor, community=community, item=item)

    assert balance(community) == 70
    assert holding.purchased_by == actor
    tx = SoapTransaction.objects.get(pk=holding.transaction_id)
    assert tx.wallet.community == community
    assert tx.amount == -30
    assert tx.balance_after == 70
    assert tx.action_type == ActionType.SPEND_CUSTOMIZATION


def test_the_buyers_personal_wallet_is_never_touched():
    community = community_with_soap(100)
    actor = member(community, MemberRole.LEADER)
    Wallet.objects.create(user=actor, soap_balance=500)

    purchase_community_item(actor=actor, community=community, item=community_item())

    assert Wallet.objects.get(user=actor).soap_balance == 500


def test_free_item_creates_no_ledger_row():
    community = community_with_soap(10)
    actor = member(community, MemberRole.LEADER)

    holding = purchase_community_item(
        actor=actor, community=community, item=community_item(price=0)
    )

    assert holding.transaction is None
    assert balance(community) == 10


def test_insufficient_soap_changes_nothing():
    community = community_with_soap(10)
    actor = member(community, MemberRole.LEADER)

    with pytest.raises(InsufficientSoap) as exc:
        purchase_community_item(actor=actor, community=community, item=community_item(price=30))

    assert exc.value.code == "insufficient_soap"
    assert balance(community) == 10
    assert not CommunityInventoryItem.objects.exists()


@pytest.mark.parametrize(
    "who",
    ["member", "silenced_admin", "banned", "non_member", "system_staff"],
)
def test_other_people_cannot_spend_the_community_soap(who):
    community = community_with_soap(100)
    actors = {
        "member": lambda: member(community, MemberRole.MEMBER),
        "silenced_admin": lambda: member(community, MemberRole.COMM_ADMIN, MemberState.SILENCED),
        "banned": lambda: member(community, MemberRole.MEMBER, MemberState.BANNED),
        "non_member": lambda: UserFactory(),
        "system_staff": lambda: UserFactory(is_staff=True),
    }
    actor = actors[who]()

    with pytest.raises(DomainError) as exc:
        purchase_community_item(actor=actor, community=community, item=community_item())

    assert exc.value.code == "permission_denied"
    assert balance(community) == 100
    assert not CommunityInventoryItem.objects.exists()


def test_buying_the_same_item_twice_is_rejected_and_charged_once():
    community = community_with_soap(100)
    actor = member(community, MemberRole.LEADER)
    item = community_item(price=30)
    purchase_community_item(actor=actor, community=community, item=item)

    with pytest.raises(DomainError) as exc:
        purchase_community_item(actor=actor, community=community, item=item)

    assert exc.value.code == "already_owned"
    assert balance(community) == 70
    assert CommunityInventoryItem.objects.count() == 1


def test_two_communities_can_own_the_same_item():
    item = community_item(price=10)
    for _ in range(2):
        community = community_with_soap(50)
        purchase_community_item(
            actor=member(community, MemberRole.LEADER), community=community, item=item
        )
    assert CommunityInventoryItem.objects.count() == 2


def test_inactive_item_and_user_only_item_are_rejected():
    community = community_with_soap(100)
    actor = member(community, MemberRole.LEADER)

    with pytest.raises(DomainError) as inactive:
        purchase_community_item(
            actor=actor, community=community, item=community_item(is_active=False)
        )
    assert inactive.value.code == "item_inactive"

    with pytest.raises(DomainError) as scope:
        purchase_community_item(
            actor=actor,
            community=community,
            item=community_item(scope=CustomizationScope.USER),
        )
    assert scope.value.code == "item_scope_mismatch"
    assert balance(community) == 100


def test_both_scope_items_are_available_to_communities():
    community = community_with_soap(100)
    actor = member(community, MemberRole.LEADER)
    holding = purchase_community_item(
        actor=actor, community=community, item=community_item(scope=CustomizationScope.BOTH)
    )
    assert holding.pk


@pytest.mark.parametrize(
    ("field", "code"),
    [("blocked_at", "community_blocked"), ("archived_at", "community_archived")],
)
def test_blocked_or_archived_community_cannot_buy(field, code):
    community = community_with_soap(100, **{field: timezone.now()})
    actor = member(community, MemberRole.LEADER)

    with pytest.raises(DomainError) as exc:
        purchase_community_item(actor=actor, community=community, item=community_item())

    assert exc.value.code == code
    assert balance(community) == 100


# ----------------------------------------------------------------------------- users


def test_users_cannot_buy_community_only_items():
    user = UserFactory()
    Wallet.objects.create(user=user, soap_balance=100)

    with pytest.raises(DomainError) as exc:
        purchase_customization_item(user=user, item=community_item())

    assert exc.value.code == "item_scope_mismatch"
    assert Wallet.objects.get(user=user).soap_balance == 100


def test_user_catalog_hides_community_only_items_and_community_catalog_hides_user_only():
    user_item = CustomizationItemFactory(scope=CustomizationScope.USER)
    comm_item = community_item()
    both_item = CustomizationItemFactory(scope=CustomizationScope.BOTH)
    community = community_with_soap(10)
    client = auth(UserFactory())

    users_view = {i["id"] for i in client.get("/api/v1/customization/items/").data["results"]}
    assert users_view == {user_item.id, both_item.id}

    url = f"/api/v1/customization/items/?community={community.commname}"
    comm_view = {i["id"] for i in client.get(url).data["results"]}
    assert comm_view == {comm_item.id, both_item.id}


# ----------------------------------------------------------------------------- API


def test_purchase_api_returns_item_and_remaining_community_soap():
    community = community_with_soap(100)
    leader = member(community, MemberRole.LEADER)
    item = community_item(price=40)

    res = auth(leader).post(
        f"/api/v1/communities/{community.commname}/customization/items/{item.id}/purchase/"
    )

    assert res.status_code == status.HTTP_201_CREATED
    assert res.data["remaining_soap"] == 60
    assert res.data["inventory_item"]["item"]["id"] == item.id
    assert res.data["inventory_item"]["item"]["is_owned"] is True
    assert res.data["inventory_item"]["purchased_by_username"] == leader.username


def test_purchase_api_error_shapes():
    community = community_with_soap(5)
    leader = member(community, MemberRole.LEADER)
    plain = member(community)
    item = community_item(price=40)
    base = f"/api/v1/communities/{community.commname}/customization/items"

    short = auth(leader).post(f"{base}/{item.id}/purchase/")
    assert short.status_code == status.HTTP_409_CONFLICT
    assert short.data["error"]["code"] == "insufficient_soap"
    assert short.data["error"]["cost"] == 40
    assert short.data["error"]["balance"] == 5

    denied = auth(plain).post(f"{base}/{item.id}/purchase/")
    assert denied.status_code == status.HTTP_403_FORBIDDEN
    assert denied.data["error"]["code"] == "permission_denied"

    missing = auth(leader).post(f"{base}/999999/purchase/")
    assert missing.status_code == status.HTTP_404_NOT_FOUND
    assert missing.data["error"]["code"] == "not_found"

    unknown = auth(leader).post("/api/v1/communities/nope_comm/customization/items/1/purchase/")
    assert unknown.status_code == status.HTTP_404_NOT_FOUND
    assert unknown.data["error"]["code"] == "community_not_found"

    anonymous = APIClient().post(f"{base}/{item.id}/purchase/")
    assert anonymous.status_code == status.HTTP_401_UNAUTHORIZED


def test_community_catalog_is_relative_to_the_community():
    community = community_with_soap(100)
    leader = member(community, MemberRole.LEADER)
    item = community_item()
    other = community_item()
    purchase_community_item(actor=leader, community=community, item=item)
    equip_community_customization(
        actor=leader, community=community, slots={item.item_type.lower(): item.id}
    )

    res = auth(leader).get(f"/api/v1/customization/items/?community={community.commname}")
    flags = {i["id"]: (i["is_owned"], i["is_equipped"]) for i in res.data["results"]}
    assert flags[item.id] == (True, True)
    assert flags[other.id] == (False, False)


def test_inventory_endpoint_lists_the_communitys_items():
    community = community_with_soap(100)
    leader = member(community, MemberRole.LEADER)
    item = community_item()
    purchase_community_item(actor=leader, community=community, item=item)

    res = auth(UserFactory()).get(
        f"/api/v1/communities/{community.commname}/customization/inventory/"
    )

    assert res.status_code == status.HTTP_200_OK
    assert [i["item"]["id"] for i in res.data["results"]] == [item.id]
    assert res.data["results"][0]["is_equipped"] is False


# ----------------------------------------------------------------------------- equip


def test_equip_and_unequip_by_slot_leaves_other_slots_alone():
    community = community_with_soap(200)
    leader = member(community, MemberRole.LEADER)
    frame = community_item(item_type=CustomizationType.AVATAR_FRAME)
    badge = community_item(item_type=CustomizationType.BADGE)
    for item in (frame, badge):
        purchase_community_item(actor=leader, community=community, item=item)

    equip_community_customization(
        actor=leader, community=community, slots={"avatar_frame": frame.id}
    )
    result = equip_community_customization(
        actor=leader, community=community, slots={"badge": badge.id}
    )
    assert set(result) == {"avatar_frame", "badge"}
    assert result["badge"]["metadata"] == badge.metadata

    result = equip_community_customization(
        actor=leader, community=community, slots={"avatar_frame": None}
    )
    assert set(result) == {"badge"}
    community.refresh_from_db()
    assert set(community.customization_json) == {"badge"}


def test_equip_rejects_unowned_missing_and_mismatched_items():
    community = community_with_soap(100)
    leader = member(community, MemberRole.LEADER)
    owned = community_item(item_type=CustomizationType.AVATAR_FRAME)
    purchase_community_item(actor=leader, community=community, item=owned)

    not_owned = community_item(item_type=CustomizationType.BADGE)
    with pytest.raises(DomainError) as e1:
        equip_community_customization(
            actor=leader, community=community, slots={"badge": not_owned.id}
        )
    assert e1.value.code == "item_not_owned"

    with pytest.raises(DomainError) as e2:
        equip_community_customization(actor=leader, community=community, slots={"badge": 999999})
    assert e2.value.code == "item_not_found"

    with pytest.raises(DomainError) as e3:
        equip_community_customization(actor=leader, community=community, slots={"badge": owned.id})
    assert e3.value.code == "slot_mismatch"

    community.refresh_from_db()
    assert community.customization_json in ({}, None)


def test_equip_requires_leader_or_admin_and_an_open_community():
    community = community_with_soap(100)
    plain = member(community)
    with pytest.raises(DomainError) as exc:
        equip_community_customization(actor=plain, community=community, slots={"badge": None})
    assert exc.value.code == "permission_denied"

    archived = community_with_soap(100, archived_at=timezone.now())
    with pytest.raises(DomainError) as exc:
        equip_community_customization(
            actor=member(archived, MemberRole.LEADER), community=archived, slots={"badge": None}
        )
    assert exc.value.code == "community_archived"


def test_equip_api_roundtrip():
    community = community_with_soap(100)
    admin = member(community, MemberRole.COMM_ADMIN)
    item = community_item(item_type=CustomizationType.PROFILE_THEME)
    purchase_community_item(actor=admin, community=community, item=item)
    url = f"/api/v1/communities/{community.commname}/customization/equip/"

    res = auth(admin).post(url, {"slots": {"profile_theme": item.id}}, format="json")
    assert res.status_code == status.HTTP_200_OK
    assert res.data["profile_theme"]["id"] == item.id
    assert auth(UserFactory()).get(url).data["profile_theme"]["id"] == item.id

    bad = auth(admin).post(url, {}, format="json")
    assert bad.status_code == status.HTTP_400_BAD_REQUEST
    assert bad.data["error"]["code"] == "validation_error"

    detail = auth(admin).get(f"/api/v1/communities/{community.commname}/")
    assert detail.data["customization_json"]["profile_theme"]["id"] == item.id


# ----------------------------------------------------------------------------- permissions map


@pytest.mark.parametrize(
    ("role", "state", "expected"),
    [
        (MemberRole.LEADER, MemberState.ACTIVE, True),
        (MemberRole.COMM_ADMIN, MemberState.ACTIVE, True),
        (MemberRole.MEMBER, MemberState.ACTIVE, False),
        (MemberRole.COMM_ADMIN, MemberState.SILENCED, False),
        (MemberRole.MEMBER, MemberState.BANNED, False),
    ],
)
def test_can_customize_follows_role_and_state(role, state, expected):
    community = CommunityFactory()
    user = member(community, role, state)
    perms = compute_community_permissions(community=community, user=user)
    assert perms["can_customize"] is expected


def test_can_customize_is_false_for_staff_visitors_and_closed_communities():
    community = CommunityFactory()
    assert (
        compute_community_permissions(community=community, user=UserFactory(is_staff=True))[
            "can_customize"
        ]
        is False
    )
    archived = CommunityFactory(archived_at=timezone.now())
    leader = member(archived, MemberRole.LEADER)
    assert compute_community_permissions(community=archived, user=leader)["can_customize"] is False
