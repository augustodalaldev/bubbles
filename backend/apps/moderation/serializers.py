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
    reviewed_by_username = serializers.CharField(source="reviewed_by.username", read_only=True)

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
    actor_username = serializers.CharField(source="actor.username", read_only=True)

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
            raise serializers.ValidationError("Adjustment amount cannot be zero.")
        return value
