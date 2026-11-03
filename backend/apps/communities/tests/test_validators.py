import pytest
from django.core.exceptions import ValidationError

from apps.communities.validators import validate_commname_format, validate_commname_not_reserved


@pytest.mark.parametrize("commname", ["abc", "a" * 21, "board_games", "retro80s"])
def test_valid_commnames_pass_format(commname):
    validate_commname_format(commname)


@pytest.mark.parametrize(
    "commname",
    ["", "ab", "a" * 22, "Board", "board games", "board-games", "ação_x", "board\n"],
)
def test_invalid_commnames_fail_format(commname):
    with pytest.raises(ValidationError):
        validate_commname_format(commname)


@pytest.mark.parametrize("commname", ["new", "mine", "search", "settings", "admin"])
def test_reserved_commnames_are_rejected(commname):
    with pytest.raises(ValidationError) as exc:
        validate_commname_not_reserved(commname)

    assert exc.value.code == "reserved_commname"


def test_regular_commname_is_not_reserved():
    validate_commname_not_reserved("board_games")
