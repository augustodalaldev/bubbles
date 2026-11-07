from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from apps.accounts.tests.factories import UserFactory
from apps.communities.models import MemberRole, MemberState
from apps.communities.tests.factories import CommunityFactory, CommunityMemberFactory
from apps.content.models import (
    Bubblegram,
    BubblegramSupport,
    BubblegramType,
    Bubblepop,
    Comment,
    CommentSupport,
)
from apps.content.services import (
    create_bubblegram,
    create_bubblepop,
    create_comment,
    delete_bubblegram,
    delete_bubblepop,
    delete_comment,
    support_bubblegram,
    support_comment,
)
from apps.core.exceptions import DomainError
from apps.economy.exceptions import InsufficientSoap
from apps.economy.models import ActionType, SoapTransaction, Wallet

pytestmark = pytest.mark.django_db


def create_test_image(name="test.jpg", color="red"):
    file = BytesIO()
    image = Image.new("RGBA", size=(50, 50), color=color)
    image.save(file, "png")
    file.seek(0)
    return SimpleUploadedFile(name, file.read(), content_type="image/png")


def test_create_personal_text_bubblegram():
    author = UserFactory()
    Wallet.objects.create(user=author, soap_balance=20)

    post = create_bubblegram(
        author=author,
        type=BubblegramType.TEXT,
        text="My first thought on Bubbles!",
    )

    assert post.pk is not None
    assert post.user == author
    assert post.community is None
    assert post.text == "My first thought on Bubbles!"
    assert post.type == BubblegramType.TEXT
    assert post.media.count() == 0

    author.wallet.refresh_from_db()
    assert author.wallet.soap_balance == 10

    tx = SoapTransaction.objects.get(wallet=author.wallet, action_type=ActionType.DEBIT_BUBBLEGRAM)
    assert tx.amount == -10
    assert tx.balance_after == 10


def test_create_personal_media_bubblegram_optional_text():
    author = UserFactory()
    Wallet.objects.create(user=author, soap_balance=50)

    img1 = create_test_image("img1.png")
    img2 = create_test_image("img2.png")

    # Text is optional for media posts
    post = create_bubblegram(
        author=author,
        type=BubblegramType.MEDIA,
        text="",
        media_files=[img1, img2],
    )

    assert post.pk is not None
    assert post.type == BubblegramType.MEDIA
    assert post.text == ""
    assert post.media.count() == 2

    author.wallet.refresh_from_db()
    assert author.wallet.soap_balance == 40


def test_create_bubblegram_insufficient_soap():
    author = UserFactory()
    Wallet.objects.create(user=author, soap_balance=5)  # costs 10

    with pytest.raises(InsufficientSoap):
        create_bubblegram(
            author=author,
            type=BubblegramType.TEXT,
            text="Cannot afford this post",
        )

    assert not Bubblegram.objects.filter(user=author).exists()


def test_create_bubblegram_validations():
    author = UserFactory()
    Wallet.objects.create(user=author, soap_balance=50)

    # TEXT requires text
    with pytest.raises(DomainError) as exc_info:
        create_bubblegram(author=author, type=BubblegramType.TEXT, text="")
    assert exc_info.value.code == "text_required"

    # TEXT rejects media
    with pytest.raises(DomainError) as exc_info:
        create_bubblegram(
            author=author,
            type=BubblegramType.TEXT,
            text="Valid",
            media_files=[create_test_image()],
        )
    assert exc_info.value.code == "media_not_allowed"

    # MEDIA requires at least 1 image
    with pytest.raises(DomainError) as exc_info:
        create_bubblegram(author=author, type=BubblegramType.MEDIA, media_files=[])
    assert exc_info.value.code == "media_required"

    # MEDIA rejects > 4 images
    with pytest.raises(DomainError) as exc_info:
        create_bubblegram(
            author=author,
            type=BubblegramType.MEDIA,
            media_files=[create_test_image(f"i{i}.png") for i in range(5)],
        )
    assert exc_info.value.code == "too_many_media"


