import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.content.models import Comment
from apps.content.tests.factories import BubblegramFactory, CommentFactory

pytestmark = pytest.mark.django_db


def test_top_level_comment_creation():
    comment = CommentFactory()

    assert comment.pk is not None
    assert comment.parent is None
    assert comment.soap_count == 0
    assert "Comment(" in str(comment)


def test_threaded_reply_creation():
    parent = CommentFactory()
    reply = CommentFactory(bubblegram=parent.bubblegram, parent=parent)

    assert reply.parent == parent
    assert reply.bubblegram == parent.bubblegram
    assert parent.replies.get() == reply


def test_clean_rejects_parent_from_different_bubblegram():
    post1 = BubblegramFactory()
    post2 = BubblegramFactory()

    parent = CommentFactory(bubblegram=post1)
    invalid_reply = CommentFactory.build(bubblegram=post2, parent=parent)

    with pytest.raises(ValidationError, match="same bubblegram"):
        invalid_reply.full_clean()


def test_clean_rejects_self_parent():
    comment = CommentFactory()
    comment.parent = comment

    with pytest.raises(ValidationError, match="own parent"):
        comment.full_clean()


class TestDatabaseConstraints:
    def test_database_rejects_self_parent(self):
        comment = CommentFactory()

        with pytest.raises(IntegrityError, match="chk_comment_no_self_parent"):
            with transaction.atomic():
                Comment.objects.filter(pk=comment.pk).update(parent=comment)
