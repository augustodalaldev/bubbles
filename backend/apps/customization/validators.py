"""Validation of catalog metadata and of the user-written profile section.

Catalog items end up in the browser as inline styles, so nothing is free-form: colors are hex,
glows follow one strict pattern, and every type accepts only the keys it knows.
"""

import re
from typing import Any

from django.core.exceptions import ValidationError

HEX_COLOR = re.compile(r"\A#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\Z")
GLOW = re.compile(r"\A0 0 (?:[0-9]|[1-2][0-9])px #(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\Z")
WALLPAPER_FITS = {"cover", "tile"}
BADGE_LABEL_MAX = 24

SECTION_TITLE_MAX = 40
SECTION_TEXT_MAX = 500


def _hex(key: str, value: Any) -> None:
    if not isinstance(value, str) or not HEX_COLOR.match(value):
        raise ValidationError(f"'{key}' must be a hex color like #F465AC.", code="invalid_metadata")


# type -> {key: (validator, required)}
_SPECS: dict[str, dict[str, tuple[str, bool]]] = {
    "AVATAR_FRAME": {"border_color": ("hex", True), "glow": ("glow", False)},
    "PROFILE_THEME": {"primary": ("hex", True), "secondary": ("hex", True)},
    "NAME_COLOR": {"color": ("hex", True)},
    "ACCENT_COLOR": {"color": ("hex", True)},
    "BADGE": {"label": ("label", True), "badge_color": ("hex", False)},
    "WALLPAPER": {"fit": ("fit", False)},
    "SECTION": {},
}


def validate_item_metadata(item_type: str, metadata: Any) -> None:
    """Raise ValidationError unless `metadata` is a well-formed token set for `item_type`."""
    if not isinstance(metadata, dict):
        raise ValidationError("Metadata must be a JSON object.", code="invalid_metadata")
    spec = _SPECS.get(item_type)
    if spec is None:
        # Types without a spec (e.g. CHAT_BUBBLE): scalars only, and *color* keys must be hex.
        for key, value in metadata.items():
            if isinstance(value, dict | list):
                raise ValidationError(f"'{key}' must be a plain value.", code="invalid_metadata")
            if "color" in key.lower():
                _hex(key, value)
        return
    unknown = set(metadata) - set(spec)
    if unknown:
        raise ValidationError(
            f"Unknown metadata key(s) for {item_type}: {sorted(unknown)}", code="invalid_metadata"
        )
    for key, (kind, required) in spec.items():
        if key not in metadata:
            if required:
                raise ValidationError(f"'{key}' is required.", code="invalid_metadata")
            continue
        value = metadata[key]
        if kind == "hex":
            _hex(key, value)
        elif kind == "glow":
            if not isinstance(value, str) or not GLOW.match(value):
                raise ValidationError(
                    f"'{key}' must look like '0 0 12px #7B63FF'.", code="invalid_metadata"
                )
        elif kind == "label":
            if not isinstance(value, str) or not 1 <= len(value.strip()) <= BADGE_LABEL_MAX:
                raise ValidationError(
                    f"'{key}' must have 1 to {BADGE_LABEL_MAX} characters.", code="invalid_metadata"
                )
        elif kind == "fit" and value not in WALLPAPER_FITS:
            raise ValidationError(
                f"'{key}' must be one of {sorted(WALLPAPER_FITS)}.", code="invalid_metadata"
            )


def clean_section(title: Any, text: Any) -> tuple[str, str]:
    """Normalize the profile section: plain text only (React escapes it), bounded lengths."""
    if not isinstance(title, str) or not isinstance(text, str):
        raise ValidationError("Title and text must be strings.", code="invalid_section")
    title, text = title.strip(), text.strip()
    for value in (title, text):
        if any(ord(ch) < 32 and ch not in "\n\t" for ch in value):
            raise ValidationError("Invalid characters.", code="invalid_section")
    if len(title) > SECTION_TITLE_MAX or len(text) > SECTION_TEXT_MAX:
        raise ValidationError("Section too long.", code="invalid_section")
    return title, text
