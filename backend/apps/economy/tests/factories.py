import factory

from apps.accounts.tests.factories import UserFactory
from apps.economy.models import ActionType, EconomySettings, SoapTransaction, Wallet


class EconomySettingsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EconomySettings
        django_get_or_create = ("id",)

    id = 1
    signup_grant = 20
    support_cost = 1
    author_credit = 1
    community_credit = 1
    bubblegram_profile_cost = 10
    bubblegram_community_cost = 10
    bubblepop_hours_per_soap = 4
    bubblepop_min_hours = 1
    bubblepop_max_hours = 48
    founding_cost = 300
    default_passive_earn_rate = 5
    passive_interval_minutes = 5
    passive_daily_cap = 15


class WalletFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Wallet

    user = factory.SubFactory(UserFactory)
    community = None
    soap_balance = 0
    passive_earn_rate = 5


class SoapTransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SoapTransaction

    wallet = factory.SubFactory(WalletFactory)
    amount = 20
    action_type = ActionType.SIGNUP_GRANT
    balance_after = 20
    idempotency_key = factory.Sequence(lambda n: f"key_{n:06d}")
