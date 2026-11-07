from rest_framework import serializers

from apps.accounts.serializers import PublicUserSerializer
from apps.communities.models import Community, CommunityMember, MemberRole, MemberState

from .models import (
    Bubblegram,
    BubblegramMedia,
    BubblegramSupport,
    BubblegramType,
    Bubblepop,
    Comment,
    CommentSupport,
)


class BubblegramMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = BubblegramMedia
        fields = ["id", "media", "position"]
        read_only_fields = fields


class BubblegramCommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = ["id", "commname", "name"]
        read_only_fields = fields


class BubblegramSerializer(serializers.ModelSerializer):
    user = PublicUserSerializer(read_only=True)
    community = BubblegramCommunitySerializer(read_only=True)
    media = BubblegramMediaSerializer(many=True, read_only=True)
    can_delete = serializers.SerializerMethodField()
    is_suggested = serializers.SerializerMethodField()
    suggestion_reason = serializers.SerializerMethodField()

    class Meta:
        model = Bubblegram
        fields = [
            "id",
            "user",
            "community",
            "text",
            "type",
            "soap_count",
            "published_at",
            "media",
            "can_delete",
            "is_suggested",
            "suggestion_reason",
        ]
        read_only_fields = fields

    def get_is_suggested(self, obj: Bubblegram) -> bool:
        return bool(getattr(obj, "is_suggested", False))

    def get_suggestion_reason(self, obj: Bubblegram) -> str | None:
        return getattr(obj, "suggestion_reason", None)

    def get_can_delete(self, obj: Bubblegram) -> bool:
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return False
        user = request.user
        if user.is_staff or obj.user_id == user.id:
            return True
        if obj.community_id:
            cache_attr = f"_comm_member_{obj.community_id}"
            if not hasattr(request, cache_attr):
                membership = CommunityMember.objects.filter(
                    community_id=obj.community_id, user=user
                ).first()
                setattr(request, cache_attr, membership)
            membership = getattr(request, cache_attr)
            if (
                membership
                and membership.current_state == MemberState.ACTIVE
                and membership.role in (MemberRole.COMM_ADMIN, MemberRole.LEADER)
            ):
                return True
        return False


class BubblegramCreateSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=2000, required=False, allow_blank=True, default="")
    type = serializers.ChoiceField(choices=BubblegramType.choices, default=BubblegramType.TEXT)
    commname = serializers.CharField(required=False, allow_null=True, default=None)
    media_files = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        max_length=4,
        default=list,
    )


class CommentSerializer(serializers.ModelSerializer):
    user = PublicUserSerializer(read_only=True)
    can_delete = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "bubblegram",
            "user",
            "parent",
            "text",
            "soap_count",
            "published_at",
            "can_delete",
        ]
        read_only_fields = fields

    def get_can_delete(self, obj: Comment) -> bool:
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return False
        actor = request.user
        if actor.is_staff or obj.user_id == actor.id:
            return True
        if obj.bubblegram.user_id == actor.id:
            return True
        if obj.bubblegram.community_id:
            cache_attr = f"_comm_member_{obj.bubblegram.community_id}"
            if not hasattr(request, cache_attr):
                membership = CommunityMember.objects.filter(
                    community_id=obj.bubblegram.community_id, user=actor
                ).first()
                setattr(request, cache_attr, membership)
            membership = getattr(request, cache_attr)
            if (
                membership
                and membership.current_state == MemberState.ACTIVE
                and membership.role in (MemberRole.COMM_ADMIN, MemberRole.LEADER)
            ):
                return True
        return False


class CommentCreateSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=2000, required=True, allow_blank=False)
    parent_id = serializers.IntegerField(required=False, allow_null=True, default=None)


class BubblegramSupportResponseSerializer(serializers.ModelSerializer):
    soap_count = serializers.IntegerField(source="bubblegram.soap_count", read_only=True)

    class Meta:
        model = BubblegramSupport
        fields = ["id", "bubblegram", "soap_count", "created_at"]
        read_only_fields = fields


class CommentSupportResponseSerializer(serializers.ModelSerializer):
    soap_count = serializers.IntegerField(source="comment.soap_count", read_only=True)

    class Meta:
        model = CommentSupport
        fields = ["id", "comment", "soap_count", "created_at"]
        read_only_fields = fields


class BubblepopSerializer(serializers.ModelSerializer):
    user = PublicUserSerializer(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    can_delete = serializers.SerializerMethodField()

    class Meta:
        model = Bubblepop
        fields = [
            "id",
            "user",
            "image",
            "description",
            "created_at",
            "expires_at",
            "is_expired",
            "can_delete",
        ]
        read_only_fields = fields

    def get_can_delete(self, obj: Bubblepop) -> bool:
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_staff or obj.user_id == request.user.id


class BubblepopCreateSerializer(serializers.Serializer):
    image = serializers.ImageField(required=True)
    duration_hours = serializers.IntegerField(min_value=1, max_value=48, default=24)
    description = serializers.CharField(
        max_length=500, required=False, allow_blank=True, default=""
    )
