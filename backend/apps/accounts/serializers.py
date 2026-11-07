from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.economy.models import SoapTransaction

User = get_user_model()


class RegisterInputSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    name = serializers.CharField(max_length=50)
    birth_date = serializers.DateField()
    description = serializers.CharField(
        max_length=250, required=False, allow_blank=True, default=""
    )
    profile_photo = serializers.ImageField(required=False, allow_null=True, default=None)


class LoginInputSerializer(serializers.Serializer):
    identifier = serializers.CharField(help_text="Username or email address")
    password = serializers.CharField(write_only=True)


class RefreshTokenInputSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=False, allow_blank=True, default="")


class CurrentUserSerializer(serializers.ModelSerializer):
    soap_balance = serializers.SerializerMethodField()
    wallet = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "name",
            "birth_date",
            "description",
            "profile_photo",
            "customization_json",
            "created_at",
            "soap_balance",
            "wallet",
        ]
        read_only_fields = fields

    def get_soap_balance(self, obj: User) -> int:
        wallet = getattr(obj, "wallet", None)
        return wallet.soap_balance if wallet else 0

    def get_wallet(self, obj: User) -> dict | None:
        wallet = getattr(obj, "wallet", None)
        if not wallet:
            return None
        return {
            "soap_balance": wallet.soap_balance,
            "passive_earn_rate": wallet.passive_earn_rate,
        }


class UpdateProfileSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50, required=False)
    description = serializers.CharField(max_length=250, required=False, allow_blank=True)
    birth_date = serializers.DateField(required=False)
    profile_photo = serializers.ImageField(required=False, allow_null=True)
    customization_json = serializers.JSONField(required=False)


class DeleteAccountSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)


class PublicUserSerializer(serializers.ModelSerializer):
    """Public profile representation.

    Invariant: Never leak private fields (email, birth_date, wallet, soap_balance).
    """

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "name",
            "description",
            "profile_photo",
            "customization_json",
            "is_active",
            "created_at",
        ]
        read_only_fields = fields


class SoapTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoapTransaction
        fields = [
            "id",
            "amount",
            "action_type",
            "balance_after",
            "created_at",
            "bubblegram_support_id",
            "comment_support_id",
        ]
        read_only_fields = fields


class AuthResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    user = CurrentUserSerializer()
