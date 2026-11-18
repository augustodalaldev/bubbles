from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.core.fields import SafeImageField
from apps.economy.models import SoapTransaction

from .models import UserConnection

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
    profile_photo = SafeImageField(required=False, allow_null=True, default=None)


class LoginInputSerializer(serializers.Serializer):
    identifier = serializers.CharField(help_text="Username or email address")
    password = serializers.CharField(write_only=True)


class RefreshTokenInputSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=False, allow_blank=True, default="")


def profile_section(user: User) -> dict | None:
    """The customizable section, shown only while a SECTION item is equipped and it has content."""
    equipped = (user.customization_json or {}).get("section")
    if not isinstance(equipped, dict) or not (user.section_title or user.section_text):
        return None
    return {"title": user.section_title, "text": user.section_text}


class CurrentUserSerializer(serializers.ModelSerializer):
    soap_balance = serializers.SerializerMethodField()
    wallet = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    section = serializers.SerializerMethodField()

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
            "is_staff",
            "status",
            "is_suspended",
            "suspended_until",
            "moderation_reason",
            "soap_balance",
            "wallet",
            "followers_count",
            "following_count",
            "section",
        ]
        read_only_fields = fields

    def get_section(self, obj: User) -> dict | None:
        return profile_section(obj)

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

    def get_followers_count(self, obj: User) -> int:
        return obj.follower_connections.filter(follower__is_active=True).count()

    def get_following_count(self, obj: User) -> int:
        return obj.following_connections.filter(followed__is_active=True).count()


class UpdateProfileSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50, required=False)
    description = serializers.CharField(max_length=250, required=False, allow_blank=True)
    birth_date = serializers.DateField(required=False)
    profile_photo = SafeImageField(required=False, allow_null=True)
    remove_profile_photo = serializers.BooleanField(required=False)
    customization_json = serializers.JSONField(required=False)


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)


class ChangeEmailSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    new_email = serializers.EmailField(max_length=254)


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


class UserProfileDetailSerializer(PublicUserSerializer):
    """Full public profile representation with social stats and relationship flags."""

    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    is_followed_by = serializers.SerializerMethodField()

    section = serializers.SerializerMethodField()

    def get_section(self, obj: User) -> dict | None:
        return profile_section(obj)

    class Meta(PublicUserSerializer.Meta):
        fields = PublicUserSerializer.Meta.fields + [
            "section",
            "followers_count",
            "following_count",
            "is_following",
            "is_followed_by",
        ]

    def get_followers_count(self, obj: User) -> int:
        return obj.follower_connections.filter(follower__is_active=True).count()

    def get_following_count(self, obj: User) -> int:
        return obj.following_connections.filter(followed__is_active=True).count()

    def get_is_following(self, obj: User) -> bool:
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return False
        if request.user.id == obj.id:
            return False
        return UserConnection.objects.filter(follower=request.user, followed=obj).exists()

    def get_is_followed_by(self, obj: User) -> bool:
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return False
        if request.user.id == obj.id:
            return False
        return UserConnection.objects.filter(follower=obj, followed=request.user).exists()


class FollowerItemSerializer(serializers.ModelSerializer):
    user = PublicUserSerializer(source="follower", read_only=True)

    class Meta:
        model = UserConnection
        fields = ["id", "user", "created_at"]
        read_only_fields = fields


class FollowingItemSerializer(serializers.ModelSerializer):
    user = PublicUserSerializer(source="followed", read_only=True)

    class Meta:
        model = UserConnection
        fields = ["id", "user", "created_at"]
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
