from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from django.db import transaction

from apps.core.exceptions import DomainError
from apps.economy.exceptions import InsufficientSoap
from apps.economy.models import (
    CREDIT_ACTION_TYPES,
    DEBIT_ACTION_TYPES,
    ActionType,
    SoapTransaction,
    Wallet,
)


@dataclass(frozen=True)
class Movement:
    wallet: Wallet
    amount: int
    action_type: str
    idempotency_key: str | None = None


def _normalize_movement(item: Any) -> Movement:
    if isinstance(item, Movement):
        return item
    if isinstance(item, (list, tuple)):
        if len(item) == 3:
            return Movement(wallet=item[0], amount=item[1], action_type=item[2])
        if len(item) == 4:
            return Movement(
                wallet=item[0],
                amount=item[1],
                action_type=item[2],
                idempotency_key=item[3],
            )
    raise DomainError(f"Invalid movement specification: {item!r}")


@transaction.atomic
def apply_movements(
    movements: Sequence[Movement | tuple[Wallet, int, str] | tuple[Wallet, int, str, str | None]],
    *,
    origin: Any = None,
) -> list[SoapTransaction]:
    """Execute several soap movements as one atomic unit.

    Invariants:
    1. Runs inside `transaction.atomic()`.
    2. Locks all involved wallets with `select_for_update()` ordered by PK (deadlock prevention).
    3. Validates integer non-zero amounts and sufficient balance for debits.
    4. Writes `SoapTransaction` rows with `balance_after`.
    5. Honors idempotency keys: returns existing transactions if already processed.
    """
    if not movements:
        return []

    normalized = [_normalize_movement(m) for m in movements]

    # Validate movements before locking
    for m in normalized:
        if not isinstance(m.wallet, Wallet) or m.wallet.pk is None:
            raise DomainError("Each movement must reference a saved Wallet instance.")
        if type(m.amount) is not int or m.amount == 0:
            raise DomainError("Movement amount must be a non-zero integer.")
        if m.action_type not in ActionType.values:
            raise DomainError(f"Unknown action_type: {m.action_type}")
        if m.action_type in DEBIT_ACTION_TYPES and m.amount > 0:
            raise DomainError(f"Action {m.action_type} is a debit and requires a negative amount.")
        if m.action_type in CREDIT_ACTION_TYPES and m.amount < 0:
            raise DomainError(f"Action {m.action_type} is a credit and requires a positive amount.")

    # Check for idempotency: if any movement with an idempotency_key already exists,
    # find existing transactions.
    idempotency_keys = [m.idempotency_key for m in normalized if m.idempotency_key]
    if idempotency_keys:
        existing = list(
            SoapTransaction.objects.filter(idempotency_key__in=idempotency_keys).order_by("pk")
        )
        if len(existing) == len(idempotency_keys):
            return existing

    # Lock involved wallets in primary-key order to avoid deadlocks
    wallet_pks = sorted({m.wallet.pk for m in normalized})
    locked_wallets = {
        w.pk: w for w in Wallet.objects.select_for_update().filter(pk__in=wallet_pks).order_by("pk")
    }

    if len(locked_wallets) != len(wallet_pks):
        raise DomainError("One or more wallets could not be found.")

    # Calculate net balance changes and validate solvency
    created_transactions: list[SoapTransaction] = []
    wallets_to_save: set[Wallet] = set()

    for m in normalized:
        locked_wallet = locked_wallets[m.wallet.pk]
        new_balance = locked_wallet.soap_balance + m.amount

        if new_balance < 0:
            raise InsufficientSoap(
                f"Insufficient soap balance for wallet {locked_wallet.pk}. "
                f"Required: {-m.amount}, available: {locked_wallet.soap_balance}.",
                cost=-m.amount,
                balance=locked_wallet.soap_balance,
            )

        locked_wallet.soap_balance = new_balance
        wallets_to_save.add(locked_wallet)

        tx = SoapTransaction(
            wallet=locked_wallet,
            amount=m.amount,
            action_type=m.action_type,
            balance_after=new_balance,
            idempotency_key=m.idempotency_key,
        )
        if origin is not None:
            origin_name = origin.__class__.__name__
            if origin_name == "BubblegramSupport":
                tx.bubblegram_support = origin
            elif origin_name == "CommentSupport":
                tx.comment_support = origin
        created_transactions.append(tx)

    # Persist updated balances and transactions
    for locked_wallet in wallets_to_save:
        locked_wallet.save(update_fields=["soap_balance"])

    for tx in created_transactions:
        tx.save()

    # Sync back in-memory balances for callers holding references
    for m in normalized:
        m.wallet.soap_balance = locked_wallets[m.wallet.pk].soap_balance

    return created_transactions


def credit(
    wallet: Wallet,
    amount: int,
    *,
    action_type: str,
    origin: Any = None,
    idempotency_key: str | None = None,
) -> SoapTransaction:
    """Credit soap to a wallet.

    `amount` must be a positive integer.
    """
    if type(amount) is not int or amount <= 0:
        raise DomainError("Credit amount must be a positive integer.")

    if idempotency_key:
        existing = SoapTransaction.objects.filter(idempotency_key=idempotency_key).first()
        if existing:
            return existing

    movements = [
        Movement(
            wallet=wallet,
            amount=amount,
            action_type=action_type,
            idempotency_key=idempotency_key,
        )
    ]
    return apply_movements(movements, origin=origin)[0]


def debit(
    wallet: Wallet,
    amount: int,
    *,
    action_type: str,
    origin: Any = None,
) -> SoapTransaction:
    """Debit soap from a wallet. Raises InsufficientSoap if balance is insufficient.

    `amount` must be a positive integer (the cost to deduct).
    """
    if type(amount) is not int or amount <= 0:
        raise DomainError("Debit amount must be a positive integer.")

    movements = [
        Movement(
            wallet=wallet,
            amount=-amount,
            action_type=action_type,
        )
    ]
    return apply_movements(movements, origin=origin)[0]


def spend_customization(
    wallet: Wallet,
    cost: int,
) -> SoapTransaction:
    """Debit soap from a wallet to purchase profile or community visual customizations.

    `cost` must be a positive integer.
    """
    return debit(wallet, cost, action_type=ActionType.SPEND_CUSTOMIZATION)
