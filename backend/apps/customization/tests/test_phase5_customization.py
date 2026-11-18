import io

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APIClient

from apps.accounts.tests.factories import UserFactory
from apps.customization.models import CustomizationItem, CustomizationType
from apps.customization.tests.factories import (
    CustomizationItemFactory,
    UserInventoryItemFactory,
)
from apps.customization.validators import clean_section, validate_item_metadata

pytestmark = pytest.mark.django_db


def png(name="w.png") -> SimpleUploadedFile:
    buf = io.BytesIO()
    Image.new("RGB", (8, 8), "blue").save(buf, format="PNG")
    return SimpleUploadedFile(name, buf.getvalue(), content_type="image/png")


def as_user(user):
    user.refresh_from_db()
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def own(user, **kwargs):
    item = CustomizationItemFactory(**kwargs)
    UserInventoryItemFactory(user=user, item=item)
    return item


def equip(user, slots):
    return as_user(user).post("/api/v1/customization/equip/", {"slots": slots}, format="json")


# ---- metadata validation -------------------------------------------------------------------


@pytest.mark.parametrize(
    ("item_type", "metadata"),
    [
        ("ACCENT_COLOR", {"color": "#F465AC"}),
        ("ACCENT_COLOR", {"color": "#fff"}),
        ("WALLPAPER", {}),
        ("WALLPAPER", {"fit": "tile"}),
        ("SECTION", {}),
        ("BADGE", {"label": "Veterano", "badge_color": "#7B63FF"}),
        ("AVATAR_FRAME", {"border_color": "#F465AC", "glow": "0 0 12px #7B63FF"}),
        ("NAME_COLOR", {"color": "#123456"}),
        ("PROFILE_THEME", {"primary": "#111", "secondary": "#222"}),
        ("CHAT_BUBBLE", {"bg_color": "#FFFFFF", "radius": 8}),
    ],
)
def test_valid_metadata_is_accepted(item_type, metadata):
    validate_item_metadata(item_type, metadata)


@pytest.mark.parametrize(
    ("item_type", "metadata"),
    [
        ("ACCENT_COLOR", {"color": "red"}),
        ("ACCENT_COLOR", {"color": "#12"}),
        ("ACCENT_COLOR", {"color": "url(javascript:alert(1))"}),
        ("ACCENT_COLOR", {}),
        ("ACCENT_COLOR", {"color": "#fff", "css": "x"}),
        ("WALLPAPER", {"fit": "stretch"}),
        ("WALLPAPER", {"background": "url(http://evil)"}),
        ("BADGE", {"label": ""}),
        ("BADGE", {"label": "x" * 25}),
        ("BADGE", {"label": "<script>", "badge_color": "blue"}),
        ("AVATAR_FRAME", {"border_color": "#fff", "glow": "0 0 12px red"}),
        ("AVATAR_FRAME", {"border_color": "#fff", "glow": "0 0 99px #fff"}),
        ("NAME_COLOR", {"color": "#12345"}),
        ("CHAT_BUBBLE", {"bg_color": "blue"}),
        ("CHAT_BUBBLE", {"nested": {"a": 1}}),
        ("SECTION", "not a dict"),
    ],
)
def test_invalid_metadata_is_rejected(item_type, metadata):
    with pytest.raises(ValidationError):
        validate_item_metadata(item_type, metadata)


def test_wallpaper_requires_an_image_when_cleaned():
    item = CustomizationItem(
        name="W", code="w1", item_type=CustomizationType.WALLPAPER, metadata={}, price=5
    )
    with pytest.raises(ValidationError) as exc:
        item.full_clean()
    assert "image" in exc.value.message_dict


def test_wallpaper_image_upload_is_validated():
    bad = SimpleUploadedFile("x.png", b"not an image", content_type="image/png")
    item = CustomizationItem(
        name="W", code="w2", item_type=CustomizationType.WALLPAPER, metadata={}, image=bad
    )
    with pytest.raises(ValidationError) as exc:
        item.full_clean()
    assert "image" in exc.value.message_dict

    ok = CustomizationItem(
        name="W", code="w3", item_type=CustomizationType.WALLPAPER, metadata={}, image=png()
    )
    ok.full_clean()


