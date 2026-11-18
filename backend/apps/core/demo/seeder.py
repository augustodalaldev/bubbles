"""Demo data generator (pet communities) and the matching reset.

Everything goes through the project's services whenever one exists, so business rules, cached
counters and the soap ledger behave exactly like in the real app. The ORM is used directly only
where no service exists: the customization catalog (an admin-maintained table), back-dated
timestamps (services always stamp "now") and already expired bubblepops.
"""

import json
import random
from collections import Counter
from datetime import timedelta
from pathlib import Path

from django.core.files.storage import default_storage
from django.db import connection, transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify
from faker import Faker

from apps.accounts.models import User, UserConnection
from apps.accounts.services import delete_account, follow_user, register_user
from apps.communities.models import Community, CommunityMember, MemberState
from apps.communities.services import (
    create_community,
    delete_community,
    join_community,
    moderate_member,
    promote_member,
    update_community,
)
from apps.content.models import (
    Bubblegram,
    BubblegramMedia,
    BubblegramSupport,
    Bubblepop,
    Comment,
    CommentSupport,
)
from apps.content.services import (
    create_bubblegram,
    create_bubblepop,
    create_comment,
    support_bubblegram,
    support_comment,
)
from apps.core.demo import content, personas, stories
from apps.core.demo.images import ImageLibrary, banner_image, breed_pool, wallpaper_image
from apps.core.exceptions import DomainError
from apps.customization.models import (
    CommunityInventoryItem,
    CustomizationItem,
    UserInventoryItem,
)
from apps.customization.services import (
    equip_community_customization,
    equip_customization,
    purchase_community_item,
    purchase_customization_item,
    update_profile_section,
)
from apps.economy.models import SoapTransaction, Wallet
from apps.economy.services import ensure_community_wallet
from apps.moderation.models import (
    AuditLog,
    Report,
    ReportReason,
    ReportStatus,
    ReportTargetType,
)
from apps.moderation.services import (
    admin_adjust_soap,
    ban_user,
    block_community,
    file_report,
    review_report,
    suspend_community,
    suspend_user,
)
from apps.social.models import Letter
from apps.social.services import send_letter

PASSWORD = "DemoPets2026!"
EMAIL_DOMAIN = "demo.bubbles.test"
ADMIN_USERNAME = "admin_demo"
MODERATOR_USERNAME = "moderador_demo"
MANIFEST_NAME = "seed_manifest.json"
MANIFEST_VERSION = 1
FOUNDING_RESERVE = 400  # a founder needs the founding cost plus soap to post


def _manifest_path(cache_dir: Path) -> Path:
    return Path(cache_dir) / MANIFEST_NAME


def load_manifest(cache_dir: Path) -> dict:
    path = _manifest_path(cache_dir)
    if path.exists():
        try:
            data = json.loads(path.read_text())
            if data.get("version") == MANIFEST_VERSION:
                data.setdefault("special", {})  # manifests written before the showcase step
                return data
        except (ValueError, OSError):
            pass
    return {
        "version": MANIFEST_VERSION,
        "db": connection.settings_dict["NAME"],
        "users": [],
        "communities": [],
        "items": [],
        "reports": [],
        "audit_logs": [],
        "special": {},
    }


def save_manifest(cache_dir: Path, manifest: dict) -> None:
    path = _manifest_path(cache_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True))


