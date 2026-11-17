import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

import pytest
from django.db import connection
from django.utils import timezone

from apps.accounts.tests.factories import UserFactory
from apps.content.models import Bubblepop
from apps.content.services import cleanup_expired_bubblepops
from apps.content.tests.factories import BubblepopFactory
from apps.economy import services as economy_services
from apps.economy.models import ActionType, EconomySettings, SoapTransaction, Wallet
from apps.economy.services import distribute_passive_soap

pytestmark = pytest.mark.django_db(transaction=True)


def configure(rate=5, interval=5, cap=15):
    settings_obj = EconomySettings.load()
    settings_obj.default_passive_earn_rate = rate
    settings_obj.passive_interval_minutes = interval
    settings_obj.passive_daily_cap = cap
    settings_obj.save()


def seen_user(now):
    user = UserFactory(last_seen_at=now)
    Wallet.objects.create(user=user, soap_balance=0, passive_earn_rate=5)
    return user


def paid(user):
    return SoapTransaction.objects.filter(
        wallet__user=user, action_type=ActionType.PASSIVE_EARN
    ).count()


def in_thread(func):
    connection.close()  # each thread needs its own DB connection
    try:
        return func()
    finally:
        connection.close()


def test_running_twice_in_the_same_window_pays_once():
    configure()
    now = timezone.now()
    user = seen_user(now)

    assert distribute_passive_soap(now=now) == 1
    assert distribute_passive_soap(now=now) == 0
    assert distribute_passive_soap(now=now + timedelta(seconds=30)) in (0, 1)  # same/next window

    assert Wallet.objects.get(user=user).soap_balance in (5, 10)
    assert paid(user) == Wallet.objects.get(user=user).soap_balance // 5


def test_overlapping_runs_never_double_pay():
    configure(cap=100)
    now = timezone.now()
    users = [seen_user(now) for _ in range(5)]

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = [
            f.result()
            for f in [
                pool.submit(in_thread, lambda: distribute_passive_soap(now=now)) for _ in range(4)
            ]
        ]

    assert sum(results) == 5  # each user paid by exactly one of the runs
    assert all(paid(u) == 1 for u in users)
    assert all(Wallet.objects.get(user=u).soap_balance == 5 for u in users)


def test_overlapping_runs_respect_the_daily_cap():
    configure(rate=5, cap=7)
    now = timezone.now()
    user = seen_user(now)
    Wallet.objects.filter(user=user).update(soap_balance=0)

    windows = [now + timedelta(minutes=5 * i) for i in range(4)]
    for stamp in windows:
        User = type(user)
        User.objects.filter(pk=user.pk).update(last_seen_at=stamp)
        with ThreadPoolExecutor(max_workers=2) as pool:
            for f in [
                pool.submit(in_thread, lambda s=stamp: distribute_passive_soap(now=s))
                for _ in range(2)
            ]:
                f.result()

    assert Wallet.objects.get(user=user).soap_balance <= 7


def test_a_failing_user_is_logged_and_does_not_block_the_others(monkeypatch, caplog):
    configure()
    now = timezone.now()
    first, second = seen_user(now), seen_user(now)
    real_credit = economy_services.credit

    def flaky(wallet, amount, **kwargs):
        if wallet.user_id == first.id:
            raise RuntimeError("ledger down")
        return real_credit(wallet, amount, **kwargs)

    monkeypatch.setattr(economy_services, "credit", flaky)

    with caplog.at_level(logging.ERROR, logger="apps.economy.services"):
        credited = distribute_passive_soap(now=now)

    assert credited == 1
    assert paid(first) == 0 and paid(second) == 1
    assert f"failed to pay user {first.id}" in caplog.text


def test_cleanup_twice_deletes_once_then_nothing():
    now = timezone.now()
    for _ in range(3):
        BubblepopFactory(created_at=now - timedelta(hours=5), expires_at=now - timedelta(hours=1))
    active = BubblepopFactory(expires_at=now + timedelta(hours=3))

    assert cleanup_expired_bubblepops(now=now) == 3
    assert cleanup_expired_bubblepops(now=now) == 0
    assert list(Bubblepop.objects.values_list("pk", flat=True)) == [active.pk]


def test_overlapping_cleanups_delete_each_row_exactly_once():
    now = timezone.now()
    for _ in range(6):
        BubblepopFactory(created_at=now - timedelta(hours=5), expires_at=now - timedelta(hours=1))

    with ThreadPoolExecutor(max_workers=3) as pool:
        results = [
            f.result()
            for f in [
                pool.submit(in_thread, lambda: cleanup_expired_bubblepops(now=now))
                for _ in range(3)
            ]
        ]

    assert sum(results) == 6
    assert not Bubblepop.objects.exists()
