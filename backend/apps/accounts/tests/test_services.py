from datetime import timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone

from apps.accounts.models import User
from apps.accounts.services import delete_account, register_user, update_profile
from apps.accounts.tests.factories import DEFAULT_PASSWORD, UserConnectionFactory, UserFactory
from apps.communities.models import CommunityMember, MemberRole
from apps.communities.tests.factories import CommunityFactory, CommunityMemberFactory
from apps.core.exceptions import DomainError
from apps.economy.models import ActionType, EconomySettings, SoapTransaction, Wallet

pytestmark = pytest.mark.django_db


def test_register_user_success():
    settings_obj = EconomySettings.load()
    birth_date = timezone.localdate() - timedelta(days=365 * 20)

    user = register_user(
        username="alice_bubble",
        email="alice@EXAMPLE.COM",
        password=DEFAULT_PASSWORD,
        name="Alice Bubble",
        birth_date=birth_date,
        description="Hello Bubbles!",
    )

    assert user.pk is not None
    assert user.username == "alice_bubble"
    assert user.email == "alice@example.com"
    assert user.name == "Alice Bubble"
    assert user.description == "Hello Bubbles!"
    assert user.is_active is True
    assert user.deleted_at is None

    # Wallet created with signup grant
    wallet = Wallet.objects.get(user=user)
    assert wallet.soap_balance == settings_obj.signup_grant
    assert wallet.passive_earn_rate == settings_obj.default_passive_earn_rate

    # Ledger row created with idempotency key
    tx = SoapTransaction.objects.get(wallet=wallet)
    assert tx.amount == settings_obj.signup_grant
    assert tx.action_type == ActionType.SIGNUP_GRANT
    assert tx.balance_after == settings_obj.signup_grant
    assert tx.idempotency_key == f"signup:{user.id}"


def test_register_user_rollback_on_failure():
    birth_date = timezone.localdate() - timedelta(days=365 * 20)

    with patch("apps.economy.services.credit", side_effect=RuntimeError("Soap minting failed")):
        with pytest.raises(RuntimeError, match="Soap minting failed"):
            register_user(
                username="bob_fail",
                email="bob@example.com",
                password=DEFAULT_PASSWORD,
                name="Bob Fail",
                birth_date=birth_date,
            )

    # Invariant: atomic rollback leaves neither user nor wallet
    assert not User.objects.filter(username="bob_fail").exists()
    assert not Wallet.objects.filter(user__username="bob_fail").exists()


def test_register_user_duplicate_username_case_insensitive():
    UserFactory(username="charlie")
    birth_date = timezone.localdate() - timedelta(days=365 * 20)

    with pytest.raises(DomainError) as exc_info:
        register_user(
            username="CHARLIE",
            email="charlie2@example.com",
            password=DEFAULT_PASSWORD,
            name="Charlie Two",
            birth_date=birth_date,
        )
    assert exc_info.value.code == "username_already_registered"


def test_register_user_duplicate_email_case_insensitive():
    UserFactory(email="david@example.com")
    birth_date = timezone.localdate() - timedelta(days=365 * 20)

    with pytest.raises(DomainError) as exc_info:
        register_user(
            username="david2",
            email="DAVID@EXAMPLE.COM",
            password=DEFAULT_PASSWORD,
            name="David Two",
            birth_date=birth_date,
        )
    assert exc_info.value.code == "email_already_registered"


def test_register_user_invalid_username_format():
    birth_date = timezone.localdate() - timedelta(days=365 * 20)

    with pytest.raises(DomainError) as exc_info:
        register_user(
            username="ab",  # Too short (min 3)
            email="short@example.com",
            password=DEFAULT_PASSWORD,
            name="Short User",
            birth_date=birth_date,
        )
    assert exc_info.value.code == "invalid_username"


def test_register_user_reserved_username():
    birth_date = timezone.localdate() - timedelta(days=365 * 20)

    with pytest.raises(DomainError) as exc_info:
        register_user(
            username="admin",
            email="admin@example.com",
            password=DEFAULT_PASSWORD,
            name="Admin User",
            birth_date=birth_date,
        )
    assert exc_info.value.code == "reserved_username"


