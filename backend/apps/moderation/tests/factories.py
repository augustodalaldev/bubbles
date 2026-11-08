import factory
from django.utils import timezone

from apps.accounts.tests.factories import UserFactory
from apps.moderation.models import (
    AuditAction,
    AuditLog,
    Report,
    ReportReason,
    ReportStatus,
    ReportTargetType,
)


class ReportFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Report

    reporter = factory.SubFactory(UserFactory)
    target_type = ReportTargetType.USER
    target_id = "1"
    reason = ReportReason.SPAM
    description = factory.Faker("sentence")
    status = ReportStatus.PENDING
    reviewed_by = None
    reviewed_at = None
    resolution_notes = ""
    created_at = factory.LazyFunction(timezone.now)


class AuditLogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AuditLog

    actor = factory.SubFactory(UserFactory, is_staff=True)
    action = AuditAction.USER_SUSPEND
    target_type = "USER"
    target_id = "1"
    reason = "Test audit reason"
    metadata = factory.LazyFunction(dict)
    created_at = factory.LazyFunction(timezone.now)
