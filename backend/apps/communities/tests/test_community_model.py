import pytest
from django.core.exceptions import ValidationError
from django.db import DataError, IntegrityError, transaction
from django.utils import timezone

from apps.communities.models import Community
from apps.communities.tests.factories import CommunityFactory

pytestmark = pytest.mark.django_db


def raw_community(**overrides) -> Community:
    """Unsaved community that skips validators, to hit database constraints directly."""
    fields = {"commname": "board_games", "name": "Board Games"}
    return Community(**{**fields, **overrides})


def test_new_community_has_sensible_defaults():
    community = CommunityFactory()

    assert community.member_count == 0
    assert community.archived_at is None
    assert not community.is_archived
    assert community.customization_json == {}
    assert community.created_at is not None
    assert str(community) == community.commname


def test_community_customization_json_persists_settings():
    customization = {
        "theme_color": "#2c3e50",
        "header_pattern": "bubbles_floating",
        "badge_icon": "star",
    }
    community = CommunityFactory(customization_json=customization)
    community.refresh_from_db()

    assert community.customization_json == customization


def test_community_field_limits_remain_60_and_500():
    assert Community._meta.get_field("name").max_length == 60
    assert Community._meta.get_field("description").max_length == 500

    # 60 chars for name passes
    valid_comm = CommunityFactory.build(name="a" * 60)
    valid_comm.full_clean()

    # 61 chars for name should fail
    with pytest.raises(ValidationError) as exc:
        CommunityFactory.build(name="a" * 61).full_clean()
    assert "name" in exc.value.message_dict


def test_archived_community_reports_is_archived():
    community = CommunityFactory(archived_at=timezone.now())

    assert community.is_archived


def test_valid_community_passes_full_clean():
    CommunityFactory.build().full_clean()


def test_reserved_commname_is_rejected_by_full_clean():
    with pytest.raises(ValidationError) as exc:
        CommunityFactory.build(commname="settings").full_clean()

    assert "commname" in exc.value.message_dict


def test_duplicate_commname_is_reported_by_full_clean():
    CommunityFactory(commname="board_games")

    with pytest.raises(ValidationError) as exc:
        CommunityFactory.build(commname="board_games").full_clean()

    assert "commname" in exc.value.message_dict


class TestDatabaseConstraints:
    def test_commname_must_be_unique(self):
        raw_community().save()

        with pytest.raises(IntegrityError, match="commname"), transaction.atomic():
            raw_community(name="Another").save()

    @pytest.mark.parametrize(
        "commname",
        ["", "ab", "Board", "board games", "board-games", "board\n"],
    )
    def test_invalid_commname_is_rejected_by_database(self, commname):
        with pytest.raises(IntegrityError, match="chk_community_commname_format"):
            with transaction.atomic():
                raw_community(commname=commname).save()

    def test_commname_longer_than_21_characters_is_rejected_by_column_type(self):
        with pytest.raises(DataError), transaction.atomic():
            raw_community(commname="a" * 22).save()

    def test_name_longer_than_60_characters_is_rejected_by_column_type(self):
        with pytest.raises(DataError), transaction.atomic():
            raw_community(name="a" * 61).save()

    @pytest.mark.parametrize("commname", ["abc", "a" * 21, "board_games"])
    def test_valid_commname_is_accepted_by_database(self, commname):
        raw_community(commname=commname).save()

        assert Community.objects.filter(commname=commname).exists()

    def test_member_count_cannot_be_negative(self):
        with pytest.raises(IntegrityError, match="member_count"), transaction.atomic():
            raw_community(member_count=-1).save()