class DemoSeeder:
    def __init__(
        self,
        *,
        cache_dir: Path,
        images: ImageLibrary,
        seed: int = 42,
        users: int = 12,
        communities: int = 6,
        posts_per_user: int = 3,
        comments_per_post: int = 3,
        expired_bubblepops: int = 2,
        days: int = 30,
        log=print,
    ):
        self.cache_dir = Path(cache_dir)
        self.images = images
        self.seed = seed
        self.personas = personas.PERSONAS[: max(4, min(users, len(personas.PERSONAS)))]
        self.n_users = len(self.personas)
        self.n_communities = max(1, min(communities, len(content.COMMUNITY_THEMES)))
        self.posts_cap = posts_per_user if posts_per_user and posts_per_user > 0 else None
        self.comments_per_post = max(0, comments_per_post)
        self.expired_bubblepops = max(0, expired_bubblepops)
        self.days = max(7, days)
        self.log = log
        self.rng = random.Random(seed)
        self.fake = Faker("pt_BR")
        self.fake.seed_instance(seed)
        self.now = timezone.now()
        self.stats: Counter[str] = Counter()
        self.new: dict[str, list] = {
            k: []
            for k in (
                "users",
                "communities",
                "members",
                "follows",
                "posts",
                "comments",
                "post_supports",
                "comment_supports",
                "letters",
                "reports",
                "pops",
            )
        }
        self.manifest = load_manifest(self.cache_dir)
        if self.manifest.get("db") != connection.settings_dict["NAME"]:
            self.manifest = {
                **load_manifest(Path("/nonexistent")),
                "db": connection.settings_dict["NAME"],
            }
        self.audit_before = (
            AuditLog.objects.order_by("-id").values_list("id", flat=True).first() or 0
        )

    # ------------------------------------------------------------------ helpers
    def _try(self, func, *args, **kwargs):
        """Run a service; a rule violation (already member, no soap, ...) just means 'skip'."""
        try:
            with transaction.atomic():
                return func(*args, **kwargs)
        except DomainError:
            self.stats["skipped (rule)"] += 1
            return None

    def _remember(self, key: str, pk: int) -> None:
        if pk not in self.manifest[key]:
            self.manifest[key].append(pk)

    def _count(self, label: str) -> None:
        self.stats[label] += 1

    def _ensure_balance(self, user, minimum: int, reason: str = "Demo seed funding") -> None:
        wallet = Wallet.objects.get(user=user)
        if wallet.soap_balance < minimum:
            admin_adjust_soap(
                actor=self.admin, wallet=wallet, amount=minimum - wallet.soap_balance, reason=reason
            )

    def _rng(self, *parts) -> random.Random:
        """An independent, reproducible stream per unit of work.

        Decisions about one user/post/community never depend on what already exists, so running
        the seed again makes the same choices, finds the rows it created and adds nothing.
        """
        return random.Random("|".join(str(x) for x in (self.seed, *parts)))

    def _past(self, lower, upper=None):
        upper = upper or self.now - timedelta(minutes=30)
        span = max(60.0, (upper - lower).total_seconds())
        moment = lower + timedelta(seconds=self.rng.uniform(0, span))
        # People post mostly at lunch and in the evening, not at 3 a.m.
        hour = self.rng.choices(
            (7, 8, 9, 12, 13, 14, 18, 19, 20, 21, 22, 23),
            weights=(2, 3, 2, 4, 3, 2, 4, 5, 6, 6, 4, 2),
        )[0]
        shifted = moment.replace(hour=hour, minute=self.rng.randint(0, 59), second=0)
        return shifted if lower <= shifted <= upper else moment

    def run(self) -> dict:
        self.images.prepare(self._photo_needs())
        self._ensure_catalog()
        self._ensure_people()
        self._follows()
        self._communities()
        self._memberships()
        self._community_customization()
        self._user_customization()
        self._banners()
        self._customization_showcase()
        self._posts()
        self._interactions()
        self._bubblepops()
        self._letters()
        self._reports()
        self._moderation_showcase()
        self._backdate()
        self._finish()
        return {"stats": dict(self.stats), "credentials": self.credentials()}

    def _ensure_catalog(self) -> None:
        for code, name, item_type, scope, price, metadata in content.CATALOG:
            item, created = CustomizationItem.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "item_type": item_type,
                    "scope": scope,
                    "price": price,
                    "metadata": metadata,
                    "description": name,
                },
            )
            if created:
                self._count("customization items")
                self._remember("items", item.pk)
        # Wallpapers are staff-uploaded images; they need the image library switched on.
        if not self.images.enabled:
            return
        for code, name, price, fit, (top, bottom) in content.WALLPAPERS:
            if CustomizationItem.objects.filter(code=code).exists():
                continue
            item = CustomizationItem.objects.create(
                code=code,
                name=name,
                item_type="WALLPAPER",
                scope="USER",
                price=price,
                description=name,
                metadata={"fit": fit},
                image=wallpaper_image(code, top, bottom, fit),
            )
            self._count("customization items")
            self._remember("items", item.pk)

    def _identity(self, index: int, taken: set[str]) -> tuple[str, str]:
        first, last = self.fake.first_name(), self.fake.last_name()
        base = f"{slugify(first)}_{slugify(last)}".replace("-", "_")[:26] or f"pet_tutor_{index}"
        username, n = base, 1
        while username in taken or len(username) < 3:
            n += 1
            username = f"{base}{n}"
        taken.add(username)
        return f"{first} {last}", username

    def _register(self, username: str, name: str, *, avatar: str, bio: str, is_staff: bool = False):
        self.rng = self._rng("user", username)
        user = User.objects.filter(username=username).first()
        if user:
            return user, False
        age_days = int(365.25 * self.rng.uniform(18, 55))
        user = register_user(
            username=username,
            email=f"{username}@{EMAIL_DOMAIN}",
            password=PASSWORD,
            name=name,
            birth_date=(self.now - timedelta(days=age_days)).date(),
            description=bio,
            profile_photo=self.images.avatar(avatar),
        )
        if is_staff:
            User.objects.filter(pk=user.pk).update(is_staff=True, is_superuser=True)
            user.refresh_from_db()
        self._remember("users", user.pk)
        self.new["users"].append(user)
        self._count("users")
        return user, True

    def _persona(self, username: str):
        return next((p for p in self.personas if p["username"] == username), None)

    def _pet(self, persona: dict, pet_id: str) -> tuple[str, str]:
        """(pet name, photo pool): cats come from the shared cat pool, dogs from their breed."""
        name, species, breed = persona["pets"][pet_id]
        return name, ("cat" if species == "cat" else breed_pool(breed))

    def _entries(self, persona: dict) -> list[dict]:
        entries = stories.STORIES.get(persona["username"], [])
        return entries[: self.posts_cap] if self.posts_cap else list(entries)

    def _photo_needs(self) -> dict[str, int]:
        """How many photos each pool must hold: one per picture in a post, one per bubblepop."""
        needs: dict[str, int] = {}
        for persona in self.personas:
            for entry in self._entries(persona):
                if entry["pet"]:
                    _, pool = self._pet(persona, entry["pet"])
                    needs[pool] = needs.get(pool, 0) + entry["photos"]
            if persona["pets"]:
                _, pool = self._pet(persona, next(iter(persona["pets"])))
                needs[pool] = needs.get(pool, 0) + len(persona["pops"][:1])
        return needs

    def _ensure_people(self) -> None:
        self.admin, admin_created = self._register(
            ADMIN_USERNAME,
            "Equipe Bubbles",
            avatar="bubble:admin",
            bio="Administração da demonstração.",
            is_staff=True,
        )
        # The admin funds everyone through audited soap adjustments. Funding happens once, when
        # an account is created: running the seed again must not hand out more soap.
        if admin_created:
            self._ensure_balance(self.admin, 4000, "Demo seed funding")
        self.users = []
        self.by_username = {}
        created_now = set()
        for persona in self.personas:
            user, created = self._register(
                persona["username"], persona["name"], avatar=persona["avatar"], bio=persona["bio"]
            )
            self.users.append(user)
            self.by_username[user.username] = user
            if created:
                created_now.add(user.pk)
        self.moderator = self.by_username[MODERATOR_USERNAME]
        for index, user in enumerate(self.users):
            if user.pk not in created_now:
                continue
            # Founders (first users) get enough soap to found a community and publish.
            self._ensure_balance(
                user, FOUNDING_RESERVE + 500 if index < self.n_communities else 450
            )

    def _follows(self) -> None:
        for user in self.users:
            for target_name in personas.FOLLOWS.get(user.username, []):
                target = self.by_username.get(target_name)
                if target is None or target.pk == user.pk:
                    continue
                if UserConnection.objects.filter(follower=user, followed=target).exists():
                    continue
                connection_row = self._try(follow_user, follower=user, followed=target)
                if connection_row:
                    self.new["follows"].append(connection_row)
                    self._count("follows")

    def _communities(self) -> None:
        self.communities = []
        for index, theme in enumerate(content.COMMUNITY_THEMES[: self.n_communities]):
            self.rng = self._rng("community", theme["commname"])
            leader = (
                self.by_username.get(personas.LEADERS.get(theme["commname"], ""))
                or self.users[index % len(self.users)]
            )
            community = Community.objects.filter(commname=theme["commname"]).first()
            if community is None:
                self._ensure_balance(leader, FOUNDING_RESERVE + 100)
                community = self._try(
                    create_community,
                    creator=leader,
                    commname=theme["commname"],
                    name=theme["name"],
                    description=theme["description"],
                    guidelines=theme["guidelines"],
                    community_photo=self.images.pick(theme["species"], self.rng),
                    banner_photo=self.images.pick(theme["species"], self.rng)
                    if index % 2 == 0
                    else None,
                )
                if community is None:
                    continue
                self._remember("communities", community.pk)
                self.new["communities"].append(community)
                self._count("communities")
                # Support received later also feeds the wallet; seed some soap so the
                # community can already buy customization.
                admin_adjust_soap(
                    actor=self.admin,
                    wallet=ensure_community_wallet(community),
                    amount=self.rng.randint(60, 220),
                    reason="Demo seed: community wallet",
                )
            self.communities.append((community, leader, theme))

    def _memberships(self) -> None:
        for _index, (community, leader, _theme) in enumerate(self.communities):
            commname = community.commname
            for user in self.users:
                if user.pk == leader.pk or commname not in personas.MEMBERSHIPS.get(
                    user.username, []
                ):
                    continue
                if CommunityMember.objects.filter(community=community, user=user).exists():
                    continue
                row = self._try(join_community, user=user, community=community)
                if row:
                    self.new["members"].append(row)
                    self._count("memberships")
            community.refresh_from_db()
            # Roles: the admins chosen for this community (the moderator among them).
            for name in personas.ADMINS.get(commname, []):
                user = self.by_username.get(name)
                if user is None or user.pk == leader.pk:
                    continue
                if CommunityMember.objects.filter(
                    community=community, user=user, role="MEMBER"
                ).exists():
                    if self._try(
                        promote_member,
                        actor=leader,
                        community=community,
                        target_username=user.username,
                    ):
                        self._count("admins promoted")
            # Member states: one silenced and one banned person, on purpose.
            for target_comm, name, state in personas.MODERATED_MEMBERS:
                target = self.by_username.get(name)
                if target_comm != commname or target is None:
                    continue
                row = CommunityMember.objects.filter(community=community, user=target).first()
                if row and row.current_state == MemberState.ACTIVE:
                    if self._try(
                        moderate_member,
                        actor=leader,
                        community=community,
                        target_username=name,
                        new_state=MemberState[state],
                    ):
                        self._count(f"members {state.lower()}")

    def _community_customization(self) -> None:
        eligible = list(
            CustomizationItem.objects.filter(
                scope__in=("COMMUNITY", "BOTH"), is_active=True
            ).order_by("price", "pk")
        )
        for community, leader, _theme in self.communities:
            self.rng = self._rng("community-items", community.commname)
            if CommunityInventoryItem.objects.filter(community=community).exists():
                continue
            for item in self.rng.sample(eligible, k=min(2, len(eligible))):
                if self._try(purchase_community_item, actor=leader, community=community, item=item):
                    self._count("community purchases")
                    self._try(
                        equip_community_customization,
                        actor=leader,
                        community=community,
                        slots={item.item_type.lower(): item.id},
                    )

    def _user_customization(self) -> None:
        eligible = list(
            CustomizationItem.objects.filter(
                scope__in=("USER", "BOTH"),
                is_active=True,
                price__lte=45,
                # the newer types (wallpaper, accent, section, badges) are placed on purpose by
                # `_customization_showcase`, so every variation shows up somewhere
                item_type__in=("AVATAR_FRAME", "PROFILE_THEME", "CHAT_BUBBLE", "NAME_COLOR"),
            ).order_by("price", "pk")
        )
        for user in self.users[: max(4, len(self.users) // 2)]:
            self.rng = self._rng("user-items", user.username)
            if UserInventoryItem.objects.filter(user=user).exists():
                continue
            for item in self.rng.sample(eligible, k=min(2, len(eligible))):
                if self._try(purchase_customization_item, user=user, item=item):
                    self._count("user purchases")
                    self._try(
                        equip_customization, user=user, slots={item.item_type.lower(): item.id}
                    )

    def _banners(self) -> None:
        """Give every community without a banner an offline-drawn one."""
        if not self.images.enabled:
            return
        for index, (community, leader, _theme) in enumerate(self.communities):
            if community.banner_photo:
                continue
            top, bottom = content.BANNER_COLORS[index % len(content.BANNER_COLORS)]
            updated = self._try(
                update_community,
                actor=leader,
                community=community,
                banner_photo=banner_image(f"banner_{community.commname}", top, bottom),
            )
            if updated:
                self._count("community banners")

    def _customization_showcase(self) -> None:
        """Every new customization option (wallpaper, accent, section, badges) on a few profiles.

        Profile `i` gets wallpaper `i`, accent `i`, section item `i` and up to three badges, all
        modulo the number of variations, so each variation shows up on at least one profile.
        """
        items = {
            kind: list(
                CustomizationItem.objects.filter(
                    item_type=kind, is_active=True, price__lte=60, scope__in=("USER", "BOTH")
                ).order_by("price", "code")
            )
            for kind in ("WALLPAPER", "ACCENT_COLOR", "SECTION", "BADGE", "NAME_COLOR")
        }
        team_badge = CustomizationItem.objects.filter(code=content.TEAM_BADGE_CODE).first()
        owners = self.users[: min(len(self.users), 6)]
        for index, user in enumerate(owners):
            if UserInventoryItem.objects.filter(user=user, item__item_type="ACCENT_COLOR").exists():
                continue
            self._ensure_balance(user, 450)
            chosen = []
            for kind in ("WALLPAPER", "ACCENT_COLOR", "SECTION"):
                if items[kind]:
                    chosen.append(items[kind][index % len(items[kind])])
            badges = items["BADGE"]
            wanted_badges = [badges[(index + k) % len(badges)] for k in range(min(3, len(badges)))]
            slots: dict[str, int] = {}
            for item in chosen:
                if self._try(purchase_customization_item, user=user, item=item):
                    self._count("user purchases")
                    slots[item.item_type.lower()] = item.id
            for slot, badge in zip(("badge", "badge_2", "badge_3"), wanted_badges, strict=False):
                if UserInventoryItem.objects.filter(user=user, item=badge).exists() or self._try(
                    purchase_customization_item, user=user, item=badge
                ):
                    slots[slot] = badge.id
            if index == 0 and team_badge is not None:
                # What staff do in the admin: hand out a badge that is not for sale.
                UserInventoryItem.objects.get_or_create(user=user, item=team_badge)
                slots["badge_3"] = team_badge.id
            if slots:
                # equip one slot at a time: a failure in one must not drop the others
                for slot, item_id in slots.items():
                    self._try(equip_customization, user=user, slots={slot: item_id})
            if "section" in slots:
                title, text = content.SECTION_BY_USER.get(
                    user.username, content.SECTION_TEXTS[index % len(content.SECTION_TEXTS)]
                )
                self._try(update_profile_section, user=user, title=title, text=text)
                self._count("profile sections")

    def _posts(self) -> None:
        self.posts = []
        self.post_entry: dict[int, tuple[dict, dict, str | None]] = {}
        communities = {c.commname: c for c, _l, _t in self.communities}
        for persona in self.personas:
            user = self.by_username[persona["username"]]
            for position, entry in enumerate(self._entries(persona)):
                self.rng = self._rng("post", user.username, position)
                # A community that was not created (fewer --communities) becomes a profile post.
                community = communities.get(entry["community"]) if entry["community"] else None
                existing = Bubblegram.objects.filter(
                    user=user, community=community, text=entry["text"]
                ).first()
                if existing:
                    self.posts.append(existing)
                    continue
                pet_name, files = None, []
                if entry["pet"]:
                    pet_name, pool = self._pet(persona, entry["pet"])
                    files = [
                        f for f in (self.images.take(pool) for _ in range(entry["photos"])) if f
                    ]
                post = self._try(
                    create_bubblegram,
                    author=user,
                    type="MEDIA" if files else "TEXT",
                    text=entry["text"],
                    community=community,
                    media_files=files or None,
                )
                if post:
                    self.posts.append(post)
                    self.new["posts"].append(post)
                    self.post_entry[post.pk] = (persona, entry, pet_name)
                    self._count("bubblegrams")

    def _can_interact(self, user, post) -> bool:
        if user.pk == post.user_id:
            return False
        return self._can_comment(user, post)

    def _can_comment(self, user, post) -> bool:
        if post.community_id is None:
            return True
        return CommunityMember.objects.filter(
            community_id=post.community_id, user=user, current_state="ACTIVE"
        ).exists()

    def _comment(self, post, author, text, parent=None):
        if Comment.objects.filter(bubblegram=post, user=author, text=text).exists():
            return None
        comment = self._try(
            create_comment, author=author, bubblegram=post, text=text, parent=parent
        )
        if comment:
            self.new["comments"].append(comment)
            self._count("comments")
        return comment

    def _interactions(self) -> None:
        for post in self.new["posts"]:
            self.rng = self._rng("interactions", post.user.username, post.text)
            persona, entry, pet_name = self.post_entry.get(post.pk, (None, None, None))
            candidates = [u for u in self.users if self._can_interact(u, post)]
            made: list[Comment] = []
            if entry and entry["thread"]:
                # A written conversation: replies point to the comment they answer.
                created: dict[int, Comment] = {}
                for index, item in enumerate(entry["thread"]):
                    author = self.by_username.get(item[0])
                    parent_index = item[2] if len(item) > 2 else None
                    parent = created.get(parent_index) if parent_index is not None else None
                    if author is None or not self._can_comment(author, post):
                        continue
                    if parent_index is not None and parent is None:
                        continue
                    comment = self._comment(post, author, item[1], parent)
                    if comment:
                        created[index] = comment
                        made.append(comment)
            elif candidates and pet_name:
                # A photo: a few people react in their own voice; the author sometimes answers.
                count = self.rng.randint(0, min(self.comments_per_post, len(candidates)))
                first = None
                for author in self.rng.sample(candidates, k=count):
                    voice = self._persona(author.username)
                    text = self.rng.choice(voice["reactions"]).format(pet=pet_name)
                    comment = self._comment(post, author, text)
                    if comment:
                        made.append(comment)
                        first = first or comment
                if first and self.rng.random() < 0.6:
                    reply = self._comment(
                        post, post.user, self.rng.choice(persona["replies"]), first
                    )
                    if reply:
                        made.append(reply)
            for donor in self.rng.sample(
                candidates, k=min(len(candidates), self.rng.randint(0, 6))
            ):
                support = self._try(support_bubblegram, donor=donor, bubblegram=post)
                if support:
                    self.new["post_supports"].append(support)
                    self._count("bubblegram supports")
            for comment in made:
                for donor in self.rng.sample(
                    candidates, k=min(len(candidates), self.rng.randint(0, 2))
                ):
                    if donor.pk == comment.user_id:
                        continue
                    support = self._try(support_comment, donor=donor, comment=comment)
                    if support:
                        self.new["comment_supports"].append(support)
                        self._count("comment supports")

    def _bubblepops(self) -> None:
        for persona in self.personas:
            user = self.by_username[persona["username"]]
            self.rng = self._rng("pop", user.username)
            if (
                not persona["pets"]
                or Bubblepop.objects.filter(user=user, expires_at__gt=self.now).exists()
            ):
                continue
            _, pool = self._pet(persona, next(iter(persona["pets"])))
            image = self.images.take(pool)
            if image is None:
                continue
            pop = self._try(
                create_bubblepop,
                author=user,
                image=image,
                duration_hours=self.rng.choice((4, 12, 24, 48)),
                description=self.rng.choice(persona["pops"]),
            )
            if pop:
                self.new["pops"].append(pop)
                self._count("bubblepops")
        # Expired bubblepops (no service creates them) so the cleanup job has something to remove.
        existing_expired = Bubblepop.objects.filter(
            user__in=self.users, expires_at__lte=self.now
        ).count()
        for n in range(max(0, self.expired_bubblepops - existing_expired)):
            self.rng = self._rng("expired-pop", existing_expired, n)
            image = self.images.pick("both", self.rng)
            if image is None:
                break
            created = self.now - timedelta(hours=self.rng.uniform(30, 60))
            pop = Bubblepop.objects.create(
                user=self.rng.choice(self.users),
                image=image,
                description="Expirado (demo da limpeza)",
                created_at=created,
                expires_at=created + timedelta(hours=self.rng.choice((4, 6, 12))),
            )
            self.new["pops"].append(pop)
            self._count("expired bubblepops")

    def _letters(self) -> None:
        for sender_name, recipient_name, text, reply_text in stories.LETTERS:
            sender, recipient = (
                self.by_username.get(sender_name),
                self.by_username.get(recipient_name),
            )
            if sender is None or recipient is None:
                continue
            if Letter.objects.filter(sender=sender, recipient=recipient, text=text).exists():
                continue
            letter = self._try(send_letter, sender=sender, recipient=recipient, text=text)
            if not letter:
                continue
            self.new["letters"].append(letter)
            self._count("letters")
            reply = self._try(
                send_letter, sender=recipient, recipient=sender, text=reply_text, reply_to=letter
            )
            if reply:
                self.new["letters"].append(reply)
                self._count("letter replies")

    def _reports(self) -> None:
        targets: list[tuple[str, str]] = [
            (ReportTargetType.BUBBLEGRAM, str(p.pk)) for p in self.new["posts"][:6]
        ]
        targets += [(ReportTargetType.COMMENT, str(c.pk)) for c in self.new["comments"][:3]]
        targets += [(ReportTargetType.USER, str(u.pk)) for u in self.users[-2:]]
        targets += [(ReportTargetType.COMMUNITY, c.commname) for c, _l, _t in self.communities[-1:]]
        if not self.new["posts"]:
            return
        reasons = [r for r, _label in ReportReason.choices]
        statuses = [None, ReportStatus.INVESTIGATING, ReportStatus.RESOLVED, ReportStatus.DISMISSED]
        for position, (target_type, target_id) in enumerate(targets[: max(3, self.n_users // 3)]):
            # Keyed by position, not by id: ids differ between databases, the choices must not.
            self.rng = self._rng("report", target_type, position)
            reporter = self.rng.choice([u for u in self.users if str(u.pk) != target_id])
            if Report.objects.filter(
                reporter=reporter, target_type=target_type, target_id=target_id
            ).exists():
                continue
            report = self._try(
                file_report,
                reporter=reporter,
                target_type=target_type,
                target_id=target_id,
                reason=self.rng.choice(reasons),
                description=self.rng.choice(content.REPORT_NOTES),
            )
            if not report:
                continue
            self.new["reports"].append(report)
            self._remember("reports", report.pk)
            self._count("reports")
            status = statuses[position % len(statuses)]  # pending first, then the other states
            if status:
                self._try(
                    review_report,
                    reviewer=self.admin,
                    report=report,
                    status=status,
                    resolution_notes="Analisado na demonstração.",
                )

    def _moderation_showcase(self) -> None:
        """Accounts and communities in every administration state, to try the moderation screens.

        Done once: the deleted account and community change their handles, so the manifest
        (not the handle) tells whether a previous run already created them.
        """
        special = self.manifest["special"]
        reasons = {
            "suspended": "Publicações repetidas (spam) nas comunidades.",
            "banned": "Assédio a outros tutores nas comunidades.",
        }
        for role, (username, name) in content.SHOWCASE_USERS.items():
            if role in special:
                continue
            if User.objects.filter(username=username).exists():
                continue
            user, created = self._register(
                username,
                name,
                avatar={"suspended": "fish:60", "banned": "fish:330", "deleted": "fish:120"}[role],
                bio="Conta de demonstração.",
            )
            if not created:
                continue
            special[role] = user.pk
            self._ensure_balance(user, 120)
            self._try(
                create_bubblegram,
                author=user,
                type="TEXT",
                text=content.SHOWCASE_USER_POSTS[role],
                community=None,
                media_files=None,
            )
            if role == "suspended":
                suspend_user(
                    actor=self.admin, user=user, duration_hours=24 * 7, reason=reasons[role]
                )
            elif role == "banned":
                ban_user(actor=self.admin, user=user, reason=reasons[role])
            else:
                delete_account(user=user, password=PASSWORD)  # content stays as "Conta excluída"
            self._count(f"{role} accounts")

        leaders = list(reversed(self.users))
        for index, (commname, name, action, description) in enumerate(content.SHOWCASE_COMMUNITIES):
            if action in special or Community.objects.filter(commname=commname).exists():
                continue
            leader = leaders[index % len(leaders)]
            self._ensure_balance(leader, FOUNDING_RESERVE + 100)
            community = self._try(
                create_community,
                creator=leader,
                commname=commname,
                name=name,
                description=description,
                guidelines="Comunidade de demonstração das telas de moderação.",
            )
            if community is None:
                continue
            self._remember("communities", community.pk)
            self.new["communities"].append(community)  # back-dated with the others
            special[action] = community.pk
            self._count("showcase communities")
            for member in self.users[:2]:
                if member.pk != leader.pk:
                    self._try(join_community, user=member, community=community)
            self._try(
                create_bubblegram,
                author=leader,
                type="TEXT",
                text=content.SHOWCASE_COMMUNITY_POSTS[action],
                community=community,
                media_files=None,
            )
            if action == "suspend":
                suspend_community(
                    actor=self.admin,
                    community=community,
                    duration_hours=24 * 10,
                    reason="Muitas discussões fora do tema.",
                )
            elif action == "ban":
                block_community(
                    actor=self.admin, community=community, reason="Conteúdo contra as regras."
                )
            else:
                delete_community(actor=leader, community=community, confirm_commname=commname)

    def _backdate(self) -> None:
        """Spread timestamps over the recent past, keeping every event after what it depends on."""
        now, days = self.now, self.days
        self.rng = self._rng("backdate", len(self.new["users"]), len(self.new["posts"]))
        user_created: dict[int, object] = {}
        for user in self.new["users"]:
            t = now - timedelta(days=self.rng.uniform(days * 0.8, days))
            User.objects.filter(pk=user.pk).update(created_at=t)
            user_created[user.pk] = t
        community_created: dict[int, object] = {}
        for community in self.new["communities"]:
            t = now - timedelta(days=self.rng.uniform(days * 0.5, days * 0.8))
            Community.objects.filter(pk=community.pk).update(created_at=t)
            community_created[community.pk] = t
        for row in self.new["members"]:
            lower = community_created.get(row.community_id) or self.now - timedelta(days=days)
            CommunityMember.objects.filter(pk=row.pk).update(joined_at=self._past(lower))
        for row in self.new["follows"]:
            UserConnection.objects.filter(pk=row.pk).update(
                created_at=self._past(now - timedelta(days=days * 0.8))
            )
        post_time: dict[int, object] = {}
        # The feed's "popular" suggestions only look at the last 24 hours, so a few supported
        # personal posts are made recent: without them the demo would never show a suggestion.
        supported = dict(
            Bubblegram.objects.filter(
                pk__in=[p.pk for p in self.new["posts"]], community__isnull=True, soap_count__gt=0
            ).values_list("pk", "soap_count")
        )
        hot = set(sorted(supported, key=lambda pk: (-supported[pk], pk))[:5])
        for post in self.new["posts"]:
            lower = max(
                user_created.get(post.user_id, now - timedelta(days=days)),
                community_created.get(post.community_id, now - timedelta(days=days))
                if post.community_id
                else now - timedelta(days=days),
            )
            t = self._past(lower, now - timedelta(hours=1))
            if post.pk in hot:
                t = now - timedelta(hours=self.rng.uniform(2, 20))
            Bubblegram.objects.filter(pk=post.pk).update(published_at=t)
            post_time[post.pk] = t
        comment_time: dict[int, object] = {}
        for comment in sorted(
            self.new["comments"], key=lambda c: c.pk
        ):  # parents are created first
            lower = (
                comment_time.get(comment.parent_id)
                or post_time.get(comment.bubblegram_id)
                or now - timedelta(days=days)
            )
            t = self._past(lower, now - timedelta(minutes=10))
            Comment.objects.filter(pk=comment.pk).update(published_at=t)
            comment_time[comment.pk] = t
        for support in self.new["post_supports"]:
            BubblegramSupport.objects.filter(pk=support.pk).update(
                created_at=self._past(
                    post_time.get(support.bubblegram_id, now - timedelta(days=1)),
                    now - timedelta(minutes=5),
                )
            )
        for support in self.new["comment_supports"]:
            CommentSupport.objects.filter(pk=support.pk).update(
                created_at=self._past(
                    comment_time.get(support.comment_id, now - timedelta(days=1)),
                    now - timedelta(minutes=5),
                )
            )
        letter_time: dict[int, object] = {}
        for letter in sorted(self.new["letters"], key=lambda x: x.pk):
            lower = letter_time.get(letter.reply_to_id) or now - timedelta(days=days * 0.6)
            t = self._past(lower, now - timedelta(minutes=20))
            Letter.objects.filter(pk=letter.pk).update(sent_at=t)
            letter_time[letter.pk] = t
        for report in self.new["reports"]:
            Report.objects.filter(pk=report.pk).update(
                created_at=self._past(now - timedelta(days=10))
            )
        # Make a few users look "online" so the passive soap job has someone to pay.
        recent = self.users[: max(2, len(self.users) // 3)]
        User.objects.filter(pk__in=[u.pk for u in recent]).update(last_seen_at=now)

    def _finish(self) -> None:
        for log_id in AuditLog.objects.filter(id__gt=self.audit_before).values_list(
            "id", flat=True
        ):
            self._remember("audit_logs", log_id)
        self.manifest["db"] = connection.settings_dict["NAME"]
        self.manifest["seed"] = self.seed
        save_manifest(self.cache_dir, self.manifest)

    def credentials(self) -> list[tuple[str, str, str]]:
        sample = [u for u in self.users if u != self.moderator][:3]
        showcase = [
            ("Suspensa (pode ler, não publica)", content.SHOWCASE_USERS["suspended"][0], PASSWORD),
            ("Banido (o login mostra o motivo)", content.SHOWCASE_USERS["banned"][0], PASSWORD),
        ]
        return [
            ("Administrador (acessa /admin/ e /moderation)", ADMIN_USERNAME, PASSWORD),
            ("Moderador de comunidades", MODERATOR_USERNAME, PASSWORD),
            *[("Usuário", u.username, PASSWORD) for u in sample],
            *showcase,
        ]


def reset_demo(cache_dir: Path, log=print) -> dict[str, int]:
    """Delete only what the seed recorded in its manifest (plus everything that hangs from it)."""
    manifest = load_manifest(cache_dir)
    if manifest.get("db") != connection.settings_dict["NAME"] or not (
        manifest["users"] or manifest["communities"]
    ):
        log("Nothing to reset: the seed manifest is empty or belongs to another database.")
        return {}

    users = User.objects.filter(pk__in=manifest["users"])
    communities = Community.objects.filter(pk__in=manifest["communities"])
    counts = {"users": users.count(), "communities": communities.count()}

    files = set()
    files.update(users.exclude(profile_photo="").values_list("profile_photo", flat=True))
    files.update(communities.exclude(community_photo="").values_list("community_photo", flat=True))
    files.update(communities.exclude(banner_photo="").values_list("banner_photo", flat=True))
    files.update(
        BubblegramMedia.objects.filter(
            Q(bubblegram__user__in=users) | Q(bubblegram__community__in=communities)
        ).values_list("media", flat=True)
    )
    files.update(
        Bubblepop.objects.filter(user__in=users).exclude(image="").values_list("image", flat=True)
    )
    files.update(
        Letter.objects.filter(Q(sender__in=users) | Q(recipient__in=users))
        .exclude(image="")
        .values_list("image", flat=True)
    )

    with transaction.atomic():
        wallets = Wallet.objects.filter(Q(user__in=users) | Q(community__in=communities))
        UserInventoryItem.objects.filter(user__in=users).delete()
        CommunityInventoryItem.objects.filter(community__in=communities).delete()
        # The ledger is append-only for the application. Only here, and only for the wallets of
        # accounts this seed created in the demo database, it is removed with the accounts.
        counts["ledger rows"] = SoapTransaction.objects.filter(wallet__in=wallets)._raw_delete(
            using="default"
        )
        wallets.delete()
        Report.objects.filter(pk__in=manifest["reports"]).delete()
        AuditLog.objects.filter(pk__in=manifest["audit_logs"]).delete()
        users.delete()
        communities.delete()
        removable = CustomizationItem.objects.filter(
            pk__in=manifest["items"], user_holdings__isnull=True, community_holdings__isnull=True
        )
        # Only the images of items that are really removed (a manual holder keeps its item).
        files.update(removable.exclude(image="").values_list("image", flat=True))
        counts["items"] = removable.delete()[0]

    removed = 0
    for name in files:
        if name and default_storage.exists(name):
            default_storage.delete(name)
            removed += 1
    counts["media files"] = removed
    _manifest_path(cache_dir).unlink(missing_ok=True)
    return counts
