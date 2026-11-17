from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.selectors import get_user_by_username

from .selectors import get_letter_by_id, list_inbox_letters, list_sent_letters
from .serializers import LetterCreateSerializer, LetterSerializer
from .services import mark_letter_as_read, send_letter


class LetterListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @extend_schema(request=LetterCreateSerializer, responses={201: LetterSerializer})
    def post(self, request):
        serializer = LetterCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        recipient_username = serializer.validated_data["recipient_username"]
        recipient = get_user_by_username(username=recipient_username)

        reply_to = None
        reply_to_id = serializer.validated_data.get("reply_to_id")
        if reply_to_id:
            reply_to = get_letter_by_id(letter_id=reply_to_id, user=request.user)

        image = request.FILES.get("image") or serializer.validated_data.get("image")

        letter = send_letter(
            sender=request.user,
            recipient=recipient,
            text=serializer.validated_data["text"],
            image=image,
            reply_to=reply_to,
        )
        return Response(
            LetterSerializer(letter, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class LetterInboxView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: LetterSerializer(many=True)})
    def get(self, request):
        qs = list_inbox_letters(user=request.user)
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = LetterSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)


class LetterSentView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: LetterSerializer(many=True)})
    def get(self, request):
        qs = list_sent_letters(user=request.user)
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = LetterSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)


class LetterDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: LetterSerializer})
    def get(self, request, pk: int):
        letter = get_letter_by_id(letter_id=pk, user=request.user)
        if letter.recipient_id == request.user.id:
            letter = mark_letter_as_read(actor=request.user, letter=letter)
        return Response(LetterSerializer(letter, context={"request": request}).data)
