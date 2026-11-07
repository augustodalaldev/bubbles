from datetime import timedelta
from io import StringIO

import pytest
from django.core.management import call_command
from django.utils import timezone

from apps.accounts.tests.factories import UserFactory
from apps.economy.models import ActionType, EconomySettings, SoapTransaction, Wallet
from apps.economy.services import distribute_passive_soap

pytestmark = pytest.mark.django_db


def test_distribute_passive_soap_eligible_users():
    settings = EconomySettings.load()
    settings.default_passive_earn_rate = 5
    settings.passive_interval_minutes = 5
    settings.passive_daily_cap = 15
    settings.save()

    now = timezone.now()

    # User 1: active, seen 2 minutes ago -> eligible
    user1 = UserFactory(last_seen_at=now - timedelta(minutes=2))
    wallet1, _ = Wallet.objects.get_or_create(user=user1, defaults={"soap_balance": 10})

    # User 2: active, seen 10 minutes ago -> ineligible (past 5 min cutoff)
    user2 = UserFactory(last_seen_at=now - timedelta(minutes=10))
    Wallet.objects.get_or_create(user=user2, defaults={"soap_balance": 10})

    # User 3: inactive, seen 1 minute ago -> ineligible
    user3 = UserFactory(last_seen_at=now - timedelta(minutes=1), is_active=False)
    Wallet.objects.get_or_create(user=user3, defaults={"soap_balance": 10})

    # User 4: soft-deleted, seen 1 minute ago -> ineligible
    user4 = UserFactory(last_seen_at=now - timedelta(minutes=1), deleted_at=now)
    Wallet.objects.get_or_create(user=user4, defaults={"soap_balance": 10})

    credited = distribute_passive_soap(now=now)
    assert credited == 1

    wallet1.refresh_from_db()
    assert wallet1.soap_balance == 15

    tx = SoapTransaction.objects.filter(wallet=wallet1, action_type=ActionType.PASSIVE_EARN).first()
    assert tx is not None
    assert tx.amount == 5


def test_distribute_passive_soap_idempotent_within_same_window():
    now = timezone.now()
    user = UserFactory(last_seen_at=now - timedelta(minutes=1))
    wallet, _ = Wallet.objects.get_or_create(user=user, defaults={"soap_balance": 0})

    credited1 = distribute_passive_soap(now=now)
    assert credited1 == 1
    wallet.refresh_from_db()
    assert wallet.soap_balance == 5

    # Second call in the same time window should not credit again
    credited2 = distribute_passive_soap(now=now)
    assert credited2 == 0
    wallet.refresh_from_db()
    assert wallet.soap_balance == 5


def test_distribute_passive_soap_respects_daily_cap():
    settings = EconomySettings.load()
    settings.passive_daily_cap = 12
    settings.default_passive_earn_rate = 5
    settings.passive_interval_minutes = 5
    settings.save()

    base_time = timezone.now().replace(hour=10, minute=0, second=0, microsecond=0)
    user = UserFactory(last_seen_at=base_time)
    wallet, _ = Wallet.objects.get_or_create(user=user, defaults={"soap_balance": 0})

    # Window 1 (10:00): receives 5 (total: 5)
    t1 = base_time
    user.last_seen_at = t1
    user.save(update_fields=["last_seen_at"])
    credited = distribute_passive_soap(now=t1)
    assert credited == 1
    wallet.refresh_from_db()
    assert wallet.soap_balance == 5

    # Window 2 (10:06): receives 5 (total: 10)
    t2 = base_time + timedelta(minutes=6)
    user.last_seen_at = t2
    user.save(update_fields=["last_seen_at"])
    credited = distribute_passive_soap(now=t2)
    assert credited == 1
    wallet.refresh_from_db()
    assert wallet.soap_balance == 10

    # Window 3 (10:12): daily cap is 12, so only 2 should be granted
    t3 = base_time + timedelta(minutes=12)
    user.last_seen_at = t3
    user.save(update_fields=["last_seen_at"])
    credited = distribute_passive_soap(now=t3)
    assert credited == 1
    wallet.refresh_from_db()
    assert wallet.soap_balance == 12

    # Window 4 (10:18): cap reached, 0 granted
    t4 = base_time + timedelta(minutes=18)
    user.last_seen_at = t4
    user.save(update_fields=["last_seen_at"])
    credited = distribute_passive_soap(now=t4)
    assert credited == 0
    wallet.refresh_from_db()
    assert wallet.soap_balance == 12


def test_distribute_passive_soap_management_command():
    now = timezone.now()
    user = UserFactory(last_seen_at=now - timedelta(seconds=30))
    Wallet.objects.get_or_create(user=user, defaults={"soap_balance": 0})

    out = StringIO()
    call_command("distribute_passive_soap", stdout=out)
    output = out.getvalue()
    assert "Successfully distributed passive soap to" in output
