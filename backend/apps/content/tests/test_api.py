from io import BytesIO

import pytest
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.tests.factories import UserFactory
from apps.communities.models import MemberRole, MemberState
from apps.communities.tests.factories import CommunityFactory, CommunityMemberFactory
from apps.content.models import Bubblegram, Bubblepop, Comment
from apps.content.tests.factories import BubblegramFactory, BubblepopFactory, CommentFactory
from apps.economy.models import Wallet

pytestmark = pytest.mark.django_db


def create_image_file(name="photo.png"):
    file = BytesIO()
    image = Image.new("RGBA", size=(40, 40), color="blue")
    image.save(file, "png")
    file.seek(0)
    file.name = name
    return file


def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_create_text_bubblegram_api():
    user = UserFactory()
    Wallet.objects.create(user=user, soap_balance=50)
    client = auth_client(user)

    payload = {
        "type": "TEXT",
        "text": "Hello world from API!",
    }
    response = client.post("/api/v1/bubblegrams/", data=payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["text"] == "Hello world from API!"
    assert response.data["type"] == "TEXT"
    assert response.data["can_delete"] is True


def test_create_media_bubblegram_api():
    user = UserFactory()
    Wallet.objects.create(user=user, soap_balance=50)
    client = auth_client(user)

    img1 = create_image_file("img1.png")
    img2 = create_image_file("img2.png")

    payload = {
        "type": "MEDIA",
        "text": "A photo with no requirement for long text",
        "media_files": [img1, img2],
    }
    response = client.post("/api/v1/bubblegrams/", data=payload, format="multipart")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["type"] == "MEDIA"
    assert len(response.data["media"]) == 2


def test_create_community_bubblegram_api():
    user = UserFactory()
    community = CommunityFactory()
    CommunityMemberFactory(
        community=community, user=user, role=MemberRole.MEMBER, current_state=MemberState.ACTIVE
    )
    Wallet.objects.create(user=user, soap_balance=50)
    client = auth_client(user)

    payload = {
        "type": "TEXT",
        "text": "Community post via API",
        "commname": community.commname,
    }
    response = client.post("/api/v1/bubblegrams/", data=payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["community"]["commname"] == community.commname


def test_create_bubblegram_api_insufficient_soap():
    user = UserFactory()
    Wallet.objects.create(user=user, soap_balance=5)  # costs 10
    client = auth_client(user)

    payload = {
        "type": "TEXT",
        "text": "Too poor to post",
    }
    response = client.post("/api/v1/bubblegrams/", data=payload, format="json")
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.data["error"]["code"] == "insufficient_soap"


def test_get_bubblegram_detail_api():
    user = UserFactory()
    post = BubblegramFactory(user=user, text="Post detail test")
    client = auth_client(user)

    response = client.get(f"/api/v1/bubblegrams/{post.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == post.id
    assert response.data["text"] == "Post detail test"
    assert response.data["can_delete"] is True


def test_delete_bubblegram_api():
    author = UserFactory()
    post = BubblegramFactory(user=author)
    client = auth_client(author)

    response = client.delete(f"/api/v1/bubblegrams/{post.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Bubblegram.objects.filter(pk=post.id).exists()


def test_delete_bubblegram_api_unauthorized():
    author = UserFactory()
    stranger = UserFactory()
    post = BubblegramFactory(user=author)
    client = auth_client(stranger)

    response = client.delete(f"/api/v1/bubblegrams/{post.id}/")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["error"]["code"] == "permission_denied"


def test_list_user_bubblegrams_api():
    user = UserFactory()
    BubblegramFactory(user=user, text="Post 1")
    BubblegramFactory(user=user, text="Post 2")

    client = auth_client(user)
    response = client.get(f"/api/v1/users/{user.username}/bubblegrams/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 2


def test_list_community_bubblegrams_api():
    community = CommunityFactory()
    user = UserFactory()
    BubblegramFactory(community=community, user=user, text="Comm post 1")
    BubblegramFactory(community=community, user=user, text="Comm post 2")

    client = auth_client(user)
    response = client.get(f"/api/v1/communities/{community.commname}/bubblegrams/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 2


def test_create_and_list_bubblegram_comments_api():
    post_author = UserFactory()
    commenter = UserFactory()
    post = BubblegramFactory(user=post_author)

    client = auth_client(commenter)

    # Create root comment
    payload = {"text": "Awesome post!"}
    resp = client.post(f"/api/v1/bubblegrams/{post.id}/comments/", data=payload, format="json")
    assert resp.status_code == status.HTTP_201_CREATED
    root_id = resp.data["id"]
    assert resp.data["text"] == "Awesome post!"
    assert resp.data["user"]["username"] == commenter.username
    assert resp.data["can_delete"] is True

    # Create reply
    reply_payload = {"text": "Replying to awesome post", "parent_id": root_id}
    reply_resp = client.post(
        f"/api/v1/bubblegrams/{post.id}/comments/", data=reply_payload, format="json"
    )
    assert reply_resp.status_code == status.HTTP_201_CREATED
    assert reply_resp.data["parent"] == root_id

    # List comments
    list_resp = client.get(f"/api/v1/bubblegrams/{post.id}/comments/")
    assert list_resp.status_code == status.HTTP_200_OK
    assert list_resp.data["count"] == 2


def test_delete_comment_api():
    post_author = UserFactory()
    commenter = UserFactory()
    post = BubblegramFactory(user=post_author)
    comment = CommentFactory(bubblegram=post, user=commenter)

    stranger = UserFactory()
    stranger_client = auth_client(stranger)
    resp = stranger_client.delete(f"/api/v1/comments/{comment.id}/")
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # Commenter deletes their comment
    commenter_client = auth_client(commenter)
    del_resp = commenter_client.delete(f"/api/v1/comments/{comment.id}/")
    assert del_resp.status_code == status.HTTP_204_NO_CONTENT
    assert not Comment.objects.filter(pk=comment.id).exists()


def test_support_bubblegram_api():
    author = UserFactory()
    donor = UserFactory()
    Wallet.objects.create(user=author, soap_balance=20)
    Wallet.objects.create(user=donor, soap_balance=20)

    post = BubblegramFactory(user=author)
    client = auth_client(donor)

    resp = client.post(f"/api/v1/bubblegrams/{post.id}/support/")
    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.data["bubblegram"] == post.id
    assert resp.data["soap_count"] == 1

    # Second support should fail with 400
    dup_resp = client.post(f"/api/v1/bubblegrams/{post.id}/support/")
    assert dup_resp.status_code == status.HTTP_400_BAD_REQUEST
    assert dup_resp.data["error"]["code"] == "already_supported"


def test_support_comment_api():
    author = UserFactory()
    donor = UserFactory()
    Wallet.objects.create(user=author, soap_balance=20)
    Wallet.objects.create(user=donor, soap_balance=20)

    post = BubblegramFactory(user=author)
    comment = CommentFactory(bubblegram=post, user=author)
    client = auth_client(donor)

    resp = client.post(f"/api/v1/comments/{comment.id}/support/")
    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.data["comment"] == comment.id
    assert resp.data["soap_count"] == 1


def test_create_bubblepop_api():
    user = UserFactory()
    Wallet.objects.create(user=user, soap_balance=20)
    client = auth_client(user)

    img = create_image_file("story.png")
    payload = {
        "image": img,
        "duration_hours": 12,  # ceil(12/4) = 3 soap
        "description": "My first pop",
    }
    resp = client.post("/api/v1/bubblepops/", data=payload, format="multipart")
    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.data["description"] == "My first pop"
    assert resp.data["is_expired"] is False
    assert resp.data["can_delete"] is True


def test_get_and_delete_bubblepop_api():
    author = UserFactory()
    pop = BubblepopFactory(user=author)

    client = auth_client(author)
    get_resp = client.get(f"/api/v1/bubblepops/{pop.id}/")
    assert get_resp.status_code == status.HTTP_200_OK
    assert get_resp.data["id"] == pop.id

    del_resp = client.delete(f"/api/v1/bubblepops/{pop.id}/")
    assert del_resp.status_code == status.HTTP_204_NO_CONTENT
    assert not Bubblepop.objects.filter(pk=pop.id).exists()


def test_list_user_bubblepops_api_excludes_expired():
    from datetime import timedelta

    from django.utils import timezone

    user = UserFactory()
    now = timezone.now()
    # Active pop
    active_pop = BubblepopFactory(
        user=user,
        created_at=now,
        expires_at=now + timedelta(hours=10),
    )
    # Expired pop (created 24h ago, expired 1h ago)
    BubblepopFactory(
        user=user,
        created_at=now - timedelta(hours=24),
        expires_at=now - timedelta(hours=1),
    )

    client = auth_client(user)
    resp = client.get(f"/api/v1/users/{user.username}/bubblepops/")
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data) == 1
    assert resp.data[0]["id"] == active_pop.id