def test_register_user_future_birth_date():
    future_date = timezone.localdate() + timedelta(days=1)

    with pytest.raises(DomainError) as exc_info:
        register_user(
            username="future_user",
            email="future@example.com",
            password=DEFAULT_PASSWORD,
            name="Future User",
            birth_date=future_date,
        )
    assert exc_info.value.code == "future_birth_date"


def test_register_user_underage_birth_date():
    underage_date = timezone.localdate() - timedelta(days=365 * 10)

    with pytest.raises(DomainError) as exc_info:
        register_user(
            username="kid_user",
            email="kid@example.com",
            password=DEFAULT_PASSWORD,
            name="Kid User",
            birth_date=underage_date,
        )
    assert exc_info.value.code == "underage"


def test_register_user_weak_password():
    birth_date = timezone.localdate() - timedelta(days=365 * 20)

    with pytest.raises(DomainError) as exc_info:
        register_user(
            username="weak_pass_user",
            email="weak@example.com",
            password="123",
            name="Weak Pass",
            birth_date=birth_date,
        )
    assert exc_info.value.code == "weak_password"


def test_update_profile_success():
    user = UserFactory(name="Old Name", description="Old Desc")
    new_birth_date = timezone.localdate() - timedelta(days=365 * 22)

    updated = update_profile(
        user=user,
        name="New Name",
        description="New Desc",
        birth_date=new_birth_date,
        customization_json={},
    )

    user.refresh_from_db()
    assert updated.name == "New Name"
    assert updated.description == "New Desc"
    assert updated.birth_date == new_birth_date
    assert updated.customization_json == {}


def test_update_profile_validations():
    user = UserFactory()

    with pytest.raises(DomainError) as exc_info:
        update_profile(user=user, name="a" * 51)
    assert exc_info.value.code == "invalid_name"

    with pytest.raises(DomainError) as exc_info:
        update_profile(user=user, description="a" * 251)
    assert exc_info.value.code == "invalid_description"

    with pytest.raises(DomainError) as exc_info:
        update_profile(user=user, birth_date=timezone.localdate() + timedelta(days=1))
    assert exc_info.value.code == "future_birth_date"


def test_delete_account_success():
    user = UserFactory()
    Wallet.objects.create(user=user, soap_balance=50)
    tx = SoapTransaction.objects.create(
        wallet=user.wallet,
        amount=50,
        action_type=ActionType.SIGNUP_GRANT,
        balance_after=50,
        idempotency_key="signup_test",
    )

    # Connections and non-leader membership
    other_user = UserFactory()
    UserConnectionFactory(follower=user, followed=other_user)
    UserConnectionFactory(follower=other_user, followed=user)

    community = CommunityFactory(member_count=5)
    CommunityMemberFactory(community=community, user=user, role=MemberRole.MEMBER)

    delete_account(user=user, password=DEFAULT_PASSWORD)

    user.refresh_from_db()
    community.refresh_from_db()

    # User anonymized
    assert user.username == f"deleted_{user.id}"
    assert user.email == f"deleted_{user.id}@deleted.invalid"
    assert user.name == "Conta excluída"
    assert user.description == ""
    assert user.is_active is False
    assert user.deleted_at is not None
    assert not user.has_usable_password()

    # Community member count decremented and membership deleted
    assert community.member_count == 4
    assert not CommunityMember.objects.filter(user=user).exists()

    # Connections deleted
    assert not user.following_connections.exists()
    assert not user.follower_connections.exists()

    # Wallet and transaction preserved
    wallet = Wallet.objects.get(user=user)
    assert wallet.soap_balance == 50
    assert SoapTransaction.objects.filter(pk=tx.pk).exists()


def test_delete_account_invalid_password():
    user = UserFactory()

    with pytest.raises(DomainError) as exc_info:
        delete_account(user=user, password="WrongPassword123!")
    assert exc_info.value.code == "invalid_password"
    assert exc_info.value.http_status == 400


def test_delete_account_blocked_if_community_leader():
    user = UserFactory()
    community = CommunityFactory(commname="my_bubbles_comm")
    CommunityMemberFactory(community=community, user=user, role=MemberRole.LEADER)

    with pytest.raises(DomainError) as exc_info:
        delete_account(user=user, password=DEFAULT_PASSWORD)

    assert exc_info.value.code == "must_transfer_leadership"
    assert exc_info.value.http_status == 409
    assert "my_bubbles_comm" in exc_info.value.extra["communities"]
