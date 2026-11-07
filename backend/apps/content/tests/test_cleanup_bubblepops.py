from datetime import timedelta
from io import StringIO

import pytest
from django.core.files.storage import default_storage
from django.core.management import call_command
from django.utils import timezone

from apps.content.models import Bubblepop
from apps.content.services import cleanup_expired_bubblepops
from apps.content.tests.factories import BubblepopFactory

pytestmark = pytest.mark.django_db


def test_cleanup_expired_bubblepops_removes_expired_only():
    now = timezone.now()

    # Active pop: expires in 2 hours
    active_pop = BubblepopFactory(
        created_at=now - timedelta(hours=2),
        expires_at=now + timedelta(hours=2),
    )
    active_image_name = active_pop.image.name
    assert default_storage.exists(active_image_name)

    # Expired pop 1: created 10 hours ago, expired 2 hours ago
    expired_pop1 = BubblepopFactory(
        created_at=now - timedelta(hours=10),
        expires_at=now - timedelta(hours=2),
    )
    img1_name = expired_pop1.image.name
    assert default_storage.exists(img1_name)

    # Expired pop 2: created 5 hours ago, expired 1 hour ago
    expired_pop2 = BubblepopFactory(
        created_at=now - timedelta(hours=5),
        expires_at=now - timedelta(hours=1),
    )
    img2_name = expired_pop2.image.name
    assert default_storage.exists(img2_name)

    deleted_count = cleanup_expired_bubblepops(now=now)
    assert deleted_count == 2

    # Verify active pop remains intact (row and file)
    assert Bubblepop.objects.filter(id=active_pop.id).exists()
    assert default_storage.exists(active_image_name)

    # Verify expired pops are deleted from DB and storage
    assert not Bubblepop.objects.filter(id=expired_pop1.id).exists()
    assert not Bubblepop.objects.filter(id=expired_pop2.id).exists()
    assert not default_storage.exists(img1_name)
    assert not default_storage.exists(img2_name)

    # Clean up active pop file from test storage
    default_storage.delete(active_image_name)


def test_cleanup_expired_bubblepops_management_command():
    now = timezone.now()
    expired_pop = BubblepopFactory(
        created_at=now - timedelta(hours=10),
        expires_at=now - timedelta(hours=2),
    )
    img_name = expired_pop.image.name

    out = StringIO()
    call_command("cleanup_expired_bubblepops", stdout=out)
    output = out.getvalue()
    assert "Successfully deleted 1 expired Bubblepop(s)." in output

    assert not Bubblepop.objects.filter(id=expired_pop.id).exists()
    assert not default_storage.exists(img_name)
