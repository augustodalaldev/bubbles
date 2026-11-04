import pytest
from django.contrib.auth import authenticate
from django.utils import timezone

from apps.accounts.tests.factories import DEFAULT_PASSWORD, UserFactory

pytestmark = pytest.mark.django_db


def test_authenticate_with_username():
    user = UserFactory(username="john_doe")
    authenticated = authenticate(identifier="john_doe", password=DEFAULT_PASSWORD)
    assert authenticated == user


def test_authenticate_with_email_case_insensitive():
    user = UserFactory(email="john@example.com")
    authenticated = authenticate(identifier="JOHN@EXAMPLE.COM", password=DEFAULT_PASSWORD)
    assert authenticated == user


def test_authenticate_wrong_password():
    UserFactory(username="john_doe")
    authenticated = authenticate(identifier="john_doe", password="WrongPassword!")
    assert authenticated is None


def test_authenticate_inactive_user():
    UserFactory(username="inactive_user", is_active=False)
    authenticated = authenticate(identifier="inactive_user", password=DEFAULT_PASSWORD)
    assert authenticated is None


def test_authenticate_deleted_user():
    UserFactory(username="deleted_user", deleted_at=timezone.now(), is_active=False)
    authenticated = authenticate(identifier="deleted_user", password=DEFAULT_PASSWORD)
    assert authenticated is None
