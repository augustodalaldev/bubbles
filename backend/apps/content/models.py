from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

from apps.core.uploads import UploadTo


class BubblegramType(models.TextChoices):
    TEXT = "TEXT", "Text"
    MEDIA = "MEDIA", "Media"


class Bubblegram(models.Model):
    """A permanent post.

    Lives either on the author's personal profile (`community = NULL`)
    or inside a community (`community != NULL`).
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bubblegrams",
    )
    community = models.ForeignKey(
        "communities.Community",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="bubblegrams",
    )
    text = models.TextField(max_length=2000, blank=True)
    type = models.CharField(
        max_length=10,
        choices=BubblegramType.choices,
        default=BubblegramType.TEXT,
    )
    # Cached counter of supports. Updated via F() in the same transaction as support creation.
    soap_count = models.PositiveIntegerField(default=0)
    published_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        indexes = [
            models.Index(
                fields=["community", "-published_at"],
                name="idx_bubblegram_community_pub",
            ),
            models.Index(fields=["user", "-published_at"], name="idx_bubblegram_user_pub"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(~Q(type=BubblegramType.TEXT) | ~Q(text="")),
                name="chk_bubblegram_text_required_if_text_type",
            ),
        ]

    def __str__(self):
        target = f"c/{self.community.commname}" if self.community_id else f"u/{self.user.username}"
        return f"Bubblegram({self.id} on {target})"

    def clean(self):
        super().clean()
        if self.type == BubblegramType.TEXT and not self.text.strip():
            raise ValidationError({"text": "Text is required for TEXT bubblegrams."})

    @property
    def is_personal(self) -> bool:
        return self.community_id is None

    @property
    def is_community(self) -> bool:
        return self.community_id is not None


class BubblegramMedia(models.Model):
    """An image attached to a MEDIA bubblegram."""

    bubblegram = models.ForeignKey(
        Bubblegram,
        on_delete=models.CASCADE,
        related_name="media",
    )
    media = models.ImageField(upload_to=UploadTo("bubblegrams"))
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(
                fields=["bubblegram", "position"],
                name="uniq_bubblegram_media_pos",
            ),
        ]

    def __str__(self):
        return f"Media({self.bubblegram_id}, pos={self.position})"


class Bubblepop(models.Model):
    """An ephemeral story on the user's personal profile only."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bubblepops",
    )
    image = models.ImageField(upload_to=UploadTo("bubblepops"))
    description = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    expires_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=["expires_at"], name="idx_pop_expires_at"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(expires_at__gt=F("created_at")),
                name="chk_pop_expires_after_created",
            ),
        ]

    def __str__(self):
        return f"Bubblepop({self.id} by {self.user_id})"

    def clean(self):
        super().clean()
        if self.expires_at and self.created_at and self.expires_at <= self.created_at:
            raise ValidationError({"expires_at": "expires_at must be strictly after created_at."})

    @property
    def is_expired(self) -> bool:
        return self.expires_at <= timezone.now()


class Comment(models.Model):
    """A comment on a bubblegram. Can be threaded (replies)."""

    bubblegram = models.ForeignKey(
        Bubblegram,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
    )
    text = models.TextField(max_length=1000)
    # Cached counter of supports.
    soap_count = models.PositiveIntegerField(default=0)
    published_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        indexes = [
            models.Index(fields=["bubblegram", "published_at"], name="idx_comment_bubblegram_pub"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=~Q(parent=F("id")),
                name="chk_comment_no_self_parent",
            ),
        ]

    def __str__(self):
        return f"Comment({self.id} on post {self.bubblegram_id})"

    def clean(self):
        super().clean()
        if self.parent_id:
            if self.parent.bubblegram_id != self.bubblegram_id:
                raise ValidationError("Parent comment must belong to the same bubblegram.")
            if self.id and self.parent_id == self.id:
                raise ValidationError("A comment cannot be its own parent.")


class BubblegramSupport(models.Model):
    """A soap support given to a bubblegram by a donor."""

    bubblegram = models.ForeignKey(
        Bubblegram,
        on_delete=models.CASCADE,
        related_name="supports",
    )
    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bubblegram_supports",
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["bubblegram", "donor"],
                name="uniq_support_bubblegram_donor",
            ),
        ]

    def __str__(self):
        return f"BubblegramSupport(donor={self.donor_id}, post={self.bubblegram_id})"

    def clean(self):
        super().clean()
        if self.donor_id and self.bubblegram_id and self.donor_id == self.bubblegram.user_id:
            raise ValidationError("Users cannot support their own bubblegram.")


class CommentSupport(models.Model):
    """A soap support given to a comment by a donor."""

    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="supports",
    )
    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comment_supports",
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["comment", "donor"],
                name="uniq_support_comment_donor",
            ),
        ]

    def __str__(self):
        return f"CommentSupport(donor={self.donor_id}, comment={self.comment_id})"

    def clean(self):
        super().clean()
        if self.donor_id and self.comment_id and self.donor_id == self.comment.user_id:
            raise ValidationError("Users cannot support their own comment.")