def test_create_community_bubblegram():
    author = UserFactory()
    community = CommunityFactory()
    CommunityMemberFactory(
        community=community, user=author, role=MemberRole.MEMBER, current_state=MemberState.ACTIVE
    )
    Wallet.objects.create(user=author, soap_balance=30)

    post = create_bubblegram(
        author=author,
        type=BubblegramType.TEXT,
        text="Hello community members!",
        community=community,
    )

    assert post.community == community
    author.wallet.refresh_from_db()
    assert author.wallet.soap_balance == 20


def test_create_community_bubblegram_silenced_or_banned_blocked():
    author = UserFactory()
    community = CommunityFactory()
    CommunityMemberFactory(
        community=community,
        user=author,
        role=MemberRole.MEMBER,
        current_state=MemberState.SILENCED,
    )
    Wallet.objects.create(user=author, soap_balance=30)

    with pytest.raises(DomainError) as exc_info:
        create_bubblegram(
            author=author,
            type=BubblegramType.TEXT,
            text="I am silenced",
            community=community,
        )
    assert exc_info.value.code == "permission_denied"


def test_create_community_bubblegram_archived_blocked():
    author = UserFactory()
    community = CommunityFactory(archived_at=pytest.importorskip("django.utils.timezone").now())
    CommunityMemberFactory(
        community=community, user=author, role=MemberRole.MEMBER, current_state=MemberState.ACTIVE
    )
    Wallet.objects.create(user=author, soap_balance=30)

    with pytest.raises(DomainError) as exc_info:
        create_bubblegram(
            author=author,
            type=BubblegramType.TEXT,
            text="Post in archived community",
            community=community,
        )
    assert exc_info.value.code == "community_archived"


def test_delete_bubblegram_by_author_no_refund():
    author = UserFactory()
    supporter = UserFactory()
    Wallet.objects.create(user=author, soap_balance=100)
    Wallet.objects.create(user=supporter, soap_balance=50)

    post = Bubblegram.objects.create(
        user=author, text="Post with support", type=BubblegramType.TEXT
    )

    # Support given to post
    support = BubblegramSupport.objects.create(bubblegram=post, donor=supporter)
    tx = SoapTransaction.objects.create(
        wallet=author.wallet,
        amount=1,
        action_type=ActionType.CREDIT_AUTHOR,
        balance_after=101,
        bubblegram_support=support,
        idempotency_key="supp_tx_1",
    )

    delete_bubblegram(actor=author, bubblegram=post)

    assert not Bubblegram.objects.filter(pk=post.pk).exists()
    assert not BubblegramSupport.objects.filter(pk=support.pk).exists()

    # Invariant: Supports are final, no refund, ledger row kept with origin SET_NULL
    tx.refresh_from_db()
    assert tx.bubblegram_support is None
    assert tx.amount == 1
    supporter.wallet.refresh_from_db()
    assert supporter.wallet.soap_balance == 50  # supporter was NOT refunded


def test_delete_community_bubblegram_by_admin():
    author = UserFactory()
    admin = UserFactory()
    community = CommunityFactory()
    CommunityMemberFactory(
        community=community, user=author, role=MemberRole.MEMBER, current_state=MemberState.ACTIVE
    )
    CommunityMemberFactory(
        community=community,
        user=admin,
        role=MemberRole.COMM_ADMIN,
        current_state=MemberState.ACTIVE,
    )

    post = Bubblegram.objects.create(
        user=author, community=community, text="Spam post", type=BubblegramType.TEXT
    )

    delete_bubblegram(actor=admin, bubblegram=post)
    assert not Bubblegram.objects.filter(pk=post.pk).exists()


def test_delete_bubblegram_unauthorized_blocked():
    author = UserFactory()
    intruder = UserFactory()
    post = Bubblegram.objects.create(user=author, text="Private post", type=BubblegramType.TEXT)

    with pytest.raises(DomainError) as exc_info:
        delete_bubblegram(actor=intruder, bubblegram=post)
    assert exc_info.value.code == "permission_denied"


def test_create_comment_personal_post_success():
    author = UserFactory()
    commenter = UserFactory()
    post = Bubblegram.objects.create(user=author, text="Post text", type=BubblegramType.TEXT)

    comment = create_comment(author=commenter, bubblegram=post, text="Nice post!")
    assert comment.pk is not None
    assert comment.bubblegram == post
    assert comment.user == commenter
    assert comment.text == "Nice post!"
    assert comment.parent is None


