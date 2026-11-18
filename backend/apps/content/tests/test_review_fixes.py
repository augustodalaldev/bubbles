from datetime import timedelta
from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import UserStatus
from apps.accounts.tests.factories import UserFactory
from apps.content.services import create_bubblepop
from apps.content.tests.factories import BubblepopFactory
from apps.core.exceptions import DomainError
from apps.economy.models import EconomySettings, Wallet

pytestmark = pytest.mark.django_db


def png(name="pop.png"):
    buffer = BytesIO()
    Image.new("RGB", (20, 20), "blue").save(buffer, "PNG")
    return SimpleUploadedFile(name, buffer.getvalue())


def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_suspended_user_cannot_publish_bubblepop_and_is_not_charged():
    user = UserFactory(status=UserStatus.SUSPENDED, suspended_until=None)
    Wallet.objects.create(user=user, soap_balance=20)

    with pytest.raises(DomainError) as exc:
        create_bubblepop(author=user, image=png(), duration_hours=4)

    assert exc.value.code == "account_suspended"
    user.wallet.refresh_from_db()
    assert user.wallet.soap_balance == 20


def test_bubblepop_api_honours_raised_max_hours_from_settings():
    settings_obj = EconomySettings.load()
    settings_obj.bubblepop_max_hours = 72
    settings_obj.save()
    user = UserFactory()
    Wallet.objects.create(user=user, soap_balance=50)

    response = auth_client(user).post(
        "/api/v1/bubblepops/", {"image": png(), "duration_hours": 60}, format="multipart"
    )

    assert response.status_code == status.HTTP_201_CREATED


def test_bubblepop_api_rejects_duration_above_settings_max():
    user = UserFactory()
    Wallet.objects.create(user=user, soap_balance=50)

    response = auth_client(user).post(
        "/api/v1/bubblepops/", {"image": png(), "duration_hours": 49}, format="multipart"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"]["code"] == "invalid_duration"


def test_expired_bubblepop_detail_is_not_found_even_before_cleanup():
    now = timezone.now()
    pop = BubblepopFactory(
        created_at=now - timedelta(hours=2), expires_at=now - timedelta(minutes=1)
    )
    response = auth_client(UserFactory()).get(f"/api/v1/bubblepops/{pop.id}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["error"]["code"] == "bubblepop_not_found"


def test_active_bubblepop_detail_still_readable():
    pop = BubblepopFactory()
    response = auth_client(UserFactory()).get(f"/api/v1/bubblepops/{pop.id}/")
    assert response.status_code == status.HTTP_200_OK
