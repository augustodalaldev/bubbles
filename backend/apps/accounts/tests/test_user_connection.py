import pytest
from django.db import IntegrityError, transaction

from apps.accounts.models import UserConnection
from apps.accounts.tests.factories import UserConnectionFactory, UserFactory

pytestmark = pytest.mark.django_db


def test_follow_is_created_between_two_users():
    connection = UserConnectionFactory()

    assert connection.follower_id != connection.followed_id
    assert connection.created_at is not None


def test_cannot_follow_the_same_user_twice():
    alice, bob = UserFactory(), UserFactory()
    UserConnection.objects.create(follower=alice, followed=bob)

    with pytest.raises(IntegrityError, match="uniq_connection_follower_followed"):
        with transaction.atomic():
            UserConnection.objects.create(follower=alice, followed=bob)


def test_cannot_follow_yourself():
    alice = UserFactory()

    with pytest.raises(IntegrityError, match="chk_no_self_follow"):
        with transaction.atomic():
            UserConnection.objects.create(follower=alice, followed=alice)


def test_follow_is_directed_so_both_directions_can_coexist():
    alice, bob = UserFactory(), UserFactory()

    UserConnection.objects.create(follower=alice, followed=bob)
    UserConnection.objects.create(follower=bob, followed=alice)

    assert alice.following_connections.count() == 1
    assert alice.follower_connections.count() == 1


def test_related_names_expose_following_and_followers():
    alice, bob, carol = UserFactory(), UserFactory(), UserFactory()
    UserConnection.objects.create(follower=alice, followed=bob)
    UserConnection.objects.create(follower=carol, followed=bob)

    assert alice.following_connections.get().followed == bob
    assert {c.follower for c in bob.follower_connections.all()} == {alice, carol}
