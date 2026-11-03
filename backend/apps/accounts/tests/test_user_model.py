from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.db import DataError, IntegrityError, transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.accounts.tests.factories import DEFAULT_PASSWORD, UserFactory

pytestmark = pytest.mark.django_db


def raw_user(**overrides) -> User:
    """Unsaved user that bypasses the manager, to hit database constraints directly."""
    fields = {
        "username": "alice",
        "email": "alice@example.com",
        "name": "Alice",
        "birth_date": "2000-01-01",
        "password": "not-a-real-hash",
    }
    return User(**{**fields, **overrides})


class TestManager:
    def test_create_user_normalizes_username_and_email(self):
        user = User.objects.create_user(
            username="  Alice_01 ",
            email="  Alice@Example.COM ",
            password=DEFAULT_PASSWORD,
            name="Alice",
            birth_date="2000-01-01",
        )

        assert user.username == "alice_01"
        assert user.email == "alice@example.com"

    def test_create_user_hashes_password(self):
        user = UserFactory()

        assert user.password != DEFAULT_PASSWORD
        assert user.check_password(DEFAULT_PASSWORD)

    def test_create_user_defaults_to_regular_active_account(self):
        user = UserFactory()

        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser

    @pytest.mark.parametrize("missing", ["username", "email"])
    def test_create_user_requires_username_and_email(self, missing):
        kwargs = {"username": "alice", "email": "alice@example.com", missing: ""}

        with pytest.raises(ValueError):
            User.objects.create_user(password=DEFAULT_PASSWORD, **kwargs)

    def test_create_superuser_sets_flags(self):
        admin = User.objects.create_superuser(
            username="boss",
            email="boss@example.com",
            password=DEFAULT_PASSWORD,
            name="Boss",
            birth_date="1990-01-01",
        )

        assert admin.is_staff
        assert admin.is_superuser

    def test_create_superuser_rejects_non_staff(self):
        with pytest.raises(ValueError):
            User.objects.create_superuser(
                username="boss", email="boss@example.com", password="x", is_staff=False
            )


class TestFieldValidation:
    def test_valid_user_passes_full_clean(self):
        UserFactory.build().full_clean()

    def test_reserved_username_is_rejected(self):
        with pytest.raises(ValidationError) as exc:
            UserFactory.build(username="admin").full_clean()

        assert "username" in exc.value.message_dict

    def test_underage_birth_date_is_rejected(self):
        too_young = timezone.localdate() - timedelta(days=365 * 10)

        with pytest.raises(ValidationError) as exc:
            UserFactory.build(birth_date=too_young).full_clean()

        assert "birth_date" in exc.value.message_dict

    def test_clean_lowercases_email(self):
        user = UserFactory.build(email="Mixed@Example.COM")

        user.full_clean()

        assert user.email == "mixed@example.com"

    def test_duplicate_email_ignoring_case_is_reported_by_full_clean(self):
        UserFactory(email="taken@example.com")

        with pytest.raises(ValidationError) as exc:
            UserFactory.build(email="TAKEN@example.com").full_clean()

        assert "__all__" in exc.value.message_dict or "email" in exc.value.message_dict


class TestDatabaseConstraints:
    def test_username_must_be_unique(self):
        raw_user().save()

        with pytest.raises(IntegrityError, match="username"), transaction.atomic():
            raw_user(email="other@example.com").save()

    def test_email_must_be_unique_ignoring_case(self):
        raw_user().save()

        with pytest.raises(IntegrityError, match="uniq_user_email_ci"), transaction.atomic():
            raw_user(username="bob", email="ALICE@Example.com").save()

    @pytest.mark.parametrize(
        "username",
        ["", "ab", "Alice", "alice smith", "alice@example", "alice\n"],
    )
    def test_invalid_username_is_rejected_by_database(self, username):
        with pytest.raises(IntegrityError, match="chk_user_username_format"):
            with transaction.atomic():
                raw_user(username=username).save()

    def test_username_longer_than_30_characters_is_rejected_by_column_type(self):
        with pytest.raises(DataError), transaction.atomic():
            raw_user(username="a" * 31).save()

    @pytest.mark.parametrize("username", ["abc", "a" * 30, "user_01"])
    def test_valid_username_is_accepted_by_database(self, username):
        raw_user(username=username).save()

        assert User.objects.filter(username=username).exists()
