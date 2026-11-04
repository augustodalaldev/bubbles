from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import MaxLengthValidator
from django.db import models
from django.db.models import F, Q
from django.db.models.functions import Lower
from django.utils import timezone

from apps.core.uploads import UploadTo

from .managers import UserManager
from .validators import (
    USERNAME_PATTERN,
    validate_birth_date,
    validate_username_format,
    validate_username_not_reserved,
)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[validate_username_format, validate_username_not_reserved],
        error_messages={"unique": "This username is not available."},
    )
    email = models.EmailField()
    name = models.CharField(max_length=50)
    birth_date = models.DateField(validators=[validate_birth_date])
    description = models.TextField(
        max_length=250,
        blank=True,
        validators=[MaxLengthValidator(250)],
    )
    profile_photo = models.ImageField(upload_to=UploadTo("profile_photos"), blank=True)
    customization_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email", "name", "birth_date"]

    class Meta:
        constraints = [
            models.UniqueConstraint(Lower("email"), name="uniq_user_email_ci"),
            models.CheckConstraint(
                condition=Q(username__regex=USERNAME_PATTERN),
                name="chk_user_username_format",
            ),
        ]

    def __str__(self):
        return self.username

    def clean(self):
        super().clean()
        if self.email:
            self.email = self.email.strip().lower()


class UserConnection(models.Model):
    """A follow: `follower` follows `followed`. Directed and immediate (no approval)."""

    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following_connections",
    )
    followed = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="follower_connections",
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "followed"],
                name="uniq_connection_follower_followed",
            ),
            models.CheckConstraint(
                condition=~Q(follower=F("followed")),
                name="chk_no_self_follow",
            ),
        ]
        indexes = [
            models.Index(fields=["followed", "-created_at"], name="idx_connection_followed"),
        ]

    def __str__(self):
        return f"{self.follower_id} -> {self.followed_id}"
