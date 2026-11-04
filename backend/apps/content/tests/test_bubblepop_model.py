from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.accounts.tests.factories import UserFactory
from apps.content.models import Bubblepop
from apps.content.tests.factories import BubblepopFactory

pytestmark = pytest.mark.django_db


def test_bubblepop_creation_and_expiration_property():
    future = timezone.now() + timedelta(hours=12)
    pop = BubblepopFactory(expires_at=future)

    assert pop.pk is not None
    assert not pop.is_expired
    assert str(pop.user_id) in str(pop)


def test_bubblepop_reports_expired():
    past = timezone.now() - timedelta(minutes=5)
    # create with future, then simulate passage of time by setting expires_at to past
    pop = BubblepopFactory(expires_at=timezone.now() + timedelta(hours=1))
    pop.expires_at = past

    assert pop.is_expired


def test_clean_rejects_expires_at_before_created_at():
    user = UserFactory()
    now = timezone.now()
    pop = Bubblepop(
        user=user,
        image="pop.png",
        created_at=now,
        expires_at=now - timedelta(hours=1),
    )

    with pytest.raises(ValidationError) as exc:
        pop.full_clean()

    assert "expires_at" in exc.value.message_dict


class TestDatabaseConstraints:
    def test_database_rejects_expiration_before_creation(self):
        user = UserFactory()
        now = timezone.now()
        pop = Bubblepop(
            user=user,
            image="pop.png",
            created_at=now,
            expires_at=now - timedelta(minutes=1),
        )

        with pytest.raises(IntegrityError, match="chk_pop_expires_after_created"):
            with transaction.atomic():
                pop.save()
