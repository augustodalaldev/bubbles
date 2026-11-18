import logging
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.core.exceptions import DomainError
from apps.core.locks import advisory_lock
from apps.economy.exceptions import InsufficientSoap
from apps.economy.models import (
    CREDIT_ACTION_TYPES,
    DEBIT_ACTION_TYPES,
    ActionType,
    EconomySettings,
    SoapTransaction,
    Wallet,
)


def ensure_user_wallet(user: Any) -> Wallet:
    """Return the user's wallet, creating it with the configured passive rate if missing."""
    wallet, _ = Wallet.objects.get_or_create(
        user=user,
        defaults={
            "soap_balance": 0,
            "passive_earn_rate": EconomySettings.load().default_passive_earn_rate,
        },
    )
    return wallet


def ensure_community_wallet(community: Any) -> Wallet:
    """Return the community's wallet, creating an empty one if missing."""
    wallet, _ = Wallet.objects.get_or_create(community=community, defaults={"soap_balance": 0})
    return wallet


logger = logging.getLogger(__name__)


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


def debit_bubblegram(
    wallet: Wallet,
    cost: int,
) -> SoapTransaction:
    """Debit soap from a wallet to publish a bubblegram (cost is burned)."""
    return debit(wallet, cost, action_type=ActionType.DEBIT_BUBBLEGRAM)


def debit_bubblepop(
    wallet: Wallet,
    cost: int,
) -> SoapTransaction:
    """Debit soap from a wallet to publish a bubblepop (cost is burned)."""
    return debit(wallet, cost, action_type=ActionType.DEBIT_BUBBLEPOP)


def distribute_passive_soap(*, now: datetime | None = None) -> int:
    """Distribute passive soap to active users (RF019).

    Invariants:
    1. Only active users seen within the last `passive_interval_minutes` receive soap.
    2. Daily limit (local day) is capped at `passive_daily_cap`.
    3. Ledger rows use ActionType.PASSIVE_EARN.
    4. Idempotent per window: the key `passive:<user>:<local date>:<window>` (window =
       floor(epoch / interval)) means that running this twice in the same period pays once.
    5. Runs are serialized across processes by an advisory lock, so two overlapping runs cannot
       both read the daily total before either has paid.
    6. Each user is paid in its own short transaction; a failure is logged and does not stop
       the others.
    """
    with advisory_lock("distribute_passive_soap"):
        return _distribute_passive_soap(now or timezone.now())


def _distribute_passive_soap(current_time: datetime) -> int:
    User = get_user_model()
    settings_obj = EconomySettings.load()

    interval_mins = settings_obj.passive_interval_minutes
    daily_cap = settings_obj.passive_daily_cap
    default_rate = settings_obj.default_passive_earn_rate

    cutoff = current_time - timedelta(minutes=interval_mins)
    eligible_user_ids = list(
        User.objects.filter(
            is_active=True,
            deleted_at__isnull=True,
            last_seen_at__gte=cutoff,
        )
        .order_by("pk")
        .values_list("pk", flat=True)
    )

    local_now = timezone.localtime(current_time)
    today_start = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
    window_bucket = int(current_time.timestamp() // (interval_mins * 60))
    credited_count = 0

    for user_id in eligible_user_ids:
        idempotency_key = f"passive:{user_id}:{local_now.date().isoformat()}:{window_bucket}"
        try:
            with transaction.atomic():
                user = User.objects.get(pk=user_id)
                wallet = ensure_user_wallet(user)
                rate = (
                    wallet.passive_earn_rate
                    if wallet.passive_earn_rate is not None
                    else default_rate
                )
                if rate <= 0:
                    continue

                if SoapTransaction.objects.filter(idempotency_key=idempotency_key).exists():
                    continue

                today_earned = (
                    SoapTransaction.objects.filter(
                        wallet=wallet,
                        action_type=ActionType.PASSIVE_EARN,
                        created_at__gte=today_start,
                    ).aggregate(total=Sum("amount"))["total"]
                    or 0
                )
                remaining_cap = daily_cap - today_earned
                if remaining_cap <= 0:
                    continue

                credit(
                    wallet,
                    min(rate, remaining_cap),
                    action_type=ActionType.PASSIVE_EARN,
                    idempotency_key=idempotency_key,
                )
                credited_count += 1
        except Exception:  # noqa: BLE001 - one user must not stop the others
            logger.exception("passive soap: failed to pay user %s", user_id)

    return credited_count


@transaction.atomic
def update_economy_settings(*, actor: Any, data: dict[str, Any]) -> EconomySettings:
    """Update system economy parameters (admin only)."""
    if not actor.is_staff:
        raise DomainError(
            "Only staff administrators can update economy settings.",
            code="permission_denied",
            http_status=403,
        )

    settings_obj = EconomySettings.load()
    updatable_fields = [
        "signup_grant",
        "support_cost",
        "author_credit",
        "community_credit",
        "bubblegram_profile_cost",
        "bubblegram_community_cost",
        "bubblepop_hours_per_soap",
        "bubblepop_min_hours",
        "bubblepop_max_hours",
        "founding_cost",
        "default_passive_earn_rate",
        "passive_interval_minutes",
        "passive_daily_cap",
    ]

    for field in updatable_fields:
        if field in data and data[field] is not None:
            setattr(settings_obj, field, data[field])

    settings_obj.updated_by = actor
    settings_obj.full_clean()
    settings_obj.save()
    return settings_obj
