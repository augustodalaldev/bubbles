from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

import pytest
from django.db import connection
from django.utils import timezone

from apps.accounts.models import User
from apps.accounts.services import register_user
from apps.accounts.tests.factories import DEFAULT_PASSWORD
from apps.core.exceptions import DomainError

pytestmark = pytest.mark.django_db(transaction=True)


def test_concurrent_signups_duplicate_username_produces_one_account():
    birth_date = timezone.localdate() - timedelta(days=365 * 20)
    username = "concurrent_user"
    email_pattern = "user_{}@example.com"

    def attempt_signup(idx: int):
        connection.close()  # Ensure each thread uses its own DB connection
        try:
            return register_user(
                username=username,
                email=email_pattern.format(idx),
                password=DEFAULT_PASSWORD,
                name=f"User {idx}",
                birth_date=birth_date,
            )
        except DomainError:
            return None
        finally:
            connection.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(attempt_signup, 1), executor.submit(attempt_signup, 2)]
        results = [f.result() for f in futures]

    created = [r for r in results if r is not None]
    assert len(created) == 1
    assert User.objects.filter(username=username).count() == 1


def test_concurrent_signups_duplicate_email_produces_one_account():
    birth_date = timezone.localdate() - timedelta(days=365 * 20)
    email = "shared_email@example.com"

    def attempt_signup(idx: int):
        connection.close()
        try:
            return register_user(
                username=f"unique_user_{idx}",
                email=email,
                password=DEFAULT_PASSWORD,
                name=f"User {idx}",
                birth_date=birth_date,
            )
        except DomainError:
            return None
        finally:
            connection.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(attempt_signup, 1), executor.submit(attempt_signup, 2)]
        results = [f.result() for f in futures]

    created = [r for r in results if r is not None]
    assert len(created) == 1
    assert User.objects.filter(email=email).count() == 1
