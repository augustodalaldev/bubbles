from django.conf import settings
from django.db import models
from django.utils import timezone


class CustomizationType(models.TextChoices):
    AVATAR_FRAME = "AVATAR_FRAME", "Avatar Frame"
    PROFILE_THEME = "PROFILE_THEME", "Profile Theme"
    CHAT_BUBBLE = "CHAT_BUBBLE", "Chat Bubble"
    BADGE = "BADGE", "Badge"
    NAME_COLOR = "NAME_COLOR", "Name Color"


class CustomizationItem(models.Model):
    """Catalog of customization items available for purchase with soap."""

    name = models.CharField(max_length=100)
    code = models.SlugField(max_length=100, unique=True)
    item_type = models.CharField(
        max_length=50,
        choices=CustomizationType.choices,
        db_index=True,
    )
    description = models.TextField(blank=True, default="")
    price = models.PositiveIntegerField(
        default=0,
        help_text="Cost in soap (0 for free/starter items).",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Design tokens and styling metadata consumed by the frontend.",
    )
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ["item_type", "price", "name"]
        indexes = [
            models.Index(fields=["item_type", "is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_item_type_display()}) - {self.price} soap"


class UserInventoryItem(models.Model):
    """Relationship model representing items owned by a user."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="inventory_items",
    )
    item = models.ForeignKey(
        CustomizationItem,
        on_delete=models.PROTECT,
        related_name="user_holdings",
    )
    acquired_at = models.DateTimeField(default=timezone.now, editable=False)
    transaction = models.ForeignKey(
        "economy.SoapTransaction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    class Meta:
        ordering = ["-acquired_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "item"],
                name="uniq_user_inventory_item",
            ),
        ]

    def __str__(self):
        return f"{self.user.username} owns {self.item.code}"
