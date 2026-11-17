import uuid
from pathlib import PurePath

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from PIL import Image

MAX_IMAGE_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB per file (docs/frontend/PLAN.md section 6)
ALLOWED_IMAGE_FORMATS = {
    "JPEG": {".jpg", ".jpeg"},
    "PNG": {".png"},
    "WEBP": {".webp"},
    "GIF": {".gif"},
}


def validate_image_upload(file) -> None:
    """Reject files that are too large or are not JPEG/PNG/WebP/GIF.

    The real format is read by Pillow (never trusting the client's content type). The
    extension is kept in the stored file name, so it must also be an image extension.
    """
    if file.size > MAX_IMAGE_UPLOAD_BYTES:
        raise ValidationError("Image must be at most 10 MB.", code="image_too_large")
    extension = PurePath(file.name or "").suffix.lower()
    try:
        position = file.tell()
    except (AttributeError, OSError):
        position = 0
    try:
        with Image.open(file) as image:
            image_format = image.format
    except Exception as exc:
        raise ValidationError("Upload a valid image.", code="invalid_image") from exc
    finally:
        file.seek(position)
    allowed_extensions = set().union(*ALLOWED_IMAGE_FORMATS.values())
    if image_format not in ALLOWED_IMAGE_FORMATS or extension not in allowed_extensions:
        raise ValidationError(
            "Only JPEG, PNG, WebP and GIF images are accepted.", code="invalid_image_type"
        )


@deconstructible
class UploadTo:
    """`upload_to` callable that stores files as `<folder>/<random uuid><ext>`.

    A class (not a closure) so migrations can serialize it. The original filename
    is discarded: it may be hostile (path tricks) or leak personal information.
    """

    def __init__(self, folder: str):
        self.folder = folder

    def __call__(self, instance, filename: str) -> str:
        extension = PurePath(filename).suffix.lower()
        return f"{self.folder}/{uuid.uuid4().hex}{extension}"
