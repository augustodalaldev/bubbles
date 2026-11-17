import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def _clear_cache():
    """EconomySettings (and throttles) live in the process-wide cache; isolate every test."""
    cache.clear()
    yield
    cache.clear()
