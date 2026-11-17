from rest_framework import serializers

from apps.accounts.serializers import PublicUserSerializer
from apps.core.fields import SafeImageField

from .models import Community, CommunityMember, MemberState
from .selectors import compute_community_permissions, get_community_membership


class CommunityCreateSerializer(serializers.Serializer):
    commname = serializers.CharField(max_length=21)
    name = serializers.CharField(max_length=60)
    description = serializers.CharField(
        max_length=500, required=False, allow_blank=True, default=""
    )
    guidelines = serializers.CharField(
        max_length=2000, required=False, allow_blank=True, default=""
    )
    community_photo = SafeImageField(required=False, allow_null=True, default=None)
    banner_photo = SafeImageField(required=False, allow_null=True, default=None)
    customization_json = serializers.JSONField(required=False, default=dict)


class CommunityUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=60, required=False)
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)
    community_photo = SafeImageField(required=False, allow_null=True)
    banner_photo = SafeImageField(required=False, allow_null=True)
    customization_json = serializers.JSONField(required=False)


class CommunityGuidelinesSerializer(serializers.Serializer):
    guidelines = serializers.CharField(max_length=2000, required=True, allow_blank=True)


class MyMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityMember
        fields = ["role", "current_state", "joined_at"]
        read_only_fields = fields


class CommunityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = [
            "id",
            "commname",
            "name",
            "description",
            "community_photo",
            "banner_photo",
            "customization_json",
            "member_count",
            "created_at",
            "is_archived",
        ]
        read_only_fields = fields


class CommunityDetailSerializer(serializers.ModelSerializer):
    my_membership = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = Community
        fields = [
            "id",
            "commname",
            "name",
            "description",
            "guidelines",
            "community_photo",
            "banner_photo",
            "customization_json",
            "member_count",
            "created_at",
            "is_archived",
            "archived_at",
            "my_membership",
            "permissions",
        ]
        read_only_fields = fields

    def get_my_membership(self, obj: Community) -> dict | None:
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return None
        membership = get_community_membership(community=obj, user=request.user)
        if not membership:
            return None
        return MyMembershipSerializer(membership).data

    def get_permissions(self, obj: Community) -> dict:
        request = self.context.get("request")
        user = request.user if request else None
        return compute_community_permissions(community=obj, user=user)


class CommunityMemberSerializer(serializers.ModelSerializer):
    user = PublicUserSerializer(read_only=True)

    class Meta:
        model = CommunityMember
        fields = ["id", "user", "role", "current_state", "joined_at"]
        read_only_fields = fields


class MemberModerateSerializer(serializers.Serializer):
    current_state = serializers.ChoiceField(choices=MemberState.choices)


class TransferLeadershipSerializer(serializers.Serializer):
    new_leader_username = serializers.CharField(required=True)


class CommunityWalletSerializer(serializers.Serializer):
    soap_balance = serializers.IntegerField(read_only=True)
