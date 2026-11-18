from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.core.uploads import UploadTo, validate_image_upload

from .validators import validate_item_metadata


class CustomizationType(models.TextChoices):
    AVATAR_FRAME = "AVATAR_FRAME", "Avatar Frame"
    PROFILE_THEME = "PROFILE_THEME", "Profile Theme"
    CHAT_BUBBLE = "CHAT_BUBBLE", "Chat Bubble"
    BADGE = "BADGE", "Badge"
    NAME_COLOR = "NAME_COLOR", "Name Color"
    WALLPAPER = "WALLPAPER", "Wallpaper"
    ACCENT_COLOR = "ACCENT_COLOR", "Accent Color"
    SECTION = "SECTION", "Profile Section"


class CustomizationScope(models.TextChoices):
    USER = "USER", "User profiles only"
    COMMUNITY = "COMMUNITY", "Communities only"
    BOTH = "BOTH", "Users and communities"


class CustomizationItem(models.Model):
    """Catalog of customization items available for purchase with soap."""

    name = models.CharField(max_length=100)
    code = models.SlugField(max_length=100, unique=True)
    item_type = models.CharField(
        max_length=50,
        choices=CustomizationType.choices,
        db_index=True,
    )
    scope = models.CharField(
        max_length=20,
        choices=CustomizationScope.choices,
        default=CustomizationScope.USER,
        db_index=True,
        help_text="Who may buy this item: user profiles, communities or both.",
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
    # Wallpapers only: uploaded by staff in the admin, never by users.
    image = models.ImageField(
        upload_to=UploadTo("customization"),
        blank=True,
        validators=[validate_image_upload],
        help_text="Required for wallpapers (JPEG/PNG/WebP/GIF, up to 10 MB).",
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

    def clean(self):
        super().clean()
        try:
            validate_item_metadata(self.item_type, self.metadata)
        except ValidationError as exc:
            raise ValidationError({"metadata": exc.messages}) from exc
        if self.item_type == CustomizationType.WALLPAPER and not self.image:
            raise ValidationError({"image": "A wallpaper needs an image."})


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
    acquired_at = models.DateTimeField(default=timezone.now, editable=False, db_index=True)
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


class CommunityInventoryItem(models.Model):
    """Item bought by a community with its own soap wallet (RF014)."""

    community = models.ForeignKey(
        "communities.Community",
        on_delete=models.CASCADE,
        related_name="inventory_items",
    )
    item = models.ForeignKey(
        CustomizationItem,
        on_delete=models.PROTECT,
        related_name="community_holdings",
    )
    purchased_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        help_text="Leader/admin who spent the community's soap.",
    )
    acquired_at = models.DateTimeField(default=timezone.now, editable=False, db_index=True)
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
                fields=["community", "item"],
                name="uniq_community_inventory_item",
            ),
        ]

    def __str__(self):
        return f"{self.community.commname} owns {self.item.code}"
