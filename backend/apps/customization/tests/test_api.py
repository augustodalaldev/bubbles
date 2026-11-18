import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.tests.factories import UserFactory
from apps.customization.models import CustomizationType
from apps.customization.tests.factories import (
    CustomizationItemFactory,
    UserInventoryItemFactory,
)
from apps.economy.models import Wallet

pytestmark = pytest.mark.django_db


def test_catalog_list_public_and_filters():
    CustomizationItemFactory(
        name="Cyber Frame",
        code="cyber_frame",
        item_type=CustomizationType.AVATAR_FRAME,
        price=10,
    )
    CustomizationItemFactory(
        name="Ocean Theme",
        code="ocean_theme",
        item_type=CustomizationType.PROFILE_THEME,
        price=20,
    )
    CustomizationItemFactory(is_active=False)

    client = APIClient()
    res = client.get("/api/v1/customization/items/")
    assert res.status_code == status.HTTP_200_OK
    assert res.data["count"] == 2

    # Filter by type
    res_type = client.get(f"/api/v1/customization/items/?type={CustomizationType.AVATAR_FRAME}")
    assert res_type.status_code == status.HTTP_200_OK
    assert res_type.data["count"] == 1
    assert res_type.data["results"][0]["code"] == "cyber_frame"

    # Search
    res_search = client.get("/api/v1/customization/items/?search=Ocean")
    assert res_search.status_code == status.HTTP_200_OK
    assert res_search.data["count"] == 1
    assert res_search.data["results"][0]["code"] == "ocean_theme"


def test_catalog_annotates_is_owned_and_is_equipped():
    user = UserFactory()
    item1 = CustomizationItemFactory(item_type=CustomizationType.AVATAR_FRAME)
    item2 = CustomizationItemFactory(item_type=CustomizationType.PROFILE_THEME)

    UserInventoryItemFactory(user=user, item=item1)
    user.customization_json = {"avatar_frame": {"id": item1.id, "code": item1.code}}
    user.save(update_fields=["customization_json"])

    client = APIClient()
    client.force_authenticate(user=user)

    res = client.get("/api/v1/customization/items/")
    assert res.status_code == status.HTTP_200_OK

    results_by_id = {r["id"]: r for r in res.data["results"]}
    assert results_by_id[item1.id]["is_owned"] is True
    assert results_by_id[item1.id]["is_equipped"] is True
    assert results_by_id[item2.id]["is_owned"] is False
    assert results_by_id[item2.id]["is_equipped"] is False


def test_purchase_item_api():
    user = UserFactory()
    Wallet.objects.create(user=user, soap_balance=25)
    item = CustomizationItemFactory(price=15)

    client = APIClient()
    # Unauthenticated
    res_unauth = client.post(f"/api/v1/customization/items/{item.id}/purchase/")
    assert res_unauth.status_code == status.HTTP_401_UNAUTHORIZED

    # Authenticated purchase
    client.force_authenticate(user=user)
    res = client.post(f"/api/v1/customization/items/{item.id}/purchase/")
    assert res.status_code == status.HTTP_201_CREATED
    assert res.data["remaining_soap"] == 10
    assert res.data["inventory_item"]["item"]["id"] == item.id

    # Duplicate purchase
    res_dup = client.post(f"/api/v1/customization/items/{item.id}/purchase/")
    assert res_dup.status_code == status.HTTP_400_BAD_REQUEST

    # Insufficient soap
    expensive_item = CustomizationItemFactory(price=50)
    res_poor = client.post(f"/api/v1/customization/items/{expensive_item.id}/purchase/")
    assert res_poor.status_code == status.HTTP_409_CONFLICT


def test_user_inventory_and_equip_api():
    user = UserFactory()
    item1 = CustomizationItemFactory(item_type=CustomizationType.AVATAR_FRAME, code="frame_neon")
    item2 = CustomizationItemFactory(item_type=CustomizationType.PROFILE_THEME, code="theme_dark")
    UserInventoryItemFactory(user=user, item=item1)
    UserInventoryItemFactory(user=user, item=item2)

    client = APIClient()
    client.force_authenticate(user=user)

    # List inventory
    res_inv = client.get("/api/v1/customization/inventory/")
    assert res_inv.status_code == status.HTTP_200_OK
    assert res_inv.data["count"] == 2

    # Equip
    payload = {"item_ids": [item1.id, item2.id]}
    res_equip = client.post("/api/v1/customization/equip/", payload)
    assert res_equip.status_code == status.HTTP_200_OK
    assert "avatar_frame" in res_equip.data
    assert "profile_theme" in res_equip.data

    # Check equipped endpoint
    res_equipped = client.get("/api/v1/customization/equipped/")
    assert res_equipped.status_code == status.HTTP_200_OK
    assert res_equipped.data == res_equip.data

    # Inventory now reflects is_equipped=True
    res_inv2 = client.get("/api/v1/customization/inventory/")
    assert res_inv2.data["results"][0]["is_equipped"] is True


def test_staff_catalog_crud():
    regular_user = UserFactory(is_staff=False)
    staff_user = UserFactory(is_staff=True)

    client = APIClient()
    client.force_authenticate(user=regular_user)

    # Regular user cannot create
    payload = {
        "name": "Admin Frame",
        "code": "admin_frame",
        "item_type": CustomizationType.AVATAR_FRAME,
        "price": 50,
        "metadata": {"border_color": "#FFD700"},
    }
    assert (
        client.post("/api/v1/customization/items/", payload, format="json").status_code
        == status.HTTP_403_FORBIDDEN
    )

    # Staff user can create
    client.force_authenticate(user=staff_user)
    res_create = client.post("/api/v1/customization/items/", payload, format="json")
    assert res_create.status_code == status.HTTP_201_CREATED
    item_id = res_create.data["id"]

    # Staff user can update
    res_patch = client.patch(
        f"/api/v1/customization/items/{item_id}/",
        {"price": 40},
    )
    assert res_patch.status_code == status.HTTP_200_OK
    assert res_patch.data["price"] == 40

    # Staff user can deactivate
    res_del = client.delete(f"/api/v1/customization/items/{item_id}/")
    assert res_del.status_code == status.HTTP_204_NO_CONTENT
