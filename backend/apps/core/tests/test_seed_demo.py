import hashlib
import io
import urllib.request
from datetime import timedelta

import pytest
from django.contrib.auth import authenticate
from django.core.files.storage import default_storage
from django.core.management import CommandError, call_command
from django.db import connection
from django.db.models import Count, Q, Sum
from django.utils import timezone
from PIL import Image

from apps.accounts.models import User, UserConnection
from apps.accounts.tests.factories import UserFactory
from apps.communities.models import Community, CommunityMember, MemberRole
from apps.content.models import Bubblegram, BubblegramMedia, BubblegramSupport, Bubblepop, Comment
from apps.core.demo import seeder
from apps.customization.models import CommunityInventoryItem, CustomizationItem, UserInventoryItem
from apps.economy.models import SoapTransaction, Wallet
from apps.moderation.models import AuditLog, Report
from apps.social.models import Letter

pytestmark = pytest.mark.django_db

SMALL = [
    "--users", "6",
    "--communities", "3",
    "--posts-per-user", "2",
    "--images", "3",
]  # fmt: skip


class FakeProvider:
    """Stands in for the photo APIs: tiny PNGs whose color identifies the URL; no network."""

    @staticmethod
    def color(url):
        digest = hashlib.sha1(url.encode()).digest()
        return (digest[0], digest[1], digest[2])

    def urls(self, species, count):
        return [f"fake://{species}/{i}" for i in range(count)]

    def download(self, url):
        buffer = io.BytesIO()
        Image.new("RGB", (24, 24), self.color(url)).save(buffer, "PNG")
        return buffer.getvalue()


@pytest.fixture
def demo(settings, tmp_path, monkeypatch):
    """Demo environment: DEBUG on, 'the demo database' = the test database, offline images."""
    settings.DEBUG = True
    settings.DEMO_DB_NAME = connection.settings_dict["NAME"]
    settings.DEMO_CACHE_DIR = tmp_path / "demo_cache"
    monkeypatch.setattr("apps.core.demo.images.WebImageProvider", FakeProvider)

    def no_network(*args, **kwargs):
        raise AssertionError("the seed must not touch the network in tests")

    monkeypatch.setattr(urllib.request, "urlopen", no_network)
    return settings.DEMO_CACHE_DIR


def seed(*extra, **kwargs):
    out = io.StringIO()
    err = io.StringIO()
    call_command("seed_demo", *SMALL, *extra, stdout=out, stderr=err, **kwargs)
    return out.getvalue(), err.getvalue()


def table_counts():
    models = (
        User, UserConnection, Community, CommunityMember, Bubblegram, BubblegramMedia,
        Comment, BubblegramSupport, Bubblepop, Letter, Report, AuditLog, SoapTransaction,
        CustomizationItem, UserInventoryItem, CommunityInventoryItem, Wallet,
    )  # fmt: skip
    return [m.objects.count() for m in models]


# ------------------------------------------------------------------------- safety


def test_refuses_to_run_without_the_demo_settings():
    with pytest.raises(CommandError, match="demo settings"):
        call_command("seed_demo")
    assert User.objects.count() == 0


def test_refuses_when_debug_is_off(demo, settings):
    settings.DEBUG = False
    with pytest.raises(CommandError, match="demo settings"):
        call_command("seed_demo")


def test_refuses_any_database_other_than_the_demo_one(demo, settings):
    settings.DEMO_DB_NAME = "some_other_database"
    with pytest.raises(CommandError, match="Refusing to run"):
        call_command("seed_demo", "--reset")
    with pytest.raises(CommandError, match="Refusing to run"):
        call_command("seed_demo")
    assert User.objects.count() == 0


# ------------------------------------------------------------------------- content


def test_seeds_every_kind_of_entity_through_the_services(demo):
    out, _err = seed()

    assert "Demo data ready." in out
    counts = dict(zip(
        ["users", "follows", "communities", "members", "posts", "media", "comments", "supports",
         "pops", "letters", "reports", "audit", "ledger", "items", "user items", "comm items",
         "wallets"],
        table_counts(), strict=True,
    ))  # fmt: skip
    for name, value in counts.items():
        assert value > 0, f"nothing was created for {name}"
    # 3 themed communities plus the 3 showcase ones (suspended, banned, deleted)
    assert counts["communities"] == 6


