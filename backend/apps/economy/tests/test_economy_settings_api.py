import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.tests.factories import UserFactory
from apps.economy.models import EconomySettings

pytestmark = pytest.mark.django_db


def test_economy_settings_get_unauthenticated():
    client = APIClient()
    res = client.get("/api/v1/economy/settings/")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_economy_settings_get_authenticated():
    user = UserFactory()
    client = APIClient()
    client.force_authenticate(user=user)

    res = client.get("/api/v1/economy/settings/")
    assert res.status_code == status.HTTP_200_OK
    assert res.data["id"] == 1
    assert "signup_grant" in res.data
    assert "support_cost" in res.data
    assert "bubblegram_profile_cost" in res.data
    assert "default_passive_earn_rate" in res.data
    assert "passive_interval_minutes" in res.data
    assert "passive_daily_cap" in res.data


def test_economy_settings_patch_forbidden_for_regular_user():
    user = UserFactory(is_staff=False)
    client = APIClient()
    client.force_authenticate(user=user)

    res = client.patch("/api/v1/economy/settings/", {"bubblegram_profile_cost": 25})
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_economy_settings_patch_success_for_staff():
    admin_user = UserFactory(is_staff=True)
    client = APIClient()
    client.force_authenticate(user=admin_user)

    payload = {
        "bubblegram_profile_cost": 25,
        "bubblepop_hours_per_soap": 6,
        "bubblepop_min_hours": 2,
        "bubblepop_max_hours": 36,
        "passive_daily_cap": 20,
    }
    res = client.patch("/api/v1/economy/settings/", payload)
    assert res.status_code == status.HTTP_200_OK
    assert res.data["bubblegram_profile_cost"] == 25
    assert res.data["bubblepop_hours_per_soap"] == 6
    assert res.data["bubblepop_min_hours"] == 2
    assert res.data["bubblepop_max_hours"] == 36
    assert res.data["passive_daily_cap"] == 20
    assert res.data["updated_by"] == admin_user.id
    assert res.data["updated_by_username"] == admin_user.username

    settings_obj = EconomySettings.load()
    assert settings_obj.bubblegram_profile_cost == 25
    assert settings_obj.updated_by == admin_user


def test_economy_settings_patch_validation_constraints():
    admin_user = UserFactory(is_staff=True)
    client = APIClient()
    client.force_authenticate(user=admin_user)

    # Min hours > Max hours
    res = client.patch(
        "/api/v1/economy/settings/",
        {"bubblepop_min_hours": 50, "bubblepop_max_hours": 24},
    )
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert "bubblepop_min_hours" in res.data["error"]["fields"]

    # Hours per soap <= 0
    res = client.patch(
        "/api/v1/economy/settings/",
        {"bubblepop_hours_per_soap": 0},
    )
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert "bubblepop_hours_per_soap" in res.data["error"]["fields"]

    # Passive interval <= 0
    res = client.patch(
        "/api/v1/economy/settings/",
        {"passive_interval_minutes": 0},
    )
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert "passive_interval_minutes" in res.data["error"]["fields"]
