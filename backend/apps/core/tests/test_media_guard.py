import tempfile
from pathlib import Path

from django.conf import settings

from conftest import _is_throwaway_media_root


def test_tests_run_with_a_temporary_media_root():
    assert str(settings.MEDIA_ROOT).startswith(str(Path(tempfile.gettempdir()).resolve()))
    assert _is_throwaway_media_root(settings.MEDIA_ROOT)


def test_real_media_folders_are_never_treated_as_throwaway():
    assert not _is_throwaway_media_root(settings.BASE_DIR / "media")
    assert not _is_throwaway_media_root(tempfile.gettempdir())  # the temp dir itself
    assert not _is_throwaway_media_root("/home")
