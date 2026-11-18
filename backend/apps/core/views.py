from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import JsonResponse
from django.views.defaults import page_not_found, server_error
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.serializers import PublicUserSerializer
from apps.communities.models import Community, not_moderated_q
from apps.communities.serializers import CommunityListSerializer

from .messages import message_for
from .serializers import SearchResultSerializer

User = get_user_model()


@extend_schema(responses=OpenApiTypes.OBJECT)
@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok"})


class SearchView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="q",
                type=str,
                description="Search query string for users and communities",
                required=False,
            )
        ],
        responses={200: SearchResultSerializer},
    )
    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if not query:
            return Response({"query": "", "users": [], "communities": []})

        users = User.objects.filter(
            Q(username__icontains=query) | Q(name__icontains=query),
            is_active=True,
            deleted_at__isnull=True,
        ).order_by("username")[:20]

        communities = (
            Community.objects.filter(
                Q(commname__icontains=query)
                | Q(name__icontains=query)
                | Q(description__icontains=query),
                archived_at__isnull=True,
                deleted_at__isnull=True,
            )
            .filter(not_moderated_q())
            .order_by("-member_count", "commname")[:20]
        )

        data = {
            "query": query,
            "users": PublicUserSerializer(users, many=True, context={"request": request}).data,
            "communities": CommunityListSerializer(
                communities, many=True, context={"request": request}
            ).data,
        }
        return Response(data, status=status.HTTP_200_OK)


def api_not_found(request, exception=None):
    """JSON 404 for unknown /api/ routes (HTML for everything else)."""
    if request.path.startswith("/api/"):
        return JsonResponse(
            {"error": {"code": "not_found", "message": message_for("not_found"), "fields": None}},
            status=404,
        )
    return page_not_found(request, exception)


def api_server_error(request):
    """JSON 500 for /api/ routes (HTML for everything else)."""
    if request.path.startswith("/api/"):
        return JsonResponse(
            {
                "error": {
                    "code": "server_error",
                    "message": message_for("server_error"),
                    "fields": None,
                }
            },
            status=500,
        )
    return server_error(request)