def test_people_and_credentials(demo):
    out, _err = seed()

    admin = User.objects.get(username="admin_demo")
    assert admin.is_staff and admin.is_superuser
    assert authenticate(username="admin_demo", password="DemoPets2026!") == admin
    moderator = User.objects.get(username="moderador_demo")
    assert not moderator.is_staff
    assert CommunityMember.objects.filter(user=moderator, role=MemberRole.COMM_ADMIN).exists()
    assert "admin_demo" in out and "moderador_demo" in out and "DemoPets2026!" in out
    live = User.objects.filter(deleted_at__isnull=True)
    assert all(u.email.endswith("@demo.bubbles.test") for u in live)


def test_soap_ledger_and_counters_stay_consistent(demo):
    seed()

    # Every wallet's balance equals the sum of its ledger: all movements went through economy.
    for wallet in Wallet.objects.all():
        ledger = SoapTransaction.objects.filter(wallet=wallet).aggregate(t=Sum("amount"))["t"] or 0
        assert ledger == wallet.soap_balance
    # Cached counters match the rows they summarize.
    for post in Bubblegram.objects.all():
        assert post.soap_count == BubblegramSupport.objects.filter(bubblegram=post).count()
    for community in Community.objects.all():
        members = CommunityMember.objects.filter(community=community).exclude(
            current_state="BANNED"
        )
        assert community.member_count == members.count()
    # Founding put soap in the community wallets and they bought customization.
    assert CommunityInventoryItem.objects.exists()
    assert all(Wallet.objects.get(community=c).soap_balance >= 0 for c in Community.objects.all())


def test_content_covers_the_interesting_cases(demo):
    seed("--users", "10", "--comments-per-post", "5")

    assert Bubblegram.objects.filter(community__isnull=True).exists()
    assert Bubblegram.objects.filter(community__isnull=False).exists()
    assert Comment.objects.filter(parent__isnull=False).exists()
    assert Bubblepop.objects.filter(expires_at__gt=timezone.now()).exists()
    assert Bubblepop.objects.filter(expires_at__lte=timezone.now()).count() == 2
    assert Letter.objects.filter(reply_to__isnull=False).exists()
    assert Letter.objects.filter(read_at__isnull=True).exists()
    assert Report.objects.filter(status="PENDING").exists()
    assert Report.objects.exclude(status="PENDING").exists()
    states = set(CommunityMember.objects.values_list("current_state", flat=True))
    assert {"ACTIVE", "SILENCED", "BANNED"} <= states


def test_dates_are_spread_over_the_recent_past(demo):
    seed("--days", "20")
    now = timezone.now()

    times = list(Bubblegram.objects.values_list("published_at", flat=True))
    assert max(times) <= now
    assert (max(times) - min(times)).days >= 2  # not all "just now"
    assert min(times) >= now - timedelta(days=21)
    for comment in Comment.objects.select_related("bubblegram"):
        assert comment.published_at >= comment.bubblegram.published_at
    for post in Bubblegram.objects.filter(community__isnull=False).select_related("community"):
        assert post.published_at >= post.community.created_at
    for community in Community.objects.all():
        assert community.created_at < now - timedelta(days=2)


# ------------------------------------------------------------------------- images


def test_images_are_saved_through_the_models_and_cached(demo):
    seed()

    assert BubblegramMedia.objects.exists()
    assert User.objects.exclude(profile_photo="").exists()
    assert Community.objects.exclude(community_photo="").exists()
    for item in BubblegramMedia.objects.all():
        assert default_storage.exists(item.media.name)
    cache = demo / "images"
    assert len(list((cache / "cat").iterdir())) == 3
    assert len(list((cache / "dog").iterdir())) == 3


