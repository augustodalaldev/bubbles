from rest_framework import serializers

from .uploads import validate_image_upload


class SafeImageField(serializers.ImageField):
    """ImageField restricted to JPEG/PNG/WebP/GIF files of at most 10 MB."""

    default_validators = [*serializers.ImageField.default_validators, validate_image_upload]
