import logging
from datetime import timedelta

import pytest
from django.core.management import CommandError, call_command
from django.utils import timezone

from apps.accounts.tests.factories import UserFactory
from apps.content.models import Bubblepop
from apps.content.tests.factories import BubblepopFactory
from apps.core.locks import advisory_lock
from apps.economy.models import ActionType, EconomySettings, SoapTransaction, Wallet

pytestmark = pytest.mark.django_db(transaction=True)


def eligible_user():
    user = UserFactory(last_seen_at=timezone.now())
    Wallet.objects.create(user=user, soap_balance=0, passive_earn_rate=5)
    return user


def test_once_runs_both_jobs_and_logs_each_execution(caplog):
    user = eligible_user()
    now = timezone.now()
    expired = BubblepopFactory(
        created_at=now - timedelta(hours=5), expires_at=now - timedelta(hours=1)
    )

    with caplog.at_level(logging.INFO, logger="bubbles.scheduler"):
        call_command("run_scheduler", "--once")

    assert Wallet.objects.get(user=user).soap_balance == 5
    assert not Bubblepop.objects.filter(pk=expired.pk).exists()
    assert "job distribute_passive_soap: finished" in caplog.text
    assert "job cleanup_expired_bubblepops: finished" in caplog.text


def test_once_twice_in_the_same_window_pays_only_once():
    user = eligible_user()

    call_command("run_scheduler", "--once")
    call_command("run_scheduler", "--once")

    assert Wallet.objects.get(user=user).soap_balance == 5
    assert (
        SoapTransaction.objects.filter(
            wallet__user=user, action_type=ActionType.PASSIVE_EARN
        ).count()
        == 1
    )


def test_once_reports_failures_but_still_runs_the_other_job(monkeypatch, caplog):
    now = timezone.now()
    expired = BubblepopFactory(
        created_at=now - timedelta(hours=5), expires_at=now - timedelta(hours=1)
    )

    def broken():
        raise RuntimeError("db exploded")

    monkeypatch.setattr(
        "apps.core.management.commands.run_scheduler.distribute_passive_soap", broken
    )

    with (
        caplog.at_level(logging.INFO, logger="bubbles.scheduler"),
        pytest.raises(CommandError, match="distribute_passive_soap"),
    ):
        call_command("run_scheduler", "--once")

    assert "job distribute_passive_soap: FAILED" in caplog.text
    assert not Bubblepop.objects.filter(pk=expired.pk).exists()


def test_passive_interval_follows_the_economy_setting():
    from apps.core.management.commands.run_scheduler import passive_interval_seconds

    settings_obj = EconomySettings.load()
    settings_obj.passive_interval_minutes = 7
    settings_obj.save()
    assert passive_interval_seconds() == 7 * 60


def test_advisory_lock_is_exclusive_across_connections():
    import threading

    from django.db import connection

    holding, release, seen = threading.Event(), threading.Event(), {}

    def holder():
        connection.close()
        try:
            with advisory_lock("test-lock") as got:
                seen["holder"] = got
                holding.set()
                release.wait(5)
        finally:
            connection.close()

    thread = threading.Thread(target=holder)
    thread.start()
    assert holding.wait(5)
    try:
        with advisory_lock("test-lock", wait=False) as got:
            assert got is False
    finally:
        release.set()
        thread.join(5)

    assert seen["holder"] is True
    with advisory_lock("test-lock", wait=False) as got:
        assert got is True  # free again once the holder released it
