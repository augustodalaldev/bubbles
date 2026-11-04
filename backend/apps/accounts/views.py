from django.conf import settings
from django.contrib.auth import authenticate
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.exceptions import DomainError

from .selectors import get_user_by_username, get_user_wallet_and_transactions
from .serializers import (
    AuthResponseSerializer,
    CurrentUserSerializer,
    DeleteAccountSerializer,
    LoginInputSerializer,
    PublicUserSerializer,
    RefreshTokenInputSerializer,
    RegisterInputSerializer,
    SoapTransactionSerializer,
    UpdateProfileSerializer,
)
from .services import delete_account, register_user, update_profile

REFRESH_COOKIE_NAME = "refresh_token"
AUTH_COOKIE_PATH = "/api/v1/auth/"


def set_refresh_cookie(response: Response, refresh_token: str) -> None:
    max_age = int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds())
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=max_age,
        httponly=True,
        samesite="Lax",
        secure=not settings.DEBUG,
        path=AUTH_COOKIE_PATH,
    )


def clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        path=AUTH_COOKIE_PATH,
        samesite="Lax",
    )


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = "auth"

    @extend_schema(request=RegisterInputSerializer, responses={201: AuthResponseSerializer})
    def post(self, request):
        serializer = RegisterInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = register_user(**serializer.validated_data)
        refresh = RefreshToken.for_user(user)

        response_data = {
            "access": str(refresh.access_token),
            "user": CurrentUserSerializer(user).data,
        }
        response = Response(response_data, status=status.HTTP_201_CREATED)
        set_refresh_cookie(response, str(refresh))
        return response


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = "auth"

    @extend_schema(request=LoginInputSerializer, responses={200: AuthResponseSerializer})
    def post(self, request):
        serializer = LoginInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            identifier=serializer.validated_data["identifier"],
            password=serializer.validated_data["password"],
        )
        if not user:
            raise DomainError(
                "Invalid username/email or password.",
                code="invalid_credentials",
                http_status=401,
            )

        refresh = RefreshToken.for_user(user)
        response_data = {
            "access": str(refresh.access_token),
            "user": CurrentUserSerializer(user).data,
        }
        response = Response(response_data, status=status.HTTP_200_OK)
        set_refresh_cookie(response, str(refresh))
        return response


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=RefreshTokenInputSerializer, responses={200: OpenApiTypes.OBJECT})
    def post(self, request):
        token_str = request.COOKIES.get(REFRESH_COOKIE_NAME) or request.data.get("refresh")
        if not token_str:
            raise DomainError(
                "Refresh token not provided.",
                code="token_missing",
                http_status=400,
            )

        try:
            refresh = RefreshToken(token_str)
            access_token = str(refresh.access_token)
            new_refresh = None

            if settings.SIMPLE_JWT.get("ROTATE_REFRESH_TOKENS", True):
                if settings.SIMPLE_JWT.get("BLACKLIST_AFTER_ROTATION", True):
                    try:
                        refresh.blacklist()
                    except AttributeError:
                        pass
                refresh.set_jti()
                refresh.set_exp()
                refresh.set_iat()
                new_refresh = str(refresh)
        except (TokenError, InvalidToken) as exc:
            raise DomainError(
                "Invalid or expired refresh token.",
                code="token_invalid",
                http_status=401,
            ) from exc

        response = Response({"access": access_token}, status=status.HTTP_200_OK)
        if new_refresh:
            set_refresh_cookie(response, new_refresh)
        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=RefreshTokenInputSerializer, responses={200: OpenApiTypes.OBJECT})
    def post(self, request):
        token_str = request.COOKIES.get(REFRESH_COOKIE_NAME) or request.data.get("refresh")
        if token_str:
            try:
                refresh = RefreshToken(token_str)
                refresh.blacklist()
            except Exception:
                pass

        response = Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        clear_refresh_cookie(response)
        return response


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: CurrentUserSerializer})
    def get(self, request):
        return Response(CurrentUserSerializer(request.user).data)

    @extend_schema(request=UpdateProfileSerializer, responses={200: CurrentUserSerializer})
    def patch(self, request):
        serializer = UpdateProfileSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = update_profile(user=request.user, **serializer.validated_data)
        return Response(CurrentUserSerializer(user).data)

    @extend_schema(request=DeleteAccountSerializer, responses={204: None})
    def delete(self, request):
        serializer = DeleteAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        delete_account(user=request.user, password=serializer.validated_data["password"])
        response = Response(status=status.HTTP_204_NO_CONTENT)
        clear_refresh_cookie(response)
        return response


class PublicProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: PublicUserSerializer})
    def get(self, request, username: str):
        user = get_user_by_username(username=username)
        return Response(PublicUserSerializer(user).data)


class UserWalletView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request):
        wallet, transactions = get_user_wallet_and_transactions(user=request.user)
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(transactions, request)
        tx_serializer = SoapTransactionSerializer(page, many=True)
        return Response(
            {
                "soap_balance": wallet.soap_balance,
                "passive_earn_rate": wallet.passive_earn_rate,
                "count": paginator.page.paginator.count,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "results": tx_serializer.data,
            }
        )
