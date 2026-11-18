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


class SuspendUserInputSerializer(serializers.Serializer):
    duration_hours = serializers.IntegerField(min_value=1, default=24)
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