def test_no_images_flag_creates_everything_without_them(demo):
    seed("--no-images")

    assert Bubblegram.objects.exists() and User.objects.count() >= 6
    assert not BubblegramMedia.objects.exists()
    assert not User.objects.exclude(profile_photo="").exists()
    assert not CustomizationItem.objects.filter(item_type="WALLPAPER").exists()
    assert not Community.objects.exclude(banner_photo="").exists()
    assert not Bubblepop.objects.exists()  # bubblepops require an image
    assert not (demo / "images").exists()


def test_offline_falls_back_to_the_cache_or_to_no_images_with_a_warning(demo, monkeypatch):
    class Offline(FakeProvider):
        def urls(self, species, count):
            raise OSError("network unreachable")

    monkeypatch.setattr("apps.core.demo.images.WebImageProvider", Offline)
    _out, err = seed()

    assert "Could not download" in err
    assert "created without images" in err
    assert Bubblegram.objects.exists()
    assert not BubblegramMedia.objects.exists()

    # With photos already cached the next run uses them without any download.
    monkeypatch.setattr("apps.core.demo.images.WebImageProvider", FakeProvider)
    seed("--reset")
    seed("--no-download")  # cache is empty and downloads are disabled: still works
    assert Bubblegram.objects.exists()


# ------------------------------------------------------------------------- idempotency and reset


def test_running_twice_does_not_duplicate_anything(demo):
    seed()
    first = table_counts()
    out, _err = seed()

    assert table_counts() == first
    assert "nothing new" in out


def test_same_seed_gives_the_same_content(demo):
    def snapshot():
        return sorted(Comment.objects.values_list("text", flat=True)), sorted(
            Bubblegram.objects.values_list("text", flat=True)
        )

    seed("--seed", "7")
    first = snapshot()
    seed("--reset")
    seed("--seed", "7")
    assert snapshot() == first


def test_the_people_are_fixed_characters_whatever_the_seed(demo):
    seed("--seed", "8")
    names = set(
        User.objects.exclude(username__startswith="deleted_").values_list("name", flat=True)
    )
    assert "Marcos Esponja Silva" in names and "Marlene Baiacu Lima" in names


def test_reset_removes_only_what_the_seed_created(demo):
    manual = UserFactory(username="manual_user")
    Wallet.objects.create(user=manual, soap_balance=5)
    SoapTransaction.objects.create(
        wallet=manual.wallet, amount=5, action_type="SIGNUP_GRANT", balance_after=5
    )
    seed()
    files = [m.media.name for m in BubblegramMedia.objects.all()]
    assert files and User.objects.count() > 2

    out = io.StringIO()
    call_command("seed_demo", "--reset", stdout=out)

    assert "Removed:" in out.getvalue()
    assert list(User.objects.values_list("username", flat=True)) == ["manual_user"]
    assert Wallet.objects.filter(user=manual).exists()
    assert SoapTransaction.objects.filter(wallet__user=manual).count() == 1
    assert not Community.objects.exists()
    assert not Bubblegram.objects.exists()
    assert not CustomizationItem.objects.exists()
    assert not Report.objects.exists() and not AuditLog.objects.exists()
    assert not SoapTransaction.objects.exclude(wallet__user=manual).exists()
    assert not any(default_storage.exists(name) for name in files)
    assert not (demo / seeder.MANIFEST_NAME).exists()


def test_reset_keeps_manual_activity_on_other_accounts_and_is_repeatable(demo):
    seed()
    out = io.StringIO()
    call_command("seed_demo", "--reset", stdout=out)
    out = io.StringIO()
    call_command("seed_demo", "--reset", stdout=out)
    assert "Nothing to reset" in out.getvalue()

    # After a reset the seed can run again from scratch.
    seed()
    assert User.objects.filter(username="admin_demo").exists()


def test_reset_does_not_delete_catalog_items_someone_else_owns(demo):
    seed()
    item = CustomizationItem.objects.filter(scope__in=("USER", "BOTH")).first()
    manual = UserFactory(username="collector")
    Wallet.objects.create(user=manual, soap_balance=100)
    UserInventoryItem.objects.create(user=manual, item=item)

    call_command("seed_demo", "--reset", stdout=io.StringIO())

    assert CustomizationItem.objects.filter(pk=item.pk).exists()  # PROTECTed by a manual holder
    assert User.objects.filter(username="collector").exists()