def test_create_comment_reply_nested():
    author = UserFactory()
    commenter1 = UserFactory()
    commenter2 = UserFactory()
    post = Bubblegram.objects.create(user=author, text="Post text", type=BubblegramType.TEXT)

    root_comment = create_comment(author=commenter1, bubblegram=post, text="Top level")
    reply = create_comment(
        author=commenter2,
        bubblegram=post,
        text="Replying here",
        parent=root_comment,
    )

    assert reply.parent == root_comment
    assert reply.bubblegram == post


def test_create_comment_mismatched_parent_post_rejected():
    author = UserFactory()
    post1 = Bubblegram.objects.create(user=author, text="Post 1", type=BubblegramType.TEXT)
    post2 = Bubblegram.objects.create(user=author, text="Post 2", type=BubblegramType.TEXT)

    comment_on_post1 = create_comment(author=author, bubblegram=post1, text="On post 1")

    with pytest.raises(DomainError) as exc_info:
        create_comment(
            author=author,
            bubblegram=post2,
            text="Reply on wrong post",
            parent=comment_on_post1,
        )
    assert exc_info.value.code == "invalid_parent"


def test_create_comment_validation_empty_and_length():
    author = UserFactory()
    post = Bubblegram.objects.create(user=author, text="Post", type=BubblegramType.TEXT)

    with pytest.raises(DomainError) as exc_info:
        create_comment(author=author, bubblegram=post, text="   ")
    assert exc_info.value.code == "text_required"

    with pytest.raises(DomainError) as exc_info:
        create_comment(author=author, bubblegram=post, text="x" * 2001)
    assert exc_info.value.code == "text_too_long"


def test_create_comment_community_membership_rules():
    author = UserFactory()
    community = CommunityFactory()
    post = Bubblegram.objects.create(
        user=author, community=community, text="Comm post", type=BubblegramType.TEXT
    )

    non_member = UserFactory()
    with pytest.raises(DomainError) as exc_info:
        create_comment(author=non_member, bubblegram=post, text="Hello?")
    assert exc_info.value.code == "permission_denied"

    silenced_user = UserFactory()
    CommunityMemberFactory(
        community=community,
        user=silenced_user,
        role=MemberRole.MEMBER,
        current_state=MemberState.SILENCED,
    )
    with pytest.raises(DomainError) as exc_info:
        create_comment(author=silenced_user, bubblegram=post, text="I'm silenced")
    assert exc_info.value.code == "permission_denied"

    active_user = UserFactory()
    CommunityMemberFactory(
        community=community,
        user=active_user,
        role=MemberRole.MEMBER,
        current_state=MemberState.ACTIVE,
    )
    comment = create_comment(author=active_user, bubblegram=post, text="I can comment!")
    assert comment.pk is not None


def test_delete_comment_permissions():
    author = UserFactory()
    post_author = UserFactory()
    stranger = UserFactory()
    post = Bubblegram.objects.create(user=post_author, text="Post", type=BubblegramType.TEXT)
    comment = Comment.objects.create(bubblegram=post, user=author, text="A comment")

    # Stranger blocked
    with pytest.raises(DomainError) as exc_info:
        delete_comment(actor=stranger, comment=comment)
    assert exc_info.value.code == "permission_denied"

    # Post author can delete
    delete_comment(actor=post_author, comment=comment)
    assert not Comment.objects.filter(pk=comment.pk).exists()

    # Comment author can delete their own
    comment2 = Comment.objects.create(bubblegram=post, user=author, text="Another comment")
    delete_comment(actor=author, comment=comment2)
    assert not Comment.objects.filter(pk=comment2.pk).exists()


