import pytest
from django.core.cache import cache
from django.db import IntegrityError, transaction

from apps.core.exceptions import DomainError
from apps.economy.models import EconomySettings

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def clear_economy_cache():
    cache.clear()
    yield
    cache.clear()


def test_default_values_match_requirements_changes():
    settings = EconomySettings.load()

    assert settings.id == 1
    assert settings.signup_grant == 20
    assert settings.support_cost == 1
    assert settings.author_credit == 1
    assert settings.community_credit == 1
    assert settings.bubblegram_profile_cost == 10
    assert settings.bubblegram_community_cost == 10
    assert settings.bubblepop_hours_per_soap == 4
    assert settings.bubblepop_min_hours == 1
    assert settings.bubblepop_max_hours == 48
    assert settings.founding_cost == 300
    assert settings.default_passive_earn_rate == 5
    assert settings.passive_interval_minutes == 5
    assert settings.passive_daily_cap == 15


def test_singleton_load_uses_cache():
    first = EconomySettings.load()
    second = EconomySettings.load()
    assert first.pk == second.pk


def test_singleton_save_updates_cache():
    settings = EconomySettings.load()
    settings.signup_grant = 50
    settings.save()

    reloaded = EconomySettings.load()
    assert reloaded.signup_grant == 50


def test_singleton_cannot_be_deleted():
    settings = EconomySettings.load()
    with pytest.raises(DomainError, match="cannot be deleted"):
        settings.delete()


class TestDatabaseConstraints:
    def test_database_rejects_row_with_id_different_than_one(self):
        EconomySettings.load()

        with pytest.raises(IntegrityError, match="chk_economy_settings_singleton"):
            with transaction.atomic():
                EconomySettings.objects.filter(id=1).update(id=2)

    def test_bubblepop_hours_range_constraint(self):
        with pytest.raises(IntegrityError, match="chk_economy_bubblepop_hours_range"):
            with transaction.atomic():
                # min hours cannot be greater than max hours
                EconomySettings(id=1, bubblepop_min_hours=10, bubblepop_max_hours=5).save()
