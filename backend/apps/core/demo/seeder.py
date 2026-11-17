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
from apps.accounts.services import follow_user, register_user
from apps.communities.models import Community, CommunityMember, MemberState
from apps.communities.services import (
    create_community,
    join_community,
    moderate_member,
    promote_member,
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
from apps.core.demo import content
from apps.core.demo.images import ImageLibrary
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
from apps.moderation.services import admin_adjust_soap, file_report, review_report
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
        self.n_users = max(4, users)
        self.n_communities = max(1, min(communities, len(content.COMMUNITY_THEMES)))
        self.posts_per_user = max(0, posts_per_user)
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
        return lower + timedelta(seconds=self.rng.uniform(0, span))

    # ------------------------------------------------------------------ steps
    def run(self) -> dict:
        self.images.prepare()
        self._ensure_catalog()
        self._ensure_people()
        self._follows()
        self._communities()
        self._memberships()
        self._community_customization()
        self._user_customization()
        self._posts()
        self._interactions()
        self._bubblepops()
        self._letters()
        self._reports()
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

    def _identity(self, index: int, taken: set[str]) -> tuple[str, str]:
        first, last = self.fake.first_name(), self.fake.last_name()
        base = f"{slugify(first)}_{slugify(last)}".replace("-", "_")[:26] or f"pet_tutor_{index}"
        username, n = base, 1
        while username in taken or len(username) < 3:
            n += 1
            username = f"{base}{n}"
        taken.add(username)
        return f"{first} {last}", username

    def _register(
        self, username: str, name: str, *, photo_species: str, bio: str, is_staff: bool = False
    ):
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
            profile_photo=self.images.pick(photo_species, self.rng),
        )
        if is_staff:
            User.objects.filter(pk=user.pk).update(is_staff=True, is_superuser=True)
            user.refresh_from_db()
        self._remember("users", user.pk)
        self.new["users"].append(user)
        self._count("users")
        return user, True

    def _ensure_people(self) -> None:
        self.admin, admin_created = self._register(
            ADMIN_USERNAME,
            "Admin Demo",
            photo_species="cat",
            bio="Administração da demonstração.",
            is_staff=True,
        )
        # The admin funds everyone through audited soap adjustments. Funding happens once, when
        # an account is created: running the seed again must not hand out more soap.
        if admin_created:
            self._ensure_balance(self.admin, 2000, "Demo seed funding")
        self.moderator, moderator_created = self._register(
            MODERATOR_USERNAME,
            "Moderador Demo",
            photo_species="dog",
            bio="Moderador das comunidades de demonstração.",
        )
        taken = {ADMIN_USERNAME, MODERATOR_USERNAME}
        self.users = []
        created_now = {self.moderator.pk} if moderator_created else set()
        for i in range(self.n_users - 1):  # the moderator counts as one of the users
            name, username = self._identity(i, taken)
            bio = content.BIOS[i % len(content.BIOS)]
            user, created = self._register(
                username, name, photo_species=self.rng.choice(("cat", "dog")), bio=bio
            )
            self.users.append(user)
            if created:
                created_now.add(user.pk)
        self.users.insert(0, self.moderator)
        for index, user in enumerate(self.users):
            if user.pk not in created_now:
                continue
            # Founders (first users) get enough soap to found a community and publish.
            self._ensure_balance(
                user, FOUNDING_RESERVE + 300 if index < self.n_communities else 250
            )

    def _follows(self) -> None:
        for user in self.users:
            self.rng = self._rng("follows", user.username)
            others = [u for u in self.users if u.pk != user.pk]
            for target in self.rng.sample(others, k=min(len(others), self.rng.randint(3, 6))):
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
            leader = self.users[index % len(self.users)]
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
        for index, (community, leader, _theme) in enumerate(self.communities):
            self.rng = self._rng("members", community.commname)
            members = [u for u in self.users if u.pk != leader.pk]
            chosen = [u for u in members if u == self.moderator or self.rng.random() < 0.6]
            for user in chosen:
                if CommunityMember.objects.filter(community=community, user=user).exists():
                    continue
                row = self._try(join_community, user=user, community=community)
                if row:
                    self.new["members"].append(row)
                    self._count("memberships")
            community.refresh_from_db()
            # Roles: the moderator is an admin of every other community, plus one more admin.
            admins = [self.moderator] if (index % 2 == 0 and self.moderator.pk != leader.pk) else []
            extra = [u for u in chosen if u not in admins and u.pk != leader.pk]
            if extra:
                admins.append(self.rng.choice(extra))
            for user in admins:
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
            # Show the member states in one community each.
            plain = [
                m
                for m in CommunityMember.objects.filter(
                    community=community, role="MEMBER", current_state=MemberState.ACTIVE
                )
                .select_related("user")
                .order_by("pk")
            ]
            if (
                plain
                and index in (1, 2)
                and not CommunityMember.objects.filter(community=community)
                .exclude(current_state="ACTIVE")
                .exists()
            ):
                target = self.rng.choice(plain)
                state = MemberState.SILENCED if index == 1 else MemberState.BANNED
                if self._try(
                    moderate_member,
                    actor=leader,
                    community=community,
                    target_username=target.user.username,
                    new_state=state,
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
                scope__in=("USER", "BOTH"), is_active=True, price__lte=45
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

    def _posts(self) -> None:
        self.posts = []
        index = 0
        memberships = {
            u.pk: [
                m.community
                for m in CommunityMember.objects.filter(user=u, current_state="ACTIVE")
                .select_related("community")
                .order_by("community_id")
            ]
            for u in self.users
        }
        theme_species = {c.pk: t["species"] for c, _l, t in self.communities}
        for user in self.users:
            for _k in range(self.posts_per_user):
                self.rng = self._rng("post", user.username, index)
                text = content.CAPTIONS[index % len(content.CAPTIONS)]
                index += 1
                communities = memberships[user.pk]
                community = (
                    self.rng.choice(communities)
                    if communities and self.rng.random() < 0.35
                    else None
                )
                species = (
                    theme_species.get(community.pk, "both")
                    if community
                    else self.rng.choice(("cat", "dog"))
                )
                existing = Bubblegram.objects.filter(
                    user=user, community=community, text=text
                ).first()
                if existing:
                    self.posts.append(existing)
                    continue
                files = [
                    f
                    for f in (
                        self.images.pick(species, self.rng)
                        for _ in range(self.rng.choice((1, 1, 2)))
                    )
                    if f
                ]
                with_images = files and self.rng.random() < 0.75
                post = self._try(
                    create_bubblegram,
                    author=user,
                    type="MEDIA" if with_images else "TEXT",
                    text=text,
                    community=community,
                    media_files=files if with_images else None,
                )
                if post:
                    self.posts.append(post)
                    self.new["posts"].append(post)
                    self._count("bubblegrams")

    def _can_interact(self, user, post) -> bool:
        if user.pk == post.user_id:
            return False
        if post.community_id is None:
            return True
        return CommunityMember.objects.filter(
            community_id=post.community_id, user=user, current_state="ACTIVE"
        ).exists()

    def _interactions(self) -> None:
        for post in self.new["posts"]:
            self.rng = self._rng("interactions", post.user.username, post.text)
            candidates = [u for u in self.users if self._can_interact(u, post)]
            if not candidates:
                continue
            made: list[Comment] = []
            for _ in range(self.rng.randint(0, self.comments_per_post)):
                author = self.rng.choice(candidates)
                parent = self.rng.choice(made) if made and self.rng.random() < 0.3 else None
                text = self.rng.choice(content.REPLIES if parent else content.COMMENTS)
                if Comment.objects.filter(bubblegram=post, user=author, text=text).exists():
                    continue
                comment = self._try(
                    create_comment, author=author, bubblegram=post, text=text, parent=parent
                )
                if comment:
                    made.append(comment)
                    self.new["comments"].append(comment)
                    self._count("comments")
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
        for user in self.users[: max(3, len(self.users) // 2)]:
            self.rng = self._rng("pop", user.username)
            if Bubblepop.objects.filter(user=user, expires_at__gt=self.now).exists():
                continue
            image = self.images.pick(self.rng.choice(("cat", "dog")), self.rng)
            if image is None:
                continue
            pop = self._try(
                create_bubblepop,
                author=user,
                image=image,
                duration_hours=self.rng.choice((4, 12, 24, 48)),
                description=self.rng.choice(content.BUBBLEPOP_NOTES),
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
        pairs = list(
            UserConnection.objects.filter(follower__in=self.users, followed__in=self.users)
            .select_related("follower", "followed")
            .order_by("follower_id", "followed_id")
        )
        self._rng("letter-pairs").shuffle(pairs)
        for connection_row in pairs[: max(4, len(self.users))]:
            sender, recipient = connection_row.follower, connection_row.followed
            self.rng = self._rng("letter", sender.username, recipient.username)
            text = self.rng.choice(content.LETTERS)
            if Letter.objects.filter(sender=sender, recipient=recipient, text=text).exists():
                continue
            image = self.images.pick("both", self.rng) if self.rng.random() < 0.25 else None
            letter = self._try(
                send_letter, sender=sender, recipient=recipient, text=text, image=image
            )
            if not letter:
                continue
            self.new["letters"].append(letter)
            self._count("letters")
            if self.rng.random() < 0.4:
                reply = self._try(
                    send_letter,
                    sender=recipient,
                    recipient=sender,
                    text=self.rng.choice(content.LETTER_REPLIES),
                    reply_to=letter,
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
        for target_type, target_id in targets[: max(3, self.n_users // 3)]:
            self.rng = self._rng("report", target_type, target_id)
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
            status = self.rng.choice(statuses)
            if status:
                self._try(
                    review_report,
                    reviewer=self.admin,
                    report=report,
                    status=status,
                    resolution_notes="Analisado na demonstração.",
                )

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
        for post in self.new["posts"]:
            lower = max(
                user_created.get(post.user_id, now - timedelta(days=days)),
                community_created.get(post.community_id, now - timedelta(days=days))
                if post.community_id
                else now - timedelta(days=days),
            )
            t = self._past(lower, now - timedelta(hours=1))
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
        return [
            ("Administrador (acessa /admin/)", ADMIN_USERNAME, PASSWORD),
            ("Moderador de comunidades", MODERATOR_USERNAME, PASSWORD),
            *[("Usuário", u.username, PASSWORD) for u in sample],
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
        counts["items"] = CustomizationItem.objects.filter(
            pk__in=manifest["items"], user_holdings__isnull=True, community_holdings__isnull=True
        ).delete()[0]

    removed = 0
    for name in files:
        if name and default_storage.exists(name):
            default_storage.delete(name)
            removed += 1
    counts["media files"] = removed
    _manifest_path(cache_dir).unlink(missing_ok=True)
    return counts
