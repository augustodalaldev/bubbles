from rest_framework import serializers

from apps.accounts.serializers import PublicUserSerializer
from apps.moderation.models import (
    AuditLog,
    Report,
    ReportStatus,
)


class ReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = [
            "target_type",
            "target_id",
            "reason",
            "description",
        ]


class ReportSerializer(serializers.ModelSerializer):
    reporter = PublicUserSerializer(read_only=True)
    reviewed_by_username = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            "id",
            "reporter",
            "target_type",
            "target_id",
            "reason",
            "description",
            "status",
            "reviewed_by_username",
            "reviewed_at",
            "resolution_notes",
            "created_at",
        ]
        read_only_fields = fields

    def get_reviewed_by_username(self, obj: Report) -> str | None:
        return obj.reviewed_by.username if obj.reviewed_by_id else None


class ReportReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[ReportStatus.INVESTIGATING, ReportStatus.RESOLVED, ReportStatus.DISMISSED]
    )
    resolution_notes = serializers.CharField(
        max_length=1000,
        required=False,
        allow_blank=True,
        default="",
    )


class AuditLogSerializer(serializers.ModelSerializer):
    actor_username = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "actor_username",
            "action",
            "target_type",
            "target_id",
            "reason",
            "metadata",
            "created_at",
        ]
        read_only_fields = fields

    def get_actor_username(self, obj: AuditLog) -> str | None:
        return obj.actor.username if obj.actor_id else None


class AdminUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    name = serializers.CharField()
    email = serializers.CharField()
    profile_photo = serializers.SerializerMethodField()
    is_staff = serializers.BooleanField()
    status = serializers.SerializerMethodField()
    suspended_until = serializers.DateTimeField()
    moderation_reason = serializers.CharField()
    created_at = serializers.DateTimeField()

    def get_status(self, obj) -> str:
        """ACTIVE / SUSPENDED / BANNED, treating an expired suspension as active."""
        if obj.is_banned:
            return "BANNED"
        return "SUSPENDED" if obj.is_suspended else "ACTIVE"

    def get_profile_photo(self, obj) -> str | None:
        return obj.profile_photo.url if obj.profile_photo else None


class AdminCommunitySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    commname = serializers.CharField()
    name = serializers.CharField()
    member_count = serializers.IntegerField()
    is_archived = serializers.BooleanField()
    status = serializers.SerializerMethodField()
    suspended_until = serializers.DateTimeField()
    blocked_at = serializers.DateTimeField()
    moderation_reason = serializers.CharField()
    created_at = serializers.DateTimeField()

    def get_status(self, obj) -> str:
        return obj.moderation_status or "ACTIVE"


class SuspendUserInputSerializer(serializers.Serializer):
    duration_hours = serializers.IntegerField(min_value=1, max_value=24 * 365, default=24)
    reason = serializers.CharField(max_length=500, required=True)


class ReasonRequiredInputSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=500, required=True)


class AdminSoapAdjustmentInputSerializer(serializers.Serializer):
    amount = serializers.IntegerField()
    reason = serializers.CharField(max_length=500, required=True)

    def validate_amount(self, value):
        if value == 0:
            raise serializers.ValidationError("O valor do ajuste não pode ser zero.")
        return value
