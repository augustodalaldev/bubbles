import pytest
from django.db import IntegrityError, transaction

from apps.core.exceptions import DomainError
from apps.economy.models import ActionType, SoapTransaction
from apps.economy.tests.factories import SoapTransactionFactory, WalletFactory

pytestmark = pytest.mark.django_db


def test_soap_transaction_creation():
    tx = SoapTransactionFactory()

    assert tx.pk is not None
    assert tx.amount == 20
    assert tx.balance_after == 20
    assert tx.created_at is not None
    assert "Tx(" in str(tx)


def test_transaction_is_immutable_save_raises():
    tx = SoapTransactionFactory()

    with pytest.raises(DomainError, match="cannot be modified"):
        tx.amount = 30
        tx.save()


def test_transaction_is_append_only_delete_raises():
    tx = SoapTransactionFactory()

    with pytest.raises(DomainError, match="append-only"):
        tx.delete()


class TestDatabaseConstraints:
    def test_database_rejects_debit_with_positive_amount(self):
        wallet = WalletFactory()

        with pytest.raises(IntegrityError, match="chk_tx_amount_sign"):
            with transaction.atomic():
                SoapTransaction.objects.create(
                    wallet=wallet,
                    amount=10,  # invalid: debits must be negative
                    action_type=ActionType.DEBIT_INTERACTION,
                    balance_after=10,
                )

    def test_database_rejects_credit_with_negative_amount(self):
        wallet = WalletFactory()

        with pytest.raises(IntegrityError, match="chk_tx_amount_sign"):
            with transaction.atomic():
                SoapTransaction.objects.create(
                    wallet=wallet,
                    amount=-10,  # invalid: credits must be positive
                    action_type=ActionType.CREDIT_AUTHOR,
                    balance_after=10,
                )

    def test_database_rejects_zero_amount(self):
        wallet = WalletFactory()

        with pytest.raises(IntegrityError, match="chk_tx_amount_sign"):
            with transaction.atomic():
                SoapTransaction.objects.create(
                    wallet=wallet,
                    amount=0,  # invalid: amount cannot be 0
                    action_type=ActionType.PASSIVE_EARN,
                    balance_after=10,
                )

    def test_admin_adjustment_allows_positive_and_negative(self):
        wallet = WalletFactory(soap_balance=50)

        tx_credit = SoapTransaction.objects.create(
            wallet=wallet,
            amount=10,
            action_type=ActionType.ADMIN_ADJUSTMENT,
            balance_after=60,
        )
        assert tx_credit.pk is not None

        tx_debit = SoapTransaction.objects.create(
            wallet=wallet,
            amount=-20,
            action_type=ActionType.ADMIN_ADJUSTMENT,
            balance_after=40,
        )
        assert tx_debit.pk is not None

    def test_idempotency_key_must_be_unique(self):
        wallet = WalletFactory()
        SoapTransaction.objects.create(
            wallet=wallet,
            amount=20,
            action_type=ActionType.SIGNUP_GRANT,
            balance_after=20,
            idempotency_key="unique_signup_key_1",
        )

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                SoapTransaction.objects.create(
                    wallet=wallet,
                    amount=20,
                    action_type=ActionType.SIGNUP_GRANT,
                    balance_after=40,
                    idempotency_key="unique_signup_key_1",
                )
