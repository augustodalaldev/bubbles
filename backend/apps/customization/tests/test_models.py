import pytest
from django.db import IntegrityError

from apps.accounts.tests.factories import UserFactory
from apps.customization.models import CustomizationType
from apps.customization.tests.factories import (
    CustomizationItemFactory,
    UserInventoryItemFactory,
)

pytestmark = pytest.mark.django_db


def test_customization_item_str_and_ordering():
    item = CustomizationItemFactory(
        name="Golden Bubble",
        item_type=CustomizationType.AVATAR_FRAME,
        price=15,
    )
    assert "Golden Bubble" in str(item)
    assert "15 soap" in str(item)


def test_user_inventory_unique_constraint():
    user = UserFactory()
    item = CustomizationItemFactory()

    UserInventoryItemFactory(user=user, item=item)

    with pytest.raises(IntegrityError):
        UserInventoryItemFactory(user=user, item=item)
