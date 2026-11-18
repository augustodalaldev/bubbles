from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.core.uploads import UploadTo

from .validators import (
    COMMNAME_PATTERN,
    validate_commname_format,
    validate_commname_not_reserved,
)


class MemberRole(models.TextChoices):
    MEMBER = "MEMBER"
    COMM_ADMIN = "COMM_ADMIN"
    LEADER = "LEADER"


class MemberState(models.TextChoices):
    ACTIVE = "ACTIVE"
    SILENCED = "SILENCED"
    BANNED = "BANNED"


class Community(models.Model):
    commname = models.CharField(
        max_length=21,
        unique=True,
        validators=[validate_commname_format, validate_commname_not_reserved],
        error_messages={"unique": "This community handle is not available."},
    )
    name = models.CharField(max_length=60)
    description = models.TextField(max_length=500, blank=True)
    guidelines = models.TextField(max_length=2000, blank=True)
    community_photo = models.ImageField(upload_to=UploadTo("community_photos"), blank=True)
    banner_photo = models.ImageField(upload_to=UploadTo("community_banners"), blank=True)
    customization_json = models.JSONField(default=dict, blank=True)
    # Cached counter of non-banned members. Only changed with F() expressions in the
    # same transaction as the join/leave/ban that causes it.
    member_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    blocked_at = models.DateTimeField(null=True, blank=True, db_index=True)
    # Soft delete by the leader: the row stays (ledger and content keep their references) but the
    # community is hidden everywhere and its handle is freed (see `delete_community`).
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    # Temporary suspension by staff (a ban is `blocked_at`). Both make the community read-only
    # and hidden from lists; `moderation_reason` is shown to its members.
    suspended_until = models.DateTimeField(null=True, blank=True)
    moderation_reason = models.CharField(max_length=500, blank=True, default="")

    class Meta:
        verbose_name_plural = "communities"
        constraints = [
            models.CheckConstraint(
                condition=Q(commname__regex=COMMNAME_PATTERN),
                name="chk_community_commname_format",
            ),
        ]

    def __str__(self):
        return self.commname

    @property
    def is_archived(self) -> bool:
        return self.archived_at is not None

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    @property
    def is_blocked(self) -> bool:
        return self.blocked_at is not None

    @property
    def is_suspended(self) -> bool:
        return self.suspended_until is not None and self.suspended_until > timezone.now()

    @property
    def is_moderated(self) -> bool:
        """Banned (blocked) or suspended: read-only and hidden from lists."""
        return self.is_blocked or self.is_suspended

    @property
    def moderation_status(self) -> str | None:
        if self.is_blocked:
            return "BANNED"
        if self.is_suspended:
            return "SUSPENDED"
        return None


def not_moderated_q(prefix: str = "") -> Q:
    """Filter for communities that are neither banned nor under an active suspension."""
    return Q(**{f"{prefix}blocked_at__isnull": True}) & (
        Q(**{f"{prefix}suspended_until__isnull": True})
        | Q(**{f"{prefix}suspended_until__lte": timezone.now()})
    )


class CommunityMember(models.Model):
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="community_memberships",
    )
    role = models.CharField(max_length=10, choices=MemberRole.choices, default=MemberRole.MEMBER)
    current_state = models.CharField(
        max_length=10,
        choices=MemberState.choices,
        default=MemberState.ACTIVE,
    )
    joined_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["community", "user"],
                name="uniq_member_community_user",
            ),
            models.UniqueConstraint(
                fields=["community"],
                condition=Q(role=MemberRole.LEADER),
                name="uniq_one_leader_per_community",
            ),
            models.CheckConstraint(
                condition=~Q(role=MemberRole.LEADER) | Q(current_state=MemberState.ACTIVE),
                name="chk_leader_must_be_active",
            ),
        ]

    def __str__(self):
        return f"{self.user_id} in {self.community_id} ({self.role}, {self.current_state})"
