import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.accounts.tests.factories import UserFactory
from apps.communities.tests.factories import CommunityFactory
from apps.economy.models import Wallet

pytestmark = pytest.mark.django_db


def test_user_wallet_creation_and_clean():
    user = UserFactory()
    wallet = Wallet(user=user, soap_balance=20, passive_earn_rate=5)
    wallet.full_clean()
    wallet.save()

    assert wallet.pk is not None
    assert wallet.is_user_wallet
    assert not wallet.is_community_wallet
    assert wallet.owner == user
    assert "user:" in str(wallet)


def test_community_wallet_creation_and_clean():
    community = CommunityFactory()
    wallet = Wallet(community=community, soap_balance=300)
    wallet.full_clean()
    wallet.save()

    assert wallet.pk is not None
    assert wallet.is_community_wallet
    assert not wallet.is_user_wallet
    assert wallet.owner == community
    assert "community:" in str(wallet)


def test_wallet_must_have_an_owner_full_clean():
    wallet = Wallet(soap_balance=10)
    with pytest.raises(ValidationError) as exc:
        wallet.full_clean()

    assert "__all__" in exc.value.message_dict


def test_wallet_cannot_have_both_owners_full_clean():
    user = UserFactory()
    community = CommunityFactory()
    wallet = Wallet(user=user, community=community, soap_balance=10)

    with pytest.raises(ValidationError) as exc:
        wallet.full_clean()

    assert "__all__" in exc.value.message_dict


def test_community_wallet_cannot_have_passive_rate_full_clean():
    community = CommunityFactory()
    wallet = Wallet(community=community, soap_balance=10, passive_earn_rate=5)

    with pytest.raises(ValidationError) as exc:
        wallet.full_clean()

    assert "__all__" in exc.value.message_dict


class TestDatabaseConstraints:
    def test_database_rejects_wallet_without_owner(self):
        with pytest.raises(IntegrityError, match="chk_wallet_exactly_one_owner"):
            with transaction.atomic():
                Wallet.objects.create(soap_balance=10)

    def test_database_rejects_wallet_with_both_owners(self):
        user = UserFactory()
        community = CommunityFactory()

        with pytest.raises(IntegrityError, match="chk_wallet_exactly_one_owner"):
            with transaction.atomic():
                Wallet.objects.create(user=user, community=community, soap_balance=10)

    def test_database_rejects_community_wallet_with_passive_rate(self):
        community = CommunityFactory()

        with pytest.raises(IntegrityError, match="chk_wallet_passive_rate_users_only"):
            with transaction.atomic():
                Wallet.objects.create(community=community, soap_balance=10, passive_earn_rate=5)

    def test_database_rejects_negative_balance(self):
        user = UserFactory()

        with pytest.raises(IntegrityError, match="soap_balance"):
            with transaction.atomic():
                Wallet.objects.create(user=user, soap_balance=-1)

    def test_user_can_have_only_one_wallet(self):
        user = UserFactory()
        Wallet.objects.create(user=user, soap_balance=10)

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Wallet.objects.create(user=user, soap_balance=20)

    def test_community_can_have_only_one_wallet(self):
        community = CommunityFactory()
        Wallet.objects.create(community=community, soap_balance=100)

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Wallet.objects.create(community=community, soap_balance=200)
