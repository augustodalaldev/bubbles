import threading

import pytest
from django.db import connection
from django.test import TransactionTestCase

from apps.accounts.tests.factories import UserFactory
from apps.communities.tests.factories import CommunityFactory
from apps.core.exceptions import DomainError
from apps.economy.exceptions import InsufficientSoap
from apps.economy.models import ActionType, SoapTransaction, Wallet
from apps.economy.services import apply_movements, credit, debit
from apps.economy.tests.factories import WalletFactory

pytestmark = pytest.mark.django_db


class TestCreditService:
    def test_credit_increases_wallet_balance_and_records_transaction(self):
        wallet = WalletFactory(soap_balance=10)

        tx = credit(wallet, 20, action_type=ActionType.SIGNUP_GRANT)

        wallet.refresh_from_db()
        assert wallet.soap_balance == 30
        assert tx.pk is not None
        assert tx.wallet == wallet
        assert tx.amount == 20
        assert tx.balance_after == 30
        assert tx.action_type == ActionType.SIGNUP_GRANT

    def test_credit_rejects_negative_or_zero_amount(self):
        wallet = WalletFactory(soap_balance=10)

        with pytest.raises(DomainError, match="positive integer"):
            credit(wallet, 0, action_type=ActionType.SIGNUP_GRANT)

        with pytest.raises(DomainError, match="positive integer"):
            credit(wallet, -5, action_type=ActionType.SIGNUP_GRANT)

    def test_credit_rejects_non_integer_amount(self):
        wallet = WalletFactory(soap_balance=10)

        with pytest.raises(DomainError, match="positive integer"):
            credit(wallet, 5.5, action_type=ActionType.SIGNUP_GRANT)  # type: ignore

    def test_credit_honors_idempotency_key(self):
        wallet = WalletFactory(soap_balance=10)
        key = "idemp_test_signup_1"

        tx1 = credit(wallet, 20, action_type=ActionType.SIGNUP_GRANT, idempotency_key=key)
        wallet.refresh_from_db()
        assert wallet.soap_balance == 30

        # Second call with the same key should return tx1 and NOT credit again
        tx2 = credit(wallet, 20, action_type=ActionType.SIGNUP_GRANT, idempotency_key=key)
        wallet.refresh_from_db()
        assert wallet.soap_balance == 30
        assert tx1.pk == tx2.pk


class TestDebitService:
    def test_debit_decreases_wallet_balance_and_records_negative_amount(self):
        wallet = WalletFactory(soap_balance=50)

        tx = debit(wallet, 20, action_type=ActionType.SPEND_CUSTOMIZATION)

        wallet.refresh_from_db()
        assert wallet.soap_balance == 30
        assert tx.pk is not None
        assert tx.amount == -20
        assert tx.balance_after == 30
        assert tx.action_type == ActionType.SPEND_CUSTOMIZATION

    def test_debit_raises_insufficient_soap_when_balance_too_low(self):
        wallet = WalletFactory(soap_balance=10)

        with pytest.raises(InsufficientSoap) as exc_info:
            debit(wallet, 15, action_type=ActionType.DEBIT_INTERACTION)

        assert exc_info.value.cost == 15
        assert exc_info.value.balance == 10
        wallet.refresh_from_db()
        assert wallet.soap_balance == 10
        assert not SoapTransaction.objects.filter(wallet=wallet).exists()

    def test_debit_rejects_negative_or_zero_amount(self):
        wallet = WalletFactory(soap_balance=50)

        with pytest.raises(DomainError, match="positive integer"):
            debit(wallet, 0, action_type=ActionType.DEBIT_INTERACTION)

        with pytest.raises(DomainError, match="positive integer"):
            debit(wallet, -10, action_type=ActionType.DEBIT_INTERACTION)


class TestApplyMovementsService:
    def test_transfer_between_wallets_is_atomic(self):
        user_wallet = WalletFactory(soap_balance=500)
        community = CommunityFactory()
        comm_wallet = Wallet.objects.create(community=community, soap_balance=0)

        movements = [
            (user_wallet, -300, ActionType.DEBIT_FOUNDING),
            (comm_wallet, 300, ActionType.CREDIT_FOUNDING),
        ]
        txs = apply_movements(movements)

        user_wallet.refresh_from_db()
        comm_wallet.refresh_from_db()

        assert user_wallet.soap_balance == 200
        assert comm_wallet.soap_balance == 300
        assert len(txs) == 2
        assert txs[0].amount == -300
        assert txs[0].balance_after == 200
        assert txs[1].amount == 300
        assert txs[1].balance_after == 300

    def test_transfer_rolls_back_completely_if_debit_fails(self):
        user_wallet = WalletFactory(soap_balance=100)
        community = CommunityFactory()
        comm_wallet = Wallet.objects.create(community=community, soap_balance=0)

        movements = [
            (user_wallet, -300, ActionType.DEBIT_FOUNDING),
            (comm_wallet, 300, ActionType.CREDIT_FOUNDING),
        ]

        with pytest.raises(InsufficientSoap):
            apply_movements(movements)

        user_wallet.refresh_from_db()
        comm_wallet.refresh_from_db()
        assert user_wallet.soap_balance == 100
        assert comm_wallet.soap_balance == 0
        assert not SoapTransaction.objects.filter(wallet__in=[user_wallet, comm_wallet]).exists()

    def test_multiple_movements_on_same_wallet(self):
        wallet = WalletFactory(soap_balance=100)

        movements = [
            (wallet, -20, ActionType.DEBIT_INTERACTION),
            (wallet, -30, ActionType.DEBIT_INTERACTION),
            (wallet, 10, ActionType.PASSIVE_EARN),
        ]
        txs = apply_movements(movements)

        wallet.refresh_from_db()
        assert wallet.soap_balance == 60
        assert len(txs) == 3
        assert [t.balance_after for t in txs] == [80, 50, 60]

    def test_rejects_empty_movements(self):
        assert apply_movements([]) == []

    def test_rejects_invalid_amount_or_sign(self):
        wallet = WalletFactory(soap_balance=100)

        with pytest.raises(DomainError, match="non-zero integer"):
            apply_movements([(wallet, 0, ActionType.PASSIVE_EARN)])

        with pytest.raises(DomainError, match="debit and requires a negative amount"):
            apply_movements([(wallet, 10, ActionType.DEBIT_INTERACTION)])

        with pytest.raises(DomainError, match="credit and requires a positive amount"):
            apply_movements([(wallet, -10, ActionType.CREDIT_AUTHOR)])


class ConcurrencyTestCase(TransactionTestCase):
    """Concurrency test requiring real DB transactions across threads."""

    def test_concurrent_debits_with_balance_for_only_one(self):
        user = UserFactory()
        wallet = Wallet.objects.create(user=user, soap_balance=10)

        results = []
        errors = []

        def worker():
            # Close connection so thread gets its own PostgreSQL connection
            connection.close()
            try:
                tx = debit(wallet, 10, action_type=ActionType.DEBIT_INTERACTION)
                results.append(tx)
            except InsufficientSoap as e:
                errors.append(e)
            finally:
                connection.close()

        t1 = threading.Thread(target=worker)
        t2 = threading.Thread(target=worker)

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        wallet.refresh_from_db()
        assert wallet.soap_balance == 0
        assert len(results) == 1
        assert len(errors) == 1
        assert SoapTransaction.objects.filter(wallet=wallet).count() == 1
