from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from apps.core.exceptions import DomainError
from apps.economy.models import SoapTransaction, Wallet
from apps.economy.services import ensure_user_wallet

from .models import UserConnection

User = get_user_model()


def get_user_by_username(*, username: str) -> User:
    """Retrieve an active public user profile by username.

    Raises 404 DomainError if user does not exist or has been deleted/deactivated.
    """
    clean_username = username.strip().lower()
    user = User.objects.filter(
        username__iexact=clean_username,
        is_active=True,
        deleted_at__isnull=True,
    ).first()
    if not user:
        raise DomainError("User not found.", code="user_not_found", http_status=404)
    return user


def get_user_wallet_and_transactions(*, user: User) -> tuple[Wallet, QuerySet[SoapTransaction]]:
    """Retrieve user's wallet and ordered ledger transactions.

    If the user has no wallet (e.g. legacy/test instance), initializes one.
    """
    if not hasattr(user, "wallet") or user.wallet is None:
        wallet = ensure_user_wallet(user)
    else:
        wallet = user.wallet

    transactions = (
        wallet.transactions.all()
        .select_related("bubblegram_support", "comment_support")
        .order_by("-created_at", "-id")
    )
    return wallet, transactions


def list_user_followers(*, user: User) -> QuerySet[UserConnection]:
    """List connections where target user is followed by active users."""
    return (
        UserConnection.objects.select_related("follower")
        .filter(followed=user, follower__is_active=True)
        .order_by("-created_at")
    )


def list_user_following(*, user: User) -> QuerySet[UserConnection]:
    """List connections where target user follows active users."""
    return (
        UserConnection.objects.select_related("followed")
        .filter(follower=user, followed__is_active=True)
        .order_by("-created_at")
    )
