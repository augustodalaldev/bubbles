import shutil
import tempfile
from pathlib import Path

import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def _clear_cache():
    """EconomySettings (and throttles) live in the process-wide cache; isolate every test."""
    cache.clear()
    yield
    cache.clear()


def _is_throwaway_media_root(path) -> bool:
    """True only for a folder inside the system temp directory (never the real `media/`)."""
    root = Path(path).resolve()
    return (
        root != Path(tempfile.gettempdir()).resolve()
        and Path(tempfile.gettempdir()).resolve() in root.parents
    )


def pytest_sessionstart(session):
    """Refuse to run against a real media folder: tests write and delete files."""
    from django.conf import settings

    if not _is_throwaway_media_root(settings.MEDIA_ROOT):
        pytest.exit(
            f"MEDIA_ROOT ({settings.MEDIA_ROOT}) is not a temporary folder. Run the tests with the "
            "test settings (unset DJANGO_SETTINGS_MODULE); the demo/dev media would be deleted.",
            returncode=2,
        )


@pytest.fixture(autouse=True, scope="session")
def _remove_test_media_root():
    yield
    from django.conf import settings

    if _is_throwaway_media_root(settings.MEDIA_ROOT):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