def test_community_posts_come_only_from_active_members(demo):
    seed()
    # (the community the leader deleted keeps its posts but loses every membership)
    for post in Bubblegram.objects.filter(community__isnull=False, community__deleted_at=None):
        assert CommunityMember.objects.filter(community=post.community, user=post.user).exists()
    totals = Bubblegram.objects.aggregate(
        n=Count("id"), personal=Count("id", filter=Q(community__isnull=True))
    )
    assert totals["personal"] > 0 and totals["n"] > totals["personal"]


# ------------------------------------------------------------------- polish 2 showcase


def test_customization_variations_are_seeded_and_worn(demo):
    seed()

    wallpapers = CustomizationItem.objects.filter(item_type="WALLPAPER")
    assert wallpapers.count() >= 3
    assert {w.metadata["fit"] for w in wallpapers} == {"cover"}  # no tiled bubble pattern
    for wallpaper in wallpapers:
        assert wallpaper.image and default_storage.exists(wallpaper.image.name)
        wallpaper.full_clean()  # the catalog art passes the same validation as the admin
    assert CustomizationItem.objects.filter(item_type="ACCENT_COLOR").count() >= 3
    assert CustomizationItem.objects.filter(item_type="SECTION").count() >= 2
    assert CustomizationItem.objects.filter(item_type="BADGE").count() >= 5
    # every variation is owned by someone
    for kind in ("WALLPAPER", "ACCENT_COLOR", "SECTION"):
        for item in CustomizationItem.objects.filter(item_type=kind, price__lte=60):
            assert UserInventoryItem.objects.filter(item=item).exists(), item.code

    worn = User.objects.filter(customization_json__has_key="wallpaper")
    assert worn.exists()
    first = worn.order_by("pk").first()
    assert first.customization_json["wallpaper"]["image"].startswith("/media/customization/")
    assert {"wallpaper", "accent_color", "section"} <= set(first.customization_json)
    # up to three badges on one profile, one of them handed out by staff (no purchase)
    three = [
        u
        for u in User.objects.all()
        if all(slot in u.customization_json for slot in ("badge", "badge_2", "badge_3"))
    ]
    assert three
    team = UserInventoryItem.objects.get(item__code="selo_equipe")
    assert team.transaction is None
    # the section text is plain pt-BR text stored on the user
    with_section = User.objects.exclude(section_text="")
    assert with_section.exists() and all(len(u.section_text) <= 500 for u in with_section)


def test_every_themed_community_gets_a_banner(demo):
    seed()
    themed = Community.objects.exclude(commname__startswith="pets_").exclude(
        commname__startswith="deleted_"
    )
    assert themed.count() == 3
    assert not themed.filter(banner_photo="").exists()


def test_moderation_showcase_states(demo):
    seed()

    suspended = User.objects.get(username="suspenso_demo")
    assert suspended.is_suspended and suspended.moderation_reason
    banned = User.objects.get(username="banido_demo")
    assert banned.is_banned and not banned.is_active and banned.moderation_reason
    assert authenticate(username="banido_demo", password="DemoPets2026!") is None
    deleted = User.objects.get(deleted_at__isnull=False)
    assert deleted.username.startswith("deleted_") and deleted.name == "Conta excluída"
    assert Bubblegram.objects.filter(user=deleted).exists()  # content stays, anonymized

    susp = Community.objects.get(commname="pets_suspensa")
    assert susp.is_suspended and susp.moderation_reason
    ban = Community.objects.get(commname="pets_banida")
    assert ban.is_blocked and ban.moderation_reason
    gone = Community.objects.get(deleted_at__isnull=False)
    assert gone.commname.startswith("deleted_") and gone.member_count == 0
    assert not CommunityMember.objects.filter(community=gone).exists()
    # the app really treats them as moderated: the staff list and the audit log show them
    assert AuditLog.objects.filter(action="USER_SUSPEND").exists()
    assert AuditLog.objects.filter(action="COMMUNITY_BLOCK").exists()
    assert AuditLog.objects.filter(action="COMMUNITY_SUSPEND").exists()


