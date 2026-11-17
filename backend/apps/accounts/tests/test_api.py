from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.tests.factories import DEFAULT_PASSWORD, UserFactory
from apps.communities.models import MemberRole
from apps.communities.tests.factories import CommunityFactory, CommunityMemberFactory
from apps.economy.models import EconomySettings, Wallet

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client():
    user = UserFactory()
    Wallet.objects.create(user=user, soap_balance=20, passive_earn_rate=5)
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


def test_register_api_success(api_client):
    settings_obj = EconomySettings.load()
    birth_date = (timezone.localdate() - timedelta(days=365 * 20)).isoformat()
    payload = {
        "username": "new_user",
        "email": "new_user@example.com",
        "password": DEFAULT_PASSWORD,
        "name": "New User",
        "birth_date": birth_date,
        "description": "Just joined Bubbles!",
    }

    response = api_client.post("/api/v1/auth/register/", data=payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert "access" in response.data
    assert response.data["user"]["username"] == "new_user"
    assert response.data["user"]["email"] == "new_user@example.com"
    assert response.data["user"]["soap_balance"] == settings_obj.signup_grant

    # Verify refresh token is set in httpOnly cookie
    assert "refresh_token" in response.cookies
    cookie = response.cookies["refresh_token"]
    assert cookie["httponly"] is True
    assert cookie["path"] == "/api/v1/auth/"


def test_register_api_validation_error(api_client):
    payload = {
        "username": "ab",  # invalid format
        "email": "not-an-email",
        "password": "123",  # weak
        "name": "A",
        "birth_date": "2030-01-01",  # future
    }
    response = api_client.post("/api/v1/auth/register/", data=payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in response.data
    assert response.data["error"]["code"] == "validation_error"
    assert "fields" in response.data["error"]
    assert "email" in response.data["error"]["fields"]


def test_register_api_duplicate_username(api_client):
    UserFactory(username="existing_user")
    birth_date = (timezone.localdate() - timedelta(days=365 * 20)).isoformat()
    payload = {
        "username": "EXISTING_USER",
        "email": "unique@example.com",
        "password": DEFAULT_PASSWORD,
        "name": "Unique Name",
        "birth_date": birth_date,
    }
    response = api_client.post("/api/v1/auth/register/", data=payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"]["code"] == "username_already_registered"


def test_login_api_by_username(api_client):
    user = UserFactory(username="login_user")
    Wallet.objects.create(user=user, soap_balance=20)
    payload = {
        "identifier": "login_user",
        "password": DEFAULT_PASSWORD,
    }
    response = api_client.post("/api/v1/auth/login/", data=payload, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert response.data["user"]["username"] == "login_user"
    assert "refresh_token" in response.cookies


def test_login_api_by_email(api_client):
    user = UserFactory(email="user_email@example.com")
    Wallet.objects.create(user=user, soap_balance=20)
    payload = {
        "identifier": "USER_EMAIL@EXAMPLE.COM",
        "password": DEFAULT_PASSWORD,
    }
    response = api_client.post("/api/v1/auth/login/", data=payload, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert response.data["user"]["email"] == "user_email@example.com"


def test_login_api_invalid_credentials(api_client):
    UserFactory(username="valid_user")
    payload = {
        "identifier": "valid_user",
        "password": "WrongPassword!",
    }
    response = api_client.post("/api/v1/auth/login/", data=payload, format="json")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data["error"]["code"] == "invalid_credentials"


def test_login_api_deleted_user(api_client):
    UserFactory(username="deleted_guy", is_active=False, deleted_at=timezone.now())
    payload = {
        "identifier": "deleted_guy",
        "password": DEFAULT_PASSWORD,
    }
    response = api_client.post("/api/v1/auth/login/", data=payload, format="json")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_refresh_api_via_cookie(api_client):
    user = UserFactory()
    refresh = RefreshToken.for_user(user)

    api_client.cookies["refresh_token"] = str(refresh)
    response = api_client.post("/api/v1/auth/refresh/")
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh_token" in response.cookies


def test_refresh_api_via_body(api_client):
    user = UserFactory()
    refresh = RefreshToken.for_user(user)

    response = api_client.post("/api/v1/auth/refresh/", data={"refresh": str(refresh)})
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data


def test_refresh_api_invalid_token(api_client):
    api_client.cookies["refresh_token"] = "invalid.token.here"
    response = api_client.post("/api/v1/auth/refresh/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data["error"]["code"] == "token_invalid"


def test_logout_api(auth_client):
    client, user = auth_client
    refresh = RefreshToken.for_user(user)
    client.cookies["refresh_token"] = str(refresh)

    response = client.post("/api/v1/auth/logout/")
    assert response.status_code == status.HTTP_200_OK

    # Refreshing with the blacklisted token must now fail
    unauthed = APIClient()
    unauthed.cookies["refresh_token"] = str(refresh)
    refresh_res = unauthed.post("/api/v1/auth/refresh/")
    assert refresh_res.status_code == status.HTTP_401_UNAUTHORIZED


def test_current_user_me_get_authenticated(auth_client):
    client, user = auth_client
    response = client.get("/api/v1/users/me/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == user.id
    assert response.data["username"] == user.username
    assert response.data["email"] == user.email
    assert response.data["status"] == "ACTIVE"
    assert response.data["is_suspended"] is False
    assert response.data["suspended_until"] is None
    assert response.data["soap_balance"] == 20
    assert response.data["wallet"]["soap_balance"] == 20
    assert response.data["wallet"]["passive_earn_rate"] == 5


def test_current_user_me_get_unauthenticated(api_client):
    response = api_client.get("/api/v1/users/me/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data["error"]["code"] == "not_authenticated"


def test_current_user_me_patch(auth_client):
    client, user = auth_client
    payload = {
        "name": "Updated Name",
        "description": "Updated Description",
        "customization_json": {"theme": "dark-bubbles"},
    }
    response = client.patch("/api/v1/users/me/", data=payload, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Updated Name"
    assert response.data["description"] == "Updated Description"
    assert response.data["customization_json"] == {"theme": "dark-bubbles"}

    user.refresh_from_db()
    assert user.name == "Updated Name"


def test_current_user_me_delete_success(auth_client):
    client, user = auth_client
    payload = {"password": DEFAULT_PASSWORD}

    response = client.delete("/api/v1/users/me/", data=payload, format="json")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    user.refresh_from_db()
    assert user.username == f"deleted_{user.id}"
    assert user.is_active is False
    assert user.deleted_at is not None


def test_current_user_me_delete_wrong_password(auth_client):
    client, user = auth_client
    payload = {"password": "IncorrectPassword!"}

    response = client.delete("/api/v1/users/me/", data=payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"]["code"] == "invalid_password"


def test_current_user_me_delete_community_leader(auth_client):
    client, user = auth_client
    community = CommunityFactory(commname="awesome_community")
    CommunityMemberFactory(community=community, user=user, role=MemberRole.LEADER)

    payload = {"password": DEFAULT_PASSWORD}
    response = client.delete("/api/v1/users/me/", data=payload, format="json")
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.data["error"]["code"] == "must_transfer_leadership"
    assert "awesome_community" in response.data["error"]["communities"]


def test_public_profile_success_and_hides_private_fields(auth_client):
    client, _ = auth_client
    target = UserFactory(username="target_user", name="Target Person", description="Bio")
    Wallet.objects.create(user=target, soap_balance=100)

    response = client.get(f"/api/v1/users/{target.username}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["username"] == "target_user"
    assert response.data["name"] == "Target Person"
    assert response.data["description"] == "Bio"

    # CRITICAL INVARIANT: Private fields must NEVER leak
    assert "email" not in response.data
    assert "wallet" not in response.data
    assert "soap_balance" not in response.data
    assert "birth_date" not in response.data


def test_public_profile_not_found(auth_client):
    client, _ = auth_client
    response = client.get("/api/v1/users/non_existent_user/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["error"]["code"] == "user_not_found"


def test_user_wallet_endpoint(auth_client):
    client, user = auth_client
    from apps.economy.models import ActionType, SoapTransaction

    SoapTransaction.objects.create(
        wallet=user.wallet,
        amount=20,
        action_type=ActionType.SIGNUP_GRANT,
        balance_after=20,
        idempotency_key="tx_test_1",
    )

    response = client.get("/api/v1/users/me/wallet/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["soap_balance"] == 20
    assert response.data["passive_earn_rate"] == 5
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["amount"] == 20
    assert response.data["results"][0]["action_type"] == ActionType.SIGNUP_GRANT


def test_auth_throttling():
    from django.core.cache import cache
    from rest_framework.throttling import ScopedRateThrottle

    cache.clear()
    client = APIClient()
    original_rates = ScopedRateThrottle.THROTTLE_RATES
    ScopedRateThrottle.THROTTLE_RATES = {"auth": "2/minute"}
    try:
        # 1st attempt
        res1 = client.post("/api/v1/auth/login/", data={"identifier": "x", "password": "y"})
        assert res1.status_code == status.HTTP_401_UNAUTHORIZED

        # 2nd attempt
        res2 = client.post("/api/v1/auth/login/", data={"identifier": "x", "password": "y"})
        assert res2.status_code == status.HTTP_401_UNAUTHORIZED

        # 3rd attempt: must be throttled
        res3 = client.post("/api/v1/auth/login/", data={"identifier": "x", "password": "y"})
        assert res3.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert res3.data["error"]["code"] == "throttled"
    finally:
        ScopedRateThrottle.THROTTLE_RATES = original_rates
        cache.clear()


def test_follow_and_unfollow_api(auth_client):
    client, user = auth_client
    target = UserFactory(username="targetuser")

    # Follow
    follow_resp = client.post(f"/api/v1/users/{target.username}/follow/")
    assert follow_resp.status_code == status.HTTP_201_CREATED

    # Cannot follow again
    dup_resp = client.post(f"/api/v1/users/{target.username}/follow/")
    assert dup_resp.status_code == status.HTTP_400_BAD_REQUEST

    # Cannot follow self
    self_resp = client.post(f"/api/v1/users/{user.username}/follow/")
    assert self_resp.status_code == status.HTTP_400_BAD_REQUEST

    # Unfollow
    unfollow_resp = client.delete(f"/api/v1/users/{target.username}/follow/")
    assert unfollow_resp.status_code == status.HTTP_204_NO_CONTENT

    # Cannot unfollow again
    unfollow_dup = client.delete(f"/api/v1/users/{target.username}/follow/")
    assert unfollow_dup.status_code == status.HTTP_400_BAD_REQUEST


def test_user_profile_detail_includes_counts_and_relationship_flags(auth_client):
    client, user = auth_client
    target = UserFactory(username="socialstar")

    # Initially: 0 followers, 0 following, is_following=False
    resp = client.get(f"/api/v1/users/{target.username}/")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["followers_count"] == 0
    assert resp.data["following_count"] == 0
    assert resp.data["is_following"] is False
    assert resp.data["is_followed_by"] is False

    # user follows target
    from apps.accounts.models import UserConnection

    UserConnection.objects.create(follower=user, followed=target)

    # target also follows user
    UserConnection.objects.create(follower=target, followed=user)

    resp2 = client.get(f"/api/v1/users/{target.username}/")
    assert resp2.status_code == status.HTTP_200_OK
    assert resp2.data["followers_count"] == 1
    assert resp2.data["following_count"] == 1
    assert resp2.data["is_following"] is True
    assert resp2.data["is_followed_by"] is True


def test_user_followers_and_following_lists_api(auth_client):
    client, user = auth_client
    target = UserFactory(username="targetperson")
    friend1 = UserFactory(username="friend1")
    friend2 = UserFactory(username="friend2")

    from apps.accounts.models import UserConnection

    # friend1 and friend2 follow target
    UserConnection.objects.create(follower=friend1, followed=target)
    UserConnection.objects.create(follower=friend2, followed=target)
    # target follows friend1
    UserConnection.objects.create(follower=target, followed=friend1)

    # Followers list
    resp_followers = client.get(f"/api/v1/users/{target.username}/followers/")
    assert resp_followers.status_code == status.HTTP_200_OK
    assert resp_followers.data["count"] == 2
    follower_usernames = [item["user"]["username"] for item in resp_followers.data["results"]]
    assert set(follower_usernames) == {"friend1", "friend2"}

    # Following list
    resp_following = client.get(f"/api/v1/users/{target.username}/following/")
    assert resp_following.status_code == status.HTTP_200_OK
    assert resp_following.data["count"] == 1
    assert resp_following.data["results"][0]["user"]["username"] == "friend1"


@pytest.mark.parametrize(
    ("path", "expected_status"),
    [("/api/v1/auth/login/", 200), ("/api/v1/auth/register/", 400)],
)
def test_auth_endpoints_ignore_stale_bearer_header(api_client, path, expected_status):
    """An expired access token in the header must not turn login/register into a 401."""
    user = UserFactory(username="stale_user")
    Wallet.objects.create(user=user, soap_balance=20)
    api_client.credentials(HTTP_AUTHORIZATION="Bearer expired.or.garbage")
    payload = {"identifier": "stale_user", "password": DEFAULT_PASSWORD}
    response = api_client.post(path, data=payload, format="json")
    assert response.status_code == expected_status


def test_refresh_endpoint_ignores_stale_bearer_header(api_client):
    user = UserFactory(username="refresh_user")
    Wallet.objects.create(user=user, soap_balance=20)
    login = api_client.post(
        "/api/v1/auth/login/",
        data={"identifier": "refresh_user", "password": DEFAULT_PASSWORD},
        format="json",
    )
    assert login.status_code == status.HTTP_200_OK
    api_client.credentials(HTTP_AUTHORIZATION="Bearer expired.or.garbage")
    response = api_client.post("/api/v1/auth/refresh/")
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data


def _login(client, username):
    return client.post(
        "/api/v1/auth/login/",
        data={"identifier": username, "password": DEFAULT_PASSWORD},
        format="json",
    )


def test_logout_works_without_valid_access_token_and_blacklists_refresh(api_client):
    user = UserFactory(username="logout_user")
    Wallet.objects.create(user=user, soap_balance=20)
    assert _login(api_client, "logout_user").status_code == status.HTTP_200_OK
    refresh_cookie = api_client.cookies["refresh_token"].value

    api_client.credentials(HTTP_AUTHORIZATION="Bearer expired.or.garbage")
    response = api_client.post("/api/v1/auth/logout/")
    assert response.status_code == status.HTTP_200_OK
    assert response.cookies["refresh_token"].value == ""

    api_client.credentials()
    api_client.cookies["refresh_token"] = refresh_cookie
    reuse = api_client.post("/api/v1/auth/refresh/")
    assert reuse.status_code == status.HTTP_401_UNAUTHORIZED
    assert reuse.data["error"]["code"] == "token_invalid"


def test_refresh_token_cannot_be_reused_after_rotation(api_client):
    user = UserFactory(username="rotate_user")
    Wallet.objects.create(user=user, soap_balance=20)
    _login(api_client, "rotate_user")
    old_cookie = api_client.cookies["refresh_token"].value

    first = api_client.post("/api/v1/auth/refresh/")
    assert first.status_code == status.HTTP_200_OK
    assert api_client.cookies["refresh_token"].value != old_cookie

    api_client.cookies["refresh_token"] = old_cookie
    second = api_client.post("/api/v1/auth/refresh/")
    assert second.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize("change", ["inactive", "deleted"])
def test_refresh_is_refused_for_inactive_or_deleted_users(api_client, change):
    user = UserFactory(username="gone_user")
    Wallet.objects.create(user=user, soap_balance=20)
    _login(api_client, "gone_user")

    if change == "inactive":
        user.is_active = False
    else:
        user.deleted_at = timezone.now()
    user.save()

    response = api_client.post("/api/v1/auth/refresh/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data["error"]["code"] == "token_invalid"


def test_me_and_login_return_absolute_profile_photo_url(api_client):
    from apps.accounts.models import User

    user = UserFactory(username="photo_user")
    Wallet.objects.create(user=user, soap_balance=20)
    User.objects.filter(pk=user.pk).update(profile_photo="profile_photos/me.png")

    login = _login(api_client, "photo_user")
    assert login.data["user"]["profile_photo"].startswith("http://testserver/media/")

    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
    me = api_client.get("/api/v1/users/me/")
    assert me.data["profile_photo"].startswith("http://testserver/media/")