def test_delete_comment_preserves_support_ledger_and_cascades_replies():
    post_author = UserFactory()
    commenter = UserFactory()
    supporter = UserFactory()
    Wallet.objects.create(user=commenter, soap_balance=20)
    Wallet.objects.create(user=supporter, soap_balance=10)

    post = Bubblegram.objects.create(user=post_author, text="Post", type=BubblegramType.TEXT)
    root = Comment.objects.create(bubblegram=post, user=commenter, text="Root")
    child = Comment.objects.create(bubblegram=post, user=commenter, text="Child", parent=root)

    support = CommentSupport.objects.create(comment=root, donor=supporter)
    tx = SoapTransaction.objects.create(
        wallet=commenter.wallet,
        amount=1,
        action_type=ActionType.CREDIT_AUTHOR,
        balance_after=21,
        comment_support=support,
        idempotency_key="comm_supp_tx_1",
    )

    delete_comment(actor=commenter, comment=root)

    assert not Comment.objects.filter(pk=root.pk).exists()
    assert not Comment.objects.filter(pk=child.pk).exists()  # Child cascade deleted
    assert not CommentSupport.objects.filter(pk=support.pk).exists()

    # SoapTransaction preserved with SET_NULL
    tx.refresh_from_db()
    assert tx.comment_support is None
    assert tx.amount == 1
    supporter.wallet.refresh_from_db()
    assert supporter.wallet.soap_balance == 10  # No refund


def test_support_personal_bubblegram_transfers_soap_and_increments_counter():
    author = UserFactory()
    donor = UserFactory()
    Wallet.objects.create(user=author, soap_balance=20)
    Wallet.objects.create(user=donor, soap_balance=10)

    post = Bubblegram.objects.create(user=author, text="Great post", type=BubblegramType.TEXT)

    support = support_bubblegram(donor=donor, bubblegram=post)
    assert support.pk is not None
    assert support.bubblegram == post
    assert support.donor == donor

    # Author received +1, donor lost -1
    author.wallet.refresh_from_db()
    donor.wallet.refresh_from_db()
    assert author.wallet.soap_balance == 21
    assert donor.wallet.soap_balance == 9

    # Counter incremented
    post.refresh_from_db()
    assert post.soap_count == 1

    # Ledger origins linked
    donor_tx = SoapTransaction.objects.get(
        wallet=donor.wallet, action_type=ActionType.DEBIT_INTERACTION
    )
    assert donor_tx.amount == -1
    assert donor_tx.bubblegram_support == support

    author_tx = SoapTransaction.objects.get(
        wallet=author.wallet, action_type=ActionType.CREDIT_AUTHOR
    )
    assert author_tx.amount == 1
    assert author_tx.bubblegram_support == support


def test_support_community_bubblegram_credits_author_and_community():
    author = UserFactory()
    donor = UserFactory()
    community = CommunityFactory()
    Wallet.objects.create(user=author, soap_balance=10)
    Wallet.objects.create(user=donor, soap_balance=10)
    Wallet.objects.create(community=community, soap_balance=50)

    post = Bubblegram.objects.create(
        user=author, community=community, text="Comm post", type=BubblegramType.TEXT
    )

    support = support_bubblegram(donor=donor, bubblegram=post)
    assert support.pk is not None

    author.wallet.refresh_from_db()
    donor.wallet.refresh_from_db()
    community.wallet.refresh_from_db()

    assert donor.wallet.soap_balance == 9
    assert author.wallet.soap_balance == 11
    assert community.wallet.soap_balance == 51

    post.refresh_from_db()
    assert post.soap_count == 1

    comm_tx = SoapTransaction.objects.get(
        wallet=community.wallet, action_type=ActionType.CREDIT_COMMUNITY
    )
    assert comm_tx.amount == 1
    assert comm_tx.bubblegram_support == support


def test_support_bubblegram_self_support_rejected():
    author = UserFactory()
    Wallet.objects.create(user=author, soap_balance=10)
    post = Bubblegram.objects.create(user=author, text="Self post", type=BubblegramType.TEXT)

    with pytest.raises(DomainError) as exc_info:
        support_bubblegram(donor=author, bubblegram=post)
    assert exc_info.value.code == "self_support_not_allowed"


def test_support_bubblegram_duplicate_rejected():
    author = UserFactory()
    donor = UserFactory()
    Wallet.objects.create(user=author, soap_balance=10)
    Wallet.objects.create(user=donor, soap_balance=10)
    post = Bubblegram.objects.create(user=author, text="Post", type=BubblegramType.TEXT)

    support_bubblegram(donor=donor, bubblegram=post)

    with pytest.raises(DomainError) as exc_info:
        support_bubblegram(donor=donor, bubblegram=post)
    assert exc_info.value.code == "already_supported"


