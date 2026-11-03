from datetime import date, timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.accounts.validators import (
    MINIMUM_AGE,
    calculate_age,
    validate_birth_date,
    validate_username_format,
    validate_username_not_reserved,
)


def years_ago(years: int) -> date:
    today = timezone.localdate()
    try:
        return today.replace(year=today.year - years)
    except ValueError:  # today is Feb 29 and the target year is not a leap year
        return today.replace(year=today.year - years, day=28)


@pytest.mark.parametrize("username", ["abc", "a" * 30, "user_01", "a1_b2_c3"])
def test_valid_usernames_pass_format(username):
    validate_username_format(username)


@pytest.mark.parametrize(
    "username",
    ["", "ab", "a" * 31, "Alice", "alice smith", "alice@example", "ação_x", "alice\n", "al-ice"],
)
def test_invalid_usernames_fail_format(username):
    with pytest.raises(ValidationError):
        validate_username_format(username)


@pytest.mark.parametrize("username", ["admin", "me", "api", "deleted_42", "deleted_whatever"])
def test_reserved_usernames_are_rejected(username):
    with pytest.raises(ValidationError) as exc:
        validate_username_not_reserved(username)

    assert exc.value.code == "reserved_username"


def test_regular_username_is_not_reserved():
    validate_username_not_reserved("augusto")


def test_calculate_age_counts_birthday_only_when_reached():
    assert calculate_age(date(2000, 6, 15), today=date(2020, 6, 14)) == 19
    assert calculate_age(date(2000, 6, 15), today=date(2020, 6, 15)) == 20


def test_birth_date_exactly_at_minimum_age_is_valid():
    validate_birth_date(years_ago(MINIMUM_AGE))


def test_birth_date_one_day_short_of_minimum_age_is_rejected():
    with pytest.raises(ValidationError) as exc:
        validate_birth_date(years_ago(MINIMUM_AGE) + timedelta(days=1))

    assert exc.value.code == "underage"


def test_future_birth_date_is_rejected():
    with pytest.raises(ValidationError) as exc:
        validate_birth_date(timezone.localdate() + timedelta(days=1))

    assert exc.value.code == "future_birth_date"
