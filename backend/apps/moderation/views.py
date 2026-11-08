from django.contrib.auth import get_user_model
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.communities.models import Community
from apps.economy.models import Wallet
from apps.moderation.models import Report
from apps.moderation.selectors import list_audit_logs, list_reports
from apps.moderation.serializers import (
    AdminSoapAdjustmentInputSerializer,
    AuditLogSerializer,
    ReasonRequiredInputSerializer,
    ReportCreateSerializer,
    ReportReviewSerializer,
    ReportSerializer,
    SuspendUserInputSerializer,
)
from apps.moderation.services import (
    admin_adjust_soap,
    admin_delete_content,
    ban_user,
    block_community,
    file_report,
    review_report,
    suspend_user,
    unban_user,
    unblock_community,
)

User = get_user_model()


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class ReportCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ReportCreateSerializer,
        responses={201: ReportSerializer},
    )
    def post(self, request):
        serializer = ReportCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = file_report(
            reporter=request.user,
            target_type=serializer.validated_data["target_type"],
            target_id=serializer.validated_data["target_id"],
            reason=serializer.validated_data["reason"],
            description=serializer.validated_data.get("description", ""),
        )
        return Response(ReportSerializer(report).data, status=status.HTTP_201_CREATED)


class AdminReportListView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        parameters=[
            OpenApiParameter("status", OpenApiTypes.STR, description="Filter by report status"),
            OpenApiParameter("target_type", OpenApiTypes.STR, description="Filter by target type"),
        ],
        responses={200: ReportSerializer(many=True)},
    )
    def get(self, request):
        status_param = request.query_params.get("status")
        target_type = request.query_params.get("target_type")
        reports = list_reports(status=status_param, target_type=target_type)

        paginator = StandardPagination()
        page = paginator.paginate_queryset(reports, request)
        serializer = ReportSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class AdminReportDetailView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(responses={200: ReportSerializer})
    def get(self, request, pk: int):
        report = get_object_or_404(Report, pk=pk)
        return Response(ReportSerializer(report).data)

    @extend_schema(
        request=ReportReviewSerializer,
        responses={200: ReportSerializer},
    )
    def patch(self, request, pk: int):
        report = get_object_or_404(Report, pk=pk)
        serializer = ReportReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = review_report(
            reviewer=request.user,
            report=report,
            status=serializer.validated_data["status"],
            resolution_notes=serializer.validated_data.get("resolution_notes", ""),
        )
        return Response(ReportSerializer(updated).data)


class AdminUserSuspendView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        request=SuspendUserInputSerializer,
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request, pk: int):
        target_user = get_object_or_404(User, pk=pk)
        serializer = SuspendUserInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        suspended_user = suspend_user(
            actor=request.user,
            user=target_user,
            duration_hours=serializer.validated_data["duration_hours"],
            reason=serializer.validated_data["reason"],
        )
        return Response(
            {
                "status": "ok",
                "user_id": suspended_user.id,
                "user_status": suspended_user.status,
                "suspended_until": suspended_user.suspended_until.isoformat(),
            }
        )


class AdminUserBanView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        request=ReasonRequiredInputSerializer,
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request, pk: int):
        target_user = get_object_or_404(User, pk=pk)
        serializer = ReasonRequiredInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        banned_user = ban_user(
            actor=request.user,
            user=target_user,
            reason=serializer.validated_data["reason"],
        )
        return Response(
            {
                "status": "ok",
                "user_id": banned_user.id,
                "user_status": banned_user.status,
            }
        )


class AdminUserUnbanView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        request=ReasonRequiredInputSerializer,
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request, pk: int):
        target_user = get_object_or_404(User, pk=pk)
        serializer = ReasonRequiredInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        restored_user = unban_user(
            actor=request.user,
            user=target_user,
            reason=serializer.validated_data["reason"],
        )
        return Response(
            {
                "status": "ok",
                "user_id": restored_user.id,
                "user_status": restored_user.status,
            }
        )


class AdminCommunityBlockView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        request=ReasonRequiredInputSerializer,
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request, commname: str):
        community = get_object_or_404(Community, commname=commname)
        serializer = ReasonRequiredInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        blocked_comm = block_community(
            actor=request.user,
            community=community,
            reason=serializer.validated_data["reason"],
        )
        return Response(
            {
                "status": "ok",
                "commname": blocked_comm.commname,
                "blocked_at": blocked_comm.blocked_at.isoformat(),
            }
        )


class AdminCommunityUnblockView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        request=ReasonRequiredInputSerializer,
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request, commname: str):
        community = get_object_or_404(Community, commname=commname)
        serializer = ReasonRequiredInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        unblocked_comm = unblock_community(
            actor=request.user,
            community=community,
            reason=serializer.validated_data["reason"],
        )
        return Response(
            {
                "status": "ok",
                "commname": unblocked_comm.commname,
                "blocked_at": None,
            }
        )


class AdminDeleteContentView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        request=ReasonRequiredInputSerializer,
        parameters=[
            OpenApiParameter(
                "type",
                OpenApiTypes.STR,
                required=True,
                description="BUBBLEGRAM or COMMENT",
            ),
            OpenApiParameter("id", OpenApiTypes.INT, required=True, description="Content ID"),
        ],
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request):
        content_type = request.query_params.get("type")
        content_id = request.query_params.get("id")
        serializer = ReasonRequiredInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        admin_delete_content(
            actor=request.user,
            content_type=content_type,
            content_id=content_id,
            reason=serializer.validated_data["reason"],
        )
        return Response({"status": "ok", "deleted": True})


class AdminSoapAdjustmentView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        request=AdminSoapAdjustmentInputSerializer,
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request, wallet_id: int):
        wallet = get_object_or_404(Wallet, pk=wallet_id)
        serializer = AdminSoapAdjustmentInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tx = admin_adjust_soap(
            actor=request.user,
            wallet=wallet,
            amount=serializer.validated_data["amount"],
            reason=serializer.validated_data["reason"],
        )
        return Response(
            {
                "status": "ok",
                "transaction_id": tx.id,
                "amount": tx.amount,
                "balance_after": tx.balance_after,
            }
        )


class AdminAuditLogListView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        parameters=[
            OpenApiParameter("action", OpenApiTypes.STR, description="Filter by audit action"),
            OpenApiParameter("target_type", OpenApiTypes.STR, description="Filter by target type"),
        ],
        responses={200: AuditLogSerializer(many=True)},
    )
    def get(self, request):
        action = request.query_params.get("action")
        target_type = request.query_params.get("target_type")
        logs = list_audit_logs(action=action, target_type=target_type)

        paginator = StandardPagination()
        page = paginator.paginate_queryset(logs, request)
        serializer = AuditLogSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