def test_reset_removes_the_showcase_and_catalog_images(demo):
    seed()
    images = list(
        CustomizationItem.objects.filter(item_type="WALLPAPER").values_list("image", flat=True)
    )
    banners = list(
        Community.objects.exclude(banner_photo="").values_list("banner_photo", flat=True)
    )
    assert images and banners

    call_command("seed_demo", "--reset", stdout=io.StringIO())

    assert not User.objects.exists() and not Community.objects.exists()
    assert not any(default_storage.exists(name) for name in images + banners)


def test_demo_feed_shows_popular_suggestions(demo):
    """Popular suggestions look at the last 24 h only, so the seed makes a few posts recent."""
    from datetime import timedelta

    from apps.content.selectors import list_feed_bubblegrams

    seed("--users", "10")
    recent = Bubblegram.objects.filter(
        community__isnull=True,
        soap_count__gt=0,
        published_at__gte=timezone.now() - timedelta(hours=24),
    )
    assert recent.exists()
    popular_seen = any(
        any(p.suggestion_reason == "popular" for p in list_feed_bubblegrams(user=user))
        for user in User.objects.filter(is_active=True)
    )
    assert popular_seen


# ------------------------------------------------------------------ believable content

FULL = ["--users", "16", "--communities", "8", "--images", "80", "--posts-per-user", "0"]


def first_pixel(field):
    with Image.open(field.open("rb")) as image:
        return image.convert("RGB").getpixel((0, 0))


def pool_colors(pool, count=80):
    return {FakeProvider.color(f"fake://{pool}/{i}") for i in range(count)}


def test_no_caption_is_repeated_and_every_profile_has_a_picture(demo):
    seed(*FULL)

    texts = list(Bubblegram.objects.values_list("text", flat=True))
    assert len(texts) > 90
    assert len(set(texts)) == len(texts)
    live = User.objects.filter(deleted_at__isnull=True)
    assert live.count() >= 18  # 16 people + admin + the two showcase accounts
    assert not live.filter(profile_photo="").exists()


def test_people_post_about_their_own_pets_with_photos_of_that_species_and_breed(demo):
    seed(*FULL)

    expectations = {
        "marcos_esponja": "dog:golden",
        "otavio_atum": "dog:husky",
        "sandra_esquilo": "dog:border",
        "gabriel_caracol": "cat",
        "lucas_molusco": "cat",
        "moderador_demo": "cat",
    }
    for username, pool in expectations.items():
        media = BubblegramMedia.objects.filter(bubblegram__user__username=username)
        assert media.exists(), username
        for item in media:
            assert first_pixel(item.media) in pool_colors(pool), (username, pool)


def test_no_photo_is_shown_twice(demo):
    seed(*FULL)

    fields = [m.media for m in BubblegramMedia.objects.all()]
    fields += [
        p.image
        for p in Bubblepop.objects.filter(
            user__username__in=["marcos_esponja", "sandra_esquilo", "bianca_bagre", "fred_sardinha"]
        )
    ]
    pixels = [first_pixel(f) for f in fields]
    assert len(pixels) > 60
    assert len(set(pixels)) == len(pixels)


def test_conversations_are_real_threads(demo):
    seed(*FULL)

    root = Comment.objects.get(text__startswith="NÃO. Chocolate é tóxico")
    reply = Comment.objects.get(text__startswith="Corri aqui e ele está bem")
    assert reply.parent_id == root.id
    assert reply.user.username == "patricio_estrela"
    assert Comment.objects.get(text__startswith="Que alívio!").parent_id == reply.id
    post = root.bubblegram
    assert post.text.startswith("Dei um pedacinho de chocolate")
    assert post.community.commname == "veterinario_responde"
    assert post.comments.count() == 5


def test_photo_posts_get_reactions_in_each_persons_voice(demo):
    seed(*FULL)

    texts = set(
        Comment.objects.filter(user__username="gabriel_caracol").values_list("text", flat=True)
    )
    assert texts and all(
        t.startswith(("Miau", "Concordo", "Valeu", "Entendo")) or t[0].isupper() for t in texts
    )
    pet_posts = Bubblegram.objects.filter(media__isnull=False).distinct()
    assert Comment.objects.filter(bubblegram__in=pet_posts).exists()