def test_staff_catalog_api_rejects_bad_metadata():
    staff = UserFactory(is_staff=True)
    res = as_user(staff).post(
        "/api/v1/customization/items/",
        {
            "name": "Cor",
            "code": "cor_ruim",
            "item_type": "ACCENT_COLOR",
            "scope": "USER",
            "price": 5,
            "metadata": {"color": "javascript:alert(1)"},
        },
        format="json",
    )
    assert res.status_code == 400
    ok = as_user(staff).post(
        "/api/v1/customization/items/",
        {
            "name": "Cor",
            "code": "cor_boa",
            "item_type": "ACCENT_COLOR",
            "scope": "USER",
            "price": 5,
            "metadata": {"color": "#F465AC"},
        },
        format="json",
    )
    assert ok.status_code == 201


# ---- wallpaper / accent ----------------------------------------------------------------------


def test_wallpaper_is_bought_equipped_and_snapshot_has_image_url():
    user = UserFactory()
    item = CustomizationItemFactory(
        item_type=CustomizationType.WALLPAPER, metadata={"fit": "cover"}, image=png(), price=0
    )
    client = as_user(user)
    assert client.post(f"/api/v1/customization/items/{item.pk}/purchase/").status_code == 201
    listing = client.get("/api/v1/customization/items/?item_type=WALLPAPER").data["results"]
    assert listing[0]["image"].startswith("http://testserver/media/customization/")
    res = equip(user, {"wallpaper": item.pk})
    assert res.status_code == 200
    stored = res.data["wallpaper"]
    assert stored["image"].startswith("/media/customization/")
    assert stored["metadata"] == {"fit": "cover"}


def test_accent_color_equips_only_in_its_slot():
    user = UserFactory()
    item = own(user, item_type=CustomizationType.ACCENT_COLOR, metadata={"color": "#38BDF8"})
    assert equip(user, {"accent_color": item.pk}).status_code == 200
    assert equip(user, {"name_color": item.pk}).status_code == 400


def test_user_cannot_equip_item_they_do_not_own():
    user = UserFactory()
    item = CustomizationItemFactory(item_type=CustomizationType.WALLPAPER, metadata={})
    res = equip(user, {"wallpaper": item.pk})
    assert res.status_code == 400 and res.data["error"]["code"] == "item_not_owned"


# ---- badges ----------------------------------------------------------------------------------


def badge(user, label):
    return own(user, item_type=CustomizationType.BADGE, metadata={"label": label})


def test_up_to_three_different_badges_can_be_shown():
    user = UserFactory()
    a, b, c = badge(user, "A"), badge(user, "B"), badge(user, "C")
    res = equip(user, {"badge": a.pk, "badge_2": b.pk, "badge_3": c.pk})
    assert res.status_code == 200
    assert [res.data[k]["metadata"]["label"] for k in ("badge", "badge_2", "badge_3")] == [
        "A",
        "B",
        "C",
    ]


def test_fourth_badge_slot_and_wrong_slots_are_rejected():
    user = UserFactory()
    a = badge(user, "A")
    assert equip(user, {"badge_4": a.pk}).status_code == 400
    frame = own(user, item_type=CustomizationType.AVATAR_FRAME, metadata={"border_color": "#fff"})
    assert equip(user, {"badge_2": frame.pk}).status_code == 400


def test_same_badge_cannot_fill_two_slots():
    user = UserFactory()
    a = badge(user, "A")
    res = equip(user, {"badge": a.pk, "badge_2": a.pk})
    assert res.status_code == 400 and res.data["error"]["code"] == "duplicate_badge"
    # and nothing was written
    user.refresh_from_db()
    assert "badge" not in user.customization_json


def test_unequipping_one_badge_keeps_the_others():
    user = UserFactory()
    a, b = badge(user, "A"), badge(user, "B")
    equip(user, {"badge": a.pk, "badge_2": b.pk})
    res = equip(user, {"badge": None})
    assert "badge" not in res.data and res.data["badge_2"]["metadata"]["label"] == "B"


