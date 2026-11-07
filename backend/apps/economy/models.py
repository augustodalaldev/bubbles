from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

from apps.core.exceptions import DomainError


class ActionType(models.TextChoices):
    # Interaction supports
    DEBIT_INTERACTION = "DEBIT_INTERACTION", "Debit interaction"
    CREDIT_AUTHOR = "CREDIT_AUTHOR", "Credit author"
    CREDIT_COMMUNITY = "CREDIT_COMMUNITY", "Credit community"
    # Passive earning
    PASSIVE_EARN = "PASSIVE_EARN", "Passive earn"
    # Additions
    SIGNUP_GRANT = "SIGNUP_GRANT", "Signup grant"
    DEBIT_FOUNDING = "DEBIT_FOUNDING", "Debit founding"
    CREDIT_FOUNDING = "CREDIT_FOUNDING", "Credit founding"
    SPEND_CUSTOMIZATION = "SPEND_CUSTOMIZATION", "Spend customization"
    ADMIN_ADJUSTMENT = "ADMIN_ADJUSTMENT", "Admin adjustment"
    DEBIT_BUBBLEGRAM = "DEBIT_BUBBLEGRAM", "Debit bubblegram"
    DEBIT_BUBBLEPOP = "DEBIT_BUBBLEPOP", "Debit bubblepop"


DEBIT_ACTION_TYPES = [
    ActionType.DEBIT_INTERACTION,
    ActionType.DEBIT_FOUNDING,
    ActionType.SPEND_CUSTOMIZATION,
    ActionType.DEBIT_BUBBLEGRAM,
    ActionType.DEBIT_BUBBLEPOP,
]

CREDIT_ACTION_TYPES = [
    ActionType.CREDIT_AUTHOR,
    ActionType.CREDIT_COMMUNITY,
    ActionType.PASSIVE_EARN,
    ActionType.SIGNUP_GRANT,
    ActionType.CREDIT_FOUNDING,
]


class EconomySettings(models.Model):
    """Singleton storing tunable economic parameters (RF018).

    Guaranteed single row by DB constraint (id=1). Cached with short TTL.
    """

    CACHE_KEY = "economy_settings"

    signup_grant = models.PositiveIntegerField(default=20)
    support_cost = models.PositiveIntegerField(default=1)
    author_credit = models.PositiveIntegerField(default=1)
    community_credit = models.PositiveIntegerField(default=1)
    bubblegram_profile_cost = models.PositiveIntegerField(default=10)
    bubblegram_community_cost = models.PositiveIntegerField(default=10)
    bubblepop_hours_per_soap = models.PositiveIntegerField(default=4)
    bubblepop_min_hours = models.PositiveIntegerField(default=1)
    bubblepop_max_hours = models.PositiveIntegerField(default=48)
    founding_cost = models.PositiveIntegerField(default=300)
    default_passive_earn_rate = models.PositiveIntegerField(default=5)
    passive_interval_minutes = models.PositiveIntegerField(default=5)
    passive_daily_cap = models.PositiveIntegerField(default=15)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "economy settings"
        verbose_name_plural = "economy settings"
        constraints = [
            models.CheckConstraint(
                condition=Q(id=1),
                name="chk_economy_settings_singleton",
            ),
            models.CheckConstraint(
                condition=Q(bubblepop_min_hours__lte=F("bubblepop_max_hours")),
                name="chk_economy_bubblepop_hours_range",
            ),
            models.CheckConstraint(
                condition=Q(bubblepop_hours_per_soap__gt=0),
                name="chk_economy_bubblepop_rate_positive",
            ),
            models.CheckConstraint(
                condition=Q(passive_interval_minutes__gt=0),
                name="chk_economy_passive_interval_positive",
            ),
        ]

    def __str__(self):
        return "Economy Settings"

    def save(self, *args, **kwargs):
        self.id = 1
        super().save(*args, **kwargs)
        cache.set(self.CACHE_KEY, self, timeout=60)

    def delete(self, *args, **kwargs):
        raise DomainError("EconomySettings singleton cannot be deleted.")

    @classmethod
    def load(cls) -> "EconomySettings":
        cached = cache.get(cls.CACHE_KEY)
        if cached is not None:
            return cached
        instance, _ = cls.objects.get_or_create(id=1)
        cache.set(cls.CACHE_KEY, instance, timeout=60)
        return instance


class Wallet(models.Model):
    """Soap wallet. Exactly one owner: either a user or a community."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="wallet",
    )
    community = models.OneToOneField(
        "communities.Community",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="wallet",
    )
    soap_balance = models.PositiveIntegerField(default=0)
    passive_earn_rate = models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    (Q(user__isnull=False) & Q(community__isnull=True))
                    | (Q(user__isnull=True) & Q(community__isnull=False))
                ),
                name="chk_wallet_exactly_one_owner",
            ),
            models.CheckConstraint(
                condition=Q(community__isnull=True) | Q(passive_earn_rate__isnull=True),
                name="chk_wallet_passive_rate_users_only",
            ),
        ]

    def __str__(self):
        owner_name = "unassigned"
        if self.user_id:
            owner_name = f"user:{self.user_id}"
        elif self.community_id:
            owner_name = f"community:{self.community_id}"
        return f"Wallet({owner_name}: {self.soap_balance} soap)"

    def clean(self):
        super().clean()
        has_user = self.user_id is not None or self.user is not None
        has_community = self.community_id is not None or self.community is not None
        if has_user == has_community:
            raise ValidationError(
                "A wallet must belong to either a user or a community, not both or neither."
            )
        if has_community and self.passive_earn_rate is not None:
            raise ValidationError("Community wallets cannot have a passive earn rate.")

    @property
    def owner(self):
        return self.user or self.community

    @property
    def is_user_wallet(self) -> bool:
        return self.user_id is not None

    @property
    def is_community_wallet(self) -> bool:
        return self.community_id is not None


class SoapTransaction(models.Model):
    """Append-only ledger of soap movements."""

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.PROTECT,
        related_name="transactions",
    )
    amount = models.IntegerField()
    action_type = models.CharField(max_length=30, choices=ActionType.choices)
    balance_after = models.PositiveIntegerField()
    idempotency_key = models.CharField(max_length=100, null=True, blank=True, unique=True)
    bubblegram_support = models.ForeignKey(
        "content.BubblegramSupport",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )
    comment_support = models.ForeignKey(
        "content.CommentSupport",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        indexes = [
            models.Index(fields=["wallet", "-created_at"], name="idx_tx_wallet_created"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    (Q(action_type__in=DEBIT_ACTION_TYPES) & Q(amount__lt=0))
                    | (Q(action_type__in=CREDIT_ACTION_TYPES) & Q(amount__gt=0))
                    | (Q(action_type=ActionType.ADMIN_ADJUSTMENT) & ~Q(amount=0))
                ),
                name="chk_tx_amount_sign",
            ),
            models.CheckConstraint(
                condition=~(Q(bubblegram_support__isnull=False) & Q(comment_support__isnull=False)),
                name="chk_tx_single_origin",
            ),
        ]

    def __str__(self):
        return f"Tx({self.wallet_id}, {self.action_type}, {self.amount:+d})"

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise DomainError("SoapTransaction is append-only and cannot be modified.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise DomainError("SoapTransaction is append-only and cannot be deleted.")

    def clean(self):
        super().clean()
        if self.bubblegram_support_id and self.comment_support_id:
            raise ValidationError(
                "A transaction cannot reference both a bubblegram support and a comment support."
            )
