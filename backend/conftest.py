import shutil

import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def _clear_cache():
    """EconomySettings (and throttles) live in the process-wide cache; isolate every test."""
    cache.clear()
    yield
    cache.clear()


@pytest.fixture(autouse=True, scope="session")
def _remove_test_media_root():
    yield
    from django.conf import settings

    shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
