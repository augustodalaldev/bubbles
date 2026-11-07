from rest_framework import serializers

from apps.accounts.serializers import PublicUserSerializer

from .models import Letter


class LetterSerializer(serializers.ModelSerializer):
    sender = PublicUserSerializer(read_only=True)
    recipient = PublicUserSerializer(read_only=True)
    is_read = serializers.BooleanField(read_only=True)

    class Meta:
        model = Letter
        fields = [
            "id",
            "sender",
            "recipient",
            "reply_to",
            "text",
            "image",
            "sent_at",
            "read_at",
            "is_read",
        ]
        read_only_fields = fields


class LetterCreateSerializer(serializers.Serializer):
    recipient_username = serializers.CharField(required=True)
    text = serializers.CharField(max_length=5000, required=True, allow_blank=False)
    reply_to_id = serializers.IntegerField(required=False, allow_null=True, default=None)
    image = serializers.ImageField(required=False, allow_null=True, default=None)
