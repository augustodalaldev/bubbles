import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.accounts.tests.factories import UserFactory
from apps.content.tests.factories import (
    BubblegramFactory,
    BubblegramSupportFactory,
    CommentFactory,
    CommentSupportFactory,
)

pytestmark = pytest.mark.django_db


def test_bubblegram_support_creation():
    support = BubblegramSupportFactory()

    assert support.pk is not None
    assert "BubblegramSupport(" in str(support)


def test_comment_support_creation():
    support = CommentSupportFactory()

    assert support.pk is not None
    assert "CommentSupport(" in str(support)


def test_clean_rejects_self_support_on_bubblegram():
    user = UserFactory()
    post = BubblegramFactory(user=user)
    support = BubblegramSupportFactory.build(bubblegram=post, donor=user)

    with pytest.raises(ValidationError, match="cannot support their own"):
        support.full_clean()


def test_clean_rejects_self_support_on_comment():
    user = UserFactory()
    comment = CommentFactory(user=user)
    support = CommentSupportFactory.build(comment=comment, donor=user)

    with pytest.raises(ValidationError, match="cannot support their own"):
        support.full_clean()


class TestDatabaseConstraints:
    def test_donor_cannot_support_same_bubblegram_twice(self):
        support = BubblegramSupportFactory()

        with pytest.raises(IntegrityError, match="uniq_support_bubblegram_donor"):
            with transaction.atomic():
                BubblegramSupportFactory(bubblegram=support.bubblegram, donor=support.donor)

    def test_donor_cannot_support_same_comment_twice(self):
        support = CommentSupportFactory()

        with pytest.raises(IntegrityError, match="uniq_support_comment_donor"):
            with transaction.atomic():
                CommentSupportFactory(comment=support.comment, donor=support.donor)
