from io import BytesIO

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.tests.factories import UserFactory
from apps.content.models import Bubblegram
from apps.core.uploads import MAX_IMAGE_UPLOAD_BYTES, validate_image_upload
from apps.economy.models import Wallet
from config.settings import base as base_settings

pytestmark = pytest.mark.django_db


def image_file(name="photo.png", fmt="PNG", size=(20, 20)):
    buffer = BytesIO()
    Image.new("RGB", size, "red").save(buffer, fmt)
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="application/octet-stream")


def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.parametrize(
    ("name", "fmt"),
    [("a.png", "PNG"), ("a.jpg", "JPEG"), ("a.jpeg", "JPEG"), ("a.webp", "WEBP"), ("a.gif", "GIF")],
)
def test_validator_accepts_allowed_formats(name, fmt):
    validate_image_upload(image_file(name, fmt))


def test_validator_rewinds_file_after_reading():
    file = image_file()
    validate_image_upload(file)
    assert file.tell() == 0


def test_validator_rejects_non_image():
    with pytest.raises(ValidationError) as exc:
        validate_image_upload(SimpleUploadedFile("evil.png", b"<html>not an image</html>"))
    assert exc.value.code == "invalid_image"


def test_validator_rejects_format_outside_whitelist():
    with pytest.raises(ValidationError) as exc:
        validate_image_upload(image_file("a.png", "BMP"))
    assert exc.value.code == "invalid_image_type"


def test_validator_rejects_non_image_extension():
    with pytest.raises(ValidationError) as exc:
        validate_image_upload(image_file("a.html", "PNG"))
    assert exc.value.code == "invalid_image_type"


def test_validator_rejects_oversized_file():
    file = image_file()
    file.size = MAX_IMAGE_UPLOAD_BYTES + 1
    with pytest.raises(ValidationError) as exc:
        validate_image_upload(file)
    assert exc.value.code == "image_too_large"


def test_bubblegram_api_rejects_unvalidated_images_key():
    """Files under the legacy `images` key must not bypass validation."""
    user = UserFactory()
    Wallet.objects.create(user=user, soap_balance=50)
    payload = {"type": "MEDIA", "text": "x", "images": SimpleUploadedFile("x.html", b"<script>")}
    response = auth_client(user).post("/api/v1/bubblegrams/", data=payload, format="multipart")
    # No media was accepted, so the MEDIA post is refused and nothing is stored.
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not Bubblegram.objects.exists()


def test_bubblegram_api_rejects_non_image_media_file():
    user = UserFactory()
    Wallet.objects.create(user=user, soap_balance=50)
    payload = {
        "type": "MEDIA",
        "media_files": SimpleUploadedFile("x.png", b"<svg onload=alert(1)>"),
    }
    response = auth_client(user).post("/api/v1/bubblegrams/", data=payload, format="multipart")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_bubblegram_api_rejects_oversized_media_file(monkeypatch):
    monkeypatch.setattr("apps.core.uploads.MAX_IMAGE_UPLOAD_BYTES", 100)
    user = UserFactory()
    Wallet.objects.create(user=user, soap_balance=50)
    payload = {"type": "MEDIA", "media_files": image_file(size=(200, 200))}
    response = auth_client(user).post("/api/v1/bubblegrams/", data=payload, format="multipart")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_bubblegram_api_accepts_valid_image():
    user = UserFactory()
    Wallet.objects.create(user=user, soap_balance=50)
    payload = {"type": "MEDIA", "media_files": image_file()}
    response = auth_client(user).post("/api/v1/bubblegrams/", data=payload, format="multipart")
    assert response.status_code == status.HTTP_201_CREATED


def test_user_throttle_allows_realistic_daily_usage():
    rate = base_settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["user"]
    assert int(rate.split("/")[0]) >= 5000
