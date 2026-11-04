import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.accounts.tests.factories import UserFactory
from apps.communities.tests.factories import CommunityFactory
from apps.content.models import Bubblegram, BubblegramType
from apps.content.tests.factories import BubblegramFactory, BubblegramMediaFactory

pytestmark = pytest.mark.django_db


def test_personal_bubblegram_creation():
    bubblegram = BubblegramFactory(community=None)

    assert bubblegram.pk is not None
    assert bubblegram.is_personal
    assert not bubblegram.is_community
    assert bubblegram.soap_count == 0
    assert "u/" in str(bubblegram)


def test_community_bubblegram_creation():
    community = CommunityFactory()
    bubblegram = BubblegramFactory(community=community)

    assert bubblegram.pk is not None
    assert bubblegram.is_community
    assert not bubblegram.is_personal
    assert f"c/{community.commname}" in str(bubblegram)


def test_text_bubblegram_requires_non_empty_text():
    user = UserFactory()
    bubblegram = BubblegramFactory.build(user=user, type=BubblegramType.TEXT, text="   ")

    with pytest.raises(ValidationError) as exc:
        bubblegram.full_clean()

    assert "text" in exc.value.message_dict


def test_media_bubblegram_allows_empty_text():
    user = UserFactory()
    bubblegram = BubblegramFactory.build(user=user, type=BubblegramType.MEDIA, text="")
    bubblegram.full_clean()


class TestDatabaseConstraints:
    def test_database_rejects_text_bubblegram_with_empty_text(self):
        user = UserFactory()
        bubblegram = Bubblegram(user=user, type=BubblegramType.TEXT, text="")

        with pytest.raises(IntegrityError, match="chk_bubblegram_text_required_if_text_type"):
            with transaction.atomic():
                bubblegram.save()

    def test_bubblegram_media_unique_position_per_post(self):
        post = BubblegramFactory(type=BubblegramType.MEDIA)
        BubblegramMediaFactory(bubblegram=post, position=0)

        with pytest.raises(IntegrityError, match="uniq_bubblegram_media_pos"):
            with transaction.atomic():
                BubblegramMediaFactory(bubblegram=post, position=0)
