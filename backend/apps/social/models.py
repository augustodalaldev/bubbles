from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

from apps.core.exceptions import DomainError
from apps.core.uploads import UploadTo


class Letter(models.Model):
    """A letter sent between users. Mail, not chat.

    Letters are immutable after sending; only `read_at` can be set upon opening.
    """

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_letters",
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_letters",
    )
    reply_to = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="replies",
    )
    text = models.TextField(max_length=5000)
    image = models.ImageField(upload_to=UploadTo("letters"), null=True, blank=True)
    sent_at = models.DateTimeField(default=timezone.now, editable=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["recipient", "-sent_at"], name="idx_letter_recipient_sent"),
            models.Index(fields=["sender", "-sent_at"], name="idx_letter_sender_sent"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=~Q(sender=F("recipient")),
                name="chk_letter_not_to_self",
            ),
            models.UniqueConstraint(
                fields=["reply_to"],
                condition=Q(reply_to__isnull=False),
                name="uniq_one_reply_per_letter",
            ),
        ]

    def __str__(self):
        return f"Letter({self.sender_id} -> {self.recipient_id})"

    def save(self, *args, **kwargs):
        if self.pk is not None:
            # Enforce immutability: only read_at may be updated after sending
            old = Letter.objects.get(pk=self.pk)
            old_image = old.image.name if old.image else None
            new_image = self.image.name if self.image else None
            if (
                old.text != self.text
                or old_image != new_image
                or old.sender_id != self.sender_id
                or old.recipient_id != self.recipient_id
                or old.reply_to_id != self.reply_to_id
            ):
                raise DomainError("Letters are immutable after sending.")
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.sender_id and self.recipient_id and self.sender_id == self.recipient_id:
            raise ValidationError("You cannot send a letter to yourself.")

        if self.reply_to_id:
            # A reply must come from the original letter's recipient and go to the original sender
            original = self.reply_to
            if original.recipient_id != self.sender_id or original.sender_id != self.recipient_id:
                raise ValidationError(
                    "Replies must be sent back to the author of the original letter."
                )

    @property
    def is_read(self) -> bool:
        return self.read_at is not None
