from rest_framework import serializers

from apps.accounts.serializers import PublicUserSerializer
from apps.core.fields import SafeImageField

from .models import Letter

EXCERPT_LENGTH = 140


class LetterReplySummarySerializer(serializers.Serializer):
    """Which letter this one answers: enough to show it and link to it."""

    id = serializers.IntegerField()
    sender = PublicUserSerializer()
    excerpt = serializers.CharField()
    sent_at = serializers.DateTimeField()


class LetterSerializer(serializers.ModelSerializer):
    sender = PublicUserSerializer(read_only=True)
    recipient = PublicUserSerializer(read_only=True)
    is_read = serializers.BooleanField(read_only=True)
    reply_to_summary = serializers.SerializerMethodField()
    reply_id = serializers.SerializerMethodField()

    class Meta:
        model = Letter
        fields = [
            "id",
            "sender",
            "recipient",
            "reply_to",
            "reply_to_summary",
            "reply_id",
            "text",
            "image",
            "sent_at",
            "read_at",
            "is_read",
        ]
        read_only_fields = fields

    def get_reply_to_summary(self, obj: Letter) -> dict | None:
        """The answered letter. Safe to expose: a reply goes from the original's recipient back to
        its sender, so whoever can see the reply was a party of the original too."""
        original = obj.reply_to
        if original is None:
            return None
        text = original.text
        excerpt = text if len(text) <= EXCERPT_LENGTH else text[:EXCERPT_LENGTH].rstrip() + "…"
        return LetterReplySummarySerializer(
            {
                "id": original.id,
                "sender": original.sender,
                "excerpt": excerpt,
                "sent_at": original.sent_at,
            },
            context=self.context,
        ).data

    def get_reply_id(self, obj: Letter) -> int | None:
        """The letter that answers this one, when it has been answered."""
        return getattr(obj, "reply_id", None)


class LetterCreateSerializer(serializers.Serializer):
    recipient_username = serializers.CharField(required=True)
    text = serializers.CharField(max_length=5000, required=True, allow_blank=False)
    reply_to_id = serializers.IntegerField(required=False, allow_null=True, default=None)
    image = SafeImageField(required=False, allow_null=True, default=None)
