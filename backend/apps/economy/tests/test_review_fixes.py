from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from django.utils import timezone

from apps.accounts.services import register_user
from apps.accounts.tests.factories import DEFAULT_PASSWORD, UserFactory
from apps.communities.services import create_community
from apps.communities.tests.factories import CommunityFactory, CommunityMemberFactory
from apps.content.models import Bubblegram, BubblegramType
from apps.content.services import create_bubblegram, support_bubblegram
from apps.economy.models import ActionType, EconomySettings, SoapTransaction, Wallet
from apps.economy.services import distribute_passive_soap

pytestmark = pytest.mark.django_db

UTC = ZoneInfo("UTC")


def set_economy(**values):
    settings_obj = EconomySettings.load()
    for key, value in values.items():
        setattr(settings_obj, key, value)
    settings_obj.save()


def test_passive_daily_cap_resets_at_local_midnight_not_utc():
    set_economy(default_passive_earn_rate=5, passive_interval_minutes=5, passive_daily_cap=15)
    # `timezone.now()` is UTC: 04:30 UTC on 17 Nov is 01:30 in Sao Paulo (still the 17th there,
    # but the UTC day started 4.5 hours earlier than the local one).
    now = datetime(2026, 11, 17, 4, 30, tzinfo=UTC)
    user = UserFactory(last_seen_at=now - timedelta(minutes=1))
    wallet = Wallet.objects.create(user=user, soap_balance=0, passive_earn_rate=5)
    # The cap was fully used at 23:00 local on 16 Nov (02:00 UTC on 17 Nov).
    SoapTransaction.objects.create(
        wallet=wallet,
        amount=15,
        action_type=ActionType.PASSIVE_EARN,
        balance_after=15,
        created_at=datetime(2026, 11, 17, 2, 0, tzinfo=UTC),
    )
    wallet.soap_balance = 15
    wallet.save()

    assert distribute_passive_soap(now=now) == 1
    wallet.refresh_from_db()
    assert wallet.soap_balance == 20


def test_passive_daily_cap_still_applies_within_the_same_local_day():
    set_economy(default_passive_earn_rate=5, passive_interval_minutes=5, passive_daily_cap=15)
    now = datetime(2026, 11, 17, 15, 0, tzinfo=UTC)  # 12:00 local
    user = UserFactory(last_seen_at=now - timedelta(minutes=1))
    wallet = Wallet.objects.create(user=user, soap_balance=15, passive_earn_rate=5)
    SoapTransaction.objects.create(
        wallet=wallet,
        amount=15,
        action_type=ActionType.PASSIVE_EARN,
        balance_after=15,
        created_at=datetime(2026, 11, 17, 12, 0, tzinfo=UTC),  # 09:00 local
    )

    assert distribute_passive_soap(now=now) == 0


def test_signup_works_when_signup_grant_is_zero():
    set_economy(signup_grant=0)
    user = register_user(
        username="zero_grant",
        email="zero@example.com",
        password=DEFAULT_PASSWORD,
        name="Zero",
        birth_date=timezone.localdate() - timedelta(days=365 * 20),
    )
    assert Wallet.objects.get(user=user).soap_balance == 0
    assert not SoapTransaction.objects.filter(wallet__user=user).exists()


def test_founding_works_when_founding_cost_is_zero():
    set_economy(founding_cost=0)
    creator = UserFactory()
    Wallet.objects.create(user=creator, soap_balance=0)
    community = create_community(creator=creator, commname="free_comm", name="Free")
    assert community.member_count == 1
    assert Wallet.objects.get(community=community).soap_balance == 0


def test_posting_works_when_bubblegram_cost_is_zero():
    set_economy(bubblegram_profile_cost=0)
    author = UserFactory()
    Wallet.objects.create(user=author, soap_balance=0)
    post = create_bubblegram(author=author, type=BubblegramType.TEXT, text="free")
    assert post.pk is not None
    assert not SoapTransaction.objects.filter(wallet__user=author).exists()


def test_support_works_when_credits_are_zero():
    set_economy(author_credit=0, community_credit=0)
    author, donor = UserFactory(), UserFactory()
    community = CommunityFactory()
    Wallet.objects.create(user=author, soap_balance=5)
    Wallet.objects.create(user=donor, soap_balance=5)
    Wallet.objects.create(community=community, soap_balance=5)
    CommunityMemberFactory(community=community, user=donor)
    post = Bubblegram.objects.create(
        user=author, community=community, text="x", type=BubblegramType.TEXT
    )

    support_bubblegram(donor=donor, bubblegram=post)

    donor.wallet.refresh_from_db()
    author.wallet.refresh_from_db()
    assert donor.wallet.soap_balance == 4
    assert author.wallet.soap_balance == 5
    post.refresh_from_db()
    assert post.soap_count == 1


def test_support_works_when_support_cost_is_zero():
    set_economy(support_cost=0)
    author, donor = UserFactory(), UserFactory()
    Wallet.objects.create(user=author, soap_balance=5)
    Wallet.objects.create(user=donor, soap_balance=0)
    post = Bubblegram.objects.create(user=author, text="x", type=BubblegramType.TEXT)

    support_bubblegram(donor=donor, bubblegram=post)

    author.wallet.refresh_from_db()
    assert author.wallet.soap_balance == 6
