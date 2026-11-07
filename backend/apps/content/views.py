from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.communities.selectors import get_community_by_commname

from .selectors import (
    get_bubblegram_by_id,
    get_bubblepop_by_id,
    get_comment_by_id,
    list_bubblegram_comments,
    list_community_bubblegrams,
    list_user_bubblegrams,
    list_user_bubblepops,
)
from .serializers import (
    BubblegramCreateSerializer,
    BubblegramSerializer,
    BubblegramSupportResponseSerializer,
    BubblepopCreateSerializer,
    BubblepopSerializer,
    CommentCreateSerializer,
    CommentSerializer,
    CommentSupportResponseSerializer,
)
from .services import (
    create_bubblegram,
    create_bubblepop,
    create_comment,
    delete_bubblegram,
    delete_bubblepop,
    delete_comment,
    support_bubblegram,
    support_comment,
)


class BubblegramListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @extend_schema(request=BubblegramCreateSerializer, responses={201: BubblegramSerializer})
    def post(self, request):
        serializer = BubblegramCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        commname = serializer.validated_data.get("commname")
        community = get_community_by_commname(commname=commname) if commname else None

        media_files = (
            request.FILES.getlist("media_files")
            or request.FILES.getlist("images")
            or serializer.validated_data.get("media_files", [])
        )

        bubblegram = create_bubblegram(
            author=request.user,
            type=serializer.validated_data.get("type"),
            text=serializer.validated_data.get("text", ""),
            community=community,
            media_files=media_files,
        )

        out_serializer = BubblegramSerializer(bubblegram, context={"request": request})
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)


class BubblegramDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: BubblegramSerializer})
    def get(self, request, pk: int):
        bubblegram = get_bubblegram_by_id(bubblegram_id=pk)
        return Response(BubblegramSerializer(bubblegram, context={"request": request}).data)

    @extend_schema(responses={204: None})
    def delete(self, request, pk: int):
        bubblegram = get_bubblegram_by_id(bubblegram_id=pk)
        delete_bubblegram(actor=request.user, bubblegram=bubblegram)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserBubblegramsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: BubblegramSerializer(many=True)})
    def get(self, request, username: str):
        qs = list_user_bubblegrams(username=username)
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = BubblegramSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)


class CommunityBubblegramsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: BubblegramSerializer(many=True)})
    def get(self, request, commname: str):
        qs = list_community_bubblegrams(commname=commname)
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = BubblegramSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)


class BubblegramCommentsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: CommentSerializer(many=True)})
    def get(self, request, pk: int):
        bubblegram = get_bubblegram_by_id(bubblegram_id=pk)
        qs = list_bubblegram_comments(bubblegram_id=bubblegram.id)
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = CommentSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(request=CommentCreateSerializer, responses={201: CommentSerializer})
    def post(self, request, pk: int):
        bubblegram = get_bubblegram_by_id(bubblegram_id=pk)
        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        parent = None
        parent_id = serializer.validated_data.get("parent_id")
        if parent_id:
            parent = get_comment_by_id(comment_id=parent_id)

        comment = create_comment(
            author=request.user,
            bubblegram=bubblegram,
            text=serializer.validated_data["text"],
            parent=parent,
        )
        return Response(
            CommentSerializer(comment, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class CommentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={204: None})
    def delete(self, request, pk: int):
        comment = get_comment_by_id(comment_id=pk)
        delete_comment(actor=request.user, comment=comment)
        return Response(status=status.HTTP_204_NO_CONTENT)


class BubblegramSupportView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses={201: BubblegramSupportResponseSerializer})
    def post(self, request, pk: int):
        bubblegram = get_bubblegram_by_id(bubblegram_id=pk)
        support = support_bubblegram(donor=request.user, bubblegram=bubblegram)
        return Response(
            BubblegramSupportResponseSerializer(support).data,
            status=status.HTTP_201_CREATED,
        )


class CommentSupportView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses={201: CommentSupportResponseSerializer})
    def post(self, request, pk: int):
        comment = get_comment_by_id(comment_id=pk)
        support = support_comment(donor=request.user, comment=comment)
        return Response(
            CommentSupportResponseSerializer(support).data,
            status=status.HTTP_201_CREATED,
        )


class BubblepopListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(request=BubblepopCreateSerializer, responses={201: BubblepopSerializer})
    def post(self, request):
        serializer = BubblepopCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        bubblepop = create_bubblepop(
            author=request.user,
            image=serializer.validated_data["image"],
            duration_hours=serializer.validated_data.get("duration_hours", 24),
            description=serializer.validated_data.get("description", ""),
        )
        return Response(
            BubblepopSerializer(bubblepop, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class BubblepopDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: BubblepopSerializer})
    def get(self, request, pk: int):
        bubblepop = get_bubblepop_by_id(bubblepop_id=pk)
        return Response(BubblepopSerializer(bubblepop, context={"request": request}).data)

    @extend_schema(responses={204: None})
    def delete(self, request, pk: int):
        bubblepop = get_bubblepop_by_id(bubblepop_id=pk)
        delete_bubblepop(actor=request.user, bubblepop=bubblepop)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserBubblepopsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: BubblepopSerializer(many=True)})
    def get(self, request, username: str):
        qs = list_user_bubblepops(username=username)
        serializer = BubblepopSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)