def test_badge_granted_by_staff_through_inventory_can_be_equipped():
    user = UserFactory()
    item = CustomizationItemFactory(
        item_type=CustomizationType.BADGE, metadata={"label": "Fundador"}, price=9999
    )
    UserInventoryItemFactory(user=user, item=item, transaction=None)  # what the admin does
    assert equip(user, {"badge": item.pk}).status_code == 200


# ---- profile section ------------------------------------------------------------------------


def test_section_is_locked_until_an_item_is_owned():
    user = UserFactory()
    res = as_user(user).put(
        "/api/v1/customization/section/", {"title": "Sobre", "text": "oi"}, format="json"
    )
    assert res.status_code == 403 and res.data["error"]["code"] == "section_locked"


def test_section_write_and_visibility_follow_the_equipped_item():
    user = UserFactory()
    item = own(user, item_type=CustomizationType.SECTION, metadata={})
    client = as_user(user)
    res = client.put(
        "/api/v1/customization/section/",
        {"title": " Meus pets ", "text": "Dois gatos e <b>um cachorro</b>"},
        format="json",
    )
    assert res.status_code == 200
    assert res.data == {
        "title": "Meus pets",
        "text": "Dois gatos e <b>um cachorro</b>",
    }  # plain text
    # not equipped yet: not shown
    assert as_user(user).get("/api/v1/users/me/").data["section"] is None
    equip(user, {"section": item.pk})
    me = as_user(user).get("/api/v1/users/me/").data
    assert me["section"] == {"title": "Meus pets", "text": "Dois gatos e <b>um cachorro</b>"}
    other = UserFactory()
    public = as_user(other).get(f"/api/v1/users/{user.username}/").data
    assert public["section"]["title"] == "Meus pets"
    # unequip hides it again for everyone
    equip(user, {"section": None})
    assert as_user(other).get(f"/api/v1/users/{user.username}/").data["section"] is None


@pytest.mark.parametrize(
    "payload",
    [
        {"title": "x" * 41, "text": "ok"},
        {"title": "ok", "text": "x" * 501},
        {"title": "ok", "text": "bad \x00 char"},
    ],
)
def test_section_limits(payload):
    user = UserFactory()
    own(user, item_type=CustomizationType.SECTION, metadata={})
    res = as_user(user).put("/api/v1/customization/section/", payload, format="json")
    assert res.status_code == 400


def test_clean_section_helper_bounds():
    assert clean_section(" a ", " b ") == ("a", "b")
    with pytest.raises(ValidationError):
        clean_section("a" * 41, "")


# ---- profile PATCH cannot smuggle tokens ---------------------------------------------------


def test_patch_profile_rebuilds_customization_from_the_catalog():
    user = UserFactory()
    item = own(user, item_type=CustomizationType.NAME_COLOR, metadata={"color": "#112233"})
    res = as_user(user).patch(
        "/api/v1/users/me/",
        {
            "customization_json": {
                "name_color": {
                    "id": item.pk,
                    "metadata": {"color": "red; background:url(//evil)"},
                    "name": "hacked",
                }
            }
        },
        format="json",
    )
    assert res.status_code == 200
    stored = res.data["customization_json"]["name_color"]
    assert stored["metadata"] == {"color": "#112233"}
    assert stored["name"] == item.name


def test_patch_profile_rejects_foreign_items_and_wrong_slots():
    user = UserFactory()
    foreign = CustomizationItemFactory(
        item_type=CustomizationType.NAME_COLOR, metadata={"color": "#112233"}
    )
    client = as_user(user)
    res = client.patch(
        "/api/v1/users/me/",
        {"customization_json": {"name_color": {"id": foreign.pk}}},
        format="json",
    )
    assert res.status_code == 400
    mine = own(user, item_type=CustomizationType.NAME_COLOR, metadata={"color": "#112233"})
    res = client.patch(
        "/api/v1/users/me/", {"customization_json": {"badge": {"id": mine.pk}}}, format="json"
    )
    assert res.status_code == 400