def test_support_bubblegram_insufficient_soap_rejected():
    author = UserFactory()
    donor = UserFactory()
    Wallet.objects.create(user=author, soap_balance=10)
    Wallet.objects.create(user=donor, soap_balance=0)
    post = Bubblegram.objects.create(user=author, text="Post", type=BubblegramType.TEXT)

    with pytest.raises(InsufficientSoap):
        support_bubblegram(donor=donor, bubblegram=post)


def test_support_comment_success_and_restrictions():
    post_author = UserFactory()
    commenter = UserFactory()
    donor = UserFactory()
    Wallet.objects.create(user=post_author, soap_balance=10)
    Wallet.objects.create(user=commenter, soap_balance=10)
    Wallet.objects.create(user=donor, soap_balance=10)

    post = Bubblegram.objects.create(user=post_author, text="Post", type=BubblegramType.TEXT)
    comment = Comment.objects.create(bubblegram=post, user=commenter, text="Nice comment")

    # Self support rejected
    with pytest.raises(DomainError) as exc_info:
        support_comment(donor=commenter, comment=comment)
    assert exc_info.value.code == "self_support_not_allowed"

    # Valid support
    support = support_comment(donor=donor, comment=comment)
    assert support.pk is not None

    donor.wallet.refresh_from_db()
    commenter.wallet.refresh_from_db()
    assert donor.wallet.soap_balance == 9
    assert commenter.wallet.soap_balance == 11

    comment.refresh_from_db()
    assert comment.soap_count == 1

    # Duplicate rejected
    with pytest.raises(DomainError) as exc_info:
        support_comment(donor=donor, comment=comment)
    assert exc_info.value.code == "already_supported"


def test_create_bubblepop_success_and_debit():
    author = UserFactory()
    # 24 hours -> ceil(24 / 4) = 6 soap
    Wallet.objects.create(user=author, soap_balance=20)
    image = create_test_image("story.png")

    pop = create_bubblepop(
        author=author,
        image=image,
        duration_hours=24,
        description="My daily update",
    )

    assert pop.pk is not None
    assert pop.user == author
    assert pop.description == "My daily update"
    assert not pop.is_expired

    author.wallet.refresh_from_db()
    assert author.wallet.soap_balance == 14  # 20 - 6 = 14

    tx = SoapTransaction.objects.get(wallet=author.wallet, action_type=ActionType.DEBIT_BUBBLEPOP)
    assert tx.amount == -6
    assert tx.balance_after == 14


def test_create_bubblepop_insufficient_soap():
    author = UserFactory()
    Wallet.objects.create(user=author, soap_balance=2)  # needs 6 for 24h
    image = create_test_image("story.png")

    with pytest.raises(InsufficientSoap):
        create_bubblepop(author=author, image=image, duration_hours=24)


def test_create_bubblepop_validations():
    author = UserFactory()
    Wallet.objects.create(user=author, soap_balance=20)
    image = create_test_image("story.png")

    # Missing image
    with pytest.raises(DomainError) as exc_info:
        create_bubblepop(author=author, image=None, duration_hours=24)
    assert exc_info.value.code == "image_required"

    # Invalid duration (<1 or >48)
    with pytest.raises(DomainError) as exc_info:
        create_bubblepop(author=author, image=image, duration_hours=0)
    assert exc_info.value.code == "invalid_duration"

    with pytest.raises(DomainError) as exc_info:
        create_bubblepop(author=author, image=image, duration_hours=49)
    assert exc_info.value.code == "invalid_duration"


def test_delete_bubblepop():
    author = UserFactory()
    stranger = UserFactory()
    Wallet.objects.create(user=author, soap_balance=20)
    image = create_test_image("story.png")

    pop = create_bubblepop(author=author, image=image, duration_hours=12)

    with pytest.raises(DomainError) as exc_info:
        delete_bubblepop(actor=stranger, bubblepop=pop)
    assert exc_info.value.code == "permission_denied"

    delete_bubblepop(actor=author, bubblepop=pop)
    assert not Bubblepop.objects.filter(pk=pop.pk).exists()
