import pytest

from apps.accounts.services import update_profile
from apps.accounts.tests.factories import UserFactory
from apps.core.exceptions import DomainError
from apps.customization.models import CustomizationType, UserInventoryItem
from apps.customization.services import (
    equip_customization,
    purchase_customization_item,
)
from apps.customization.tests.factories import (
    CustomizationItemFactory,
    UserInventoryItemFactory,
)
from apps.economy.exceptions import InsufficientSoap
from apps.economy.models import ActionType, Wallet

pytestmark = pytest.mark.django_db


def test_purchase_customization_item_success():
    user = UserFactory()
    wallet, _ = Wallet.objects.get_or_create(user=user, defaults={"soap_balance": 30})
    wallet.soap_balance = 30
    wallet.save()

    item = CustomizationItemFactory(price=20)

    inv = purchase_customization_item(user=user, item=item)
    assert inv.user == user
    assert inv.item == item
    assert inv.transaction is not None
    assert inv.transaction.action_type == ActionType.SPEND_CUSTOMIZATION

    wallet.refresh_from_db()
    assert wallet.soap_balance == 10
    assert UserInventoryItem.objects.filter(user=user, item=item).exists()


def test_purchase_free_customization_item():
    user = UserFactory()
    wallet, _ = Wallet.objects.get_or_create(user=user, defaults={"soap_balance": 5})

    item = CustomizationItemFactory(price=0)

    inv = purchase_customization_item(user=user, item=item)
    assert inv.user == user
    assert inv.item == item
    assert inv.transaction is None

    wallet.refresh_from_db()
    assert wallet.soap_balance == 5


def test_purchase_insufficient_soap_raises():
    user = UserFactory()
    wallet, _ = Wallet.objects.get_or_create(user=user, defaults={"soap_balance": 5})

    item = CustomizationItemFactory(price=20)

    with pytest.raises(InsufficientSoap):
        purchase_customization_item(user=user, item=item)


def test_purchase_already_owned_raises():
    user = UserFactory()
    item = CustomizationItemFactory(price=10)
    UserInventoryItemFactory(user=user, item=item)

    with pytest.raises(DomainError) as exc:
        purchase_customization_item(user=user, item=item)
    assert exc.value.code == "already_owned"


def test_purchase_inactive_item_raises():
    user = UserFactory()
    item = CustomizationItemFactory(is_active=False)

    with pytest.raises(DomainError) as exc:
        purchase_customization_item(user=user, item=item)
    assert exc.value.code == "item_inactive"


def test_equip_customization_by_item_ids_success():
    user = UserFactory()
    item_frame = CustomizationItemFactory(
        item_type=CustomizationType.AVATAR_FRAME,
        code="gold_frame",
        metadata={"border": "gold"},
    )
    item_theme = CustomizationItemFactory(
        item_type=CustomizationType.PROFILE_THEME,
        code="neon_theme",
        metadata={"color": "neon"},
    )
    UserInventoryItemFactory(user=user, item=item_frame)
    UserInventoryItemFactory(user=user, item=item_theme)

    equipped = equip_customization(user=user, item_ids=[item_frame.id, item_theme.id])
    assert "avatar_frame" in equipped
    assert equipped["avatar_frame"]["code"] == "gold_frame"
    assert equipped["avatar_frame"]["metadata"] == {"border": "gold"}
    assert "profile_theme" in equipped
    assert equipped["profile_theme"]["code"] == "neon_theme"

    user.refresh_from_db()
    assert user.customization_json == equipped

    # Clear all equipped by passing empty list
    cleared = equip_customization(user=user, item_ids=[])
    assert cleared == {}
    user.refresh_from_db()
    assert user.customization_json == {}


def test_equip_customization_unowned_item_raises():
    user = UserFactory()
    item = CustomizationItemFactory()

    with pytest.raises(DomainError) as exc:
        equip_customization(user=user, item_ids=[item.id])
    assert exc.value.code == "item_not_owned"


def test_equip_customization_slot_conflict_raises():
    user = UserFactory()
    frame1 = CustomizationItemFactory(item_type=CustomizationType.AVATAR_FRAME)
    frame2 = CustomizationItemFactory(item_type=CustomizationType.AVATAR_FRAME)
    UserInventoryItemFactory(user=user, item=frame1)
    UserInventoryItemFactory(user=user, item=frame2)

    with pytest.raises(DomainError) as exc:
        equip_customization(user=user, item_ids=[frame1.id, frame2.id])
    assert exc.value.code == "slot_conflict"


def test_equip_customization_by_slots():
    user = UserFactory()
    frame = CustomizationItemFactory(item_type=CustomizationType.AVATAR_FRAME, code="frame_blue")
    theme = CustomizationItemFactory(item_type=CustomizationType.PROFILE_THEME, code="theme_dark")
    UserInventoryItemFactory(user=user, item=frame)
    UserInventoryItemFactory(user=user, item=theme)

    # Equip frame
    res1 = equip_customization(user=user, slots={"avatar_frame": frame.id})
    assert "avatar_frame" in res1
    assert res1["avatar_frame"]["code"] == "frame_blue"

    # Equip theme alongside
    res2 = equip_customization(user=user, slots={"profile_theme": theme.id})
    assert "avatar_frame" in res2
    assert "profile_theme" in res2

    # Unequip frame
    res3 = equip_customization(user=user, slots={"avatar_frame": None})
    assert "avatar_frame" not in res3
    assert "profile_theme" in res3


def test_update_profile_validates_inventory():
    user = UserFactory()
    item = CustomizationItemFactory(code="unowned_item")

    # Trying to wear an item not in inventory raises DomainError
    payload = {"avatar_frame": {"id": item.id, "code": item.code}}
    with pytest.raises(DomainError) as exc:
        update_profile(user=user, customization_json=payload)
    assert exc.value.code == "item_not_owned"

    # Once owned, update_profile succeeds
    UserInventoryItemFactory(user=user, item=item)
    updated = update_profile(user=user, customization_json=payload)
    assert updated.customization_json == payload