def test_letters_are_conversations_between_people_who_follow_each_other(demo):
    seed(*FULL)

    questions = Letter.objects.filter(reply_to__isnull=True)
    assert questions.count() == 11
    for letter in questions:
        assert UserConnection.objects.filter(
            follower=letter.sender, followed=letter.recipient
        ).exists()
        assert UserConnection.objects.filter(
            follower=letter.recipient, followed=letter.sender
        ).exists()
        answer = Letter.objects.get(reply_to=letter)
        assert answer.sender_id == letter.recipient_id
    nat = Letter.objects.get(text__startswith="Oi, Nat! O Pedra comeu")
    assert "sabonete" in Letter.objects.get(reply_to=nat).text


def test_activity_varies_between_people(demo):
    seed(*FULL)

    counts = {
        u.username: Bubblegram.objects.filter(user=u).count()
        for u in User.objects.filter(deleted_at__isnull=True)
        if u.username not in ("admin_demo", "suspenso_demo", "banido_demo")
    }
    assert max(counts.values()) - min(counts.values()) >= 2
    assert len(set(counts.values())) >= 3


def test_bubblepops_are_in_each_persons_voice(demo):
    seed(*FULL)

    pop = Bubblepop.objects.get(user__username="gabriel_caracol", expires_at__gt=timezone.now())
    assert pop.description in ("Concha.", "Espiral.")


# ---- the written content itself (pure data checks) ----


def test_written_content_is_consistent():
    from apps.core.demo import personas, stories

    names = {p["username"] for p in personas.PERSONAS}
    assert len(names) == len(personas.PERSONAS) == 16
    for persona in personas.PERSONAS:
        username = persona["username"]
        assert persona["pets"] and persona["reactions"] and persona["replies"] and persona["pops"]
        assert set(personas.FOLLOWS[username]) <= names - {username}
        assert set(personas.MEMBERSHIPS[username]) <= set(personas.THEMES)
        entries = stories.STORIES[username]
        assert entries
        for entry in entries:
            if entry["pet"]:
                assert entry["pet"] in persona["pets"], (username, entry["text"])
            assert entry["community"] in (None, *personas.MEMBERSHIPS[username]), (
                username,
                entry["text"],
            )
            assert len(entry["text"]) <= 2000
            for index, item in enumerate(entry["thread"]):
                assert item[0] in names, (username, item)
                parent = item[2] if len(item) > 2 else None
                assert parent is None or parent < index
                # nobody comments in a community they are not in
                if entry["community"]:
                    assert entry["community"] in personas.MEMBERSHIPS[item[0]], (username, item)
    for leader in personas.LEADERS.values():
        assert leader in names


def test_captions_do_not_contradict_the_photos():
    """Cats come from a random cat pool (no colors or breeds in captions); a dog's caption
    only names its own breed."""
    import re

    from apps.core.demo import personas, stories

    cat_words = re.compile(
        r"\b(laranja|preto|preta|branco|branca|cinza|amarel[oa]|rajad[oa]|tigrad[oa]|siamês|persa)\b",
        re.I,
    )
    breed_words = {
        "golden": "golden", "labrador": "labrador", "husky": "husky", "beagle": "beagle",
        "boxer": "boxer", "chihuahua": "chihuahua", "poodle": "poodle", "dachshund": "salsicha",
        "cocker": "cocker", "border": "border collie", "samoyed": "samoied",
    }  # fmt: skip
    for persona in personas.PERSONAS:
        for entry in stories.STORIES[persona["username"]]:
            if not entry["pet"]:
                continue
            _name, species, breed = persona["pets"][entry["pet"]]
            text = entry["text"].lower()
            if species == "cat":
                assert not cat_words.search(text), entry["text"]
            else:
                for other, word in breed_words.items():
                    if other != breed:
                        assert word not in text, (entry["text"], breed)
