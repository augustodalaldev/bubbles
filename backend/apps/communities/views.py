from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.exceptions import DomainError
from apps.economy.services import ensure_community_wallet

from .models import CommunityMember, MemberRole, MemberState
from .selectors import (
    assert_community_visible,
    get_community_by_commname,
    list_communities,
    list_community_members,
)
from .serializers import (
    CommunityCreateSerializer,
    CommunityDetailSerializer,
    CommunityGuidelinesSerializer,
    CommunityListSerializer,
    CommunityMemberSerializer,
    CommunityUpdateSerializer,
    CommunityWalletSerializer,
    DeleteCommunitySerializer,
    MemberModerateSerializer,
    TransferLeadershipSerializer,
)
from .services import (
    archive_community,
    create_community,
    delete_community,
    demote_member,
    join_community,
    leave_community,
    moderate_member,
    promote_member,
    transfer_leadership,
    update_community,
    update_guidelines,
)


class CommunityListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: CommunityListSerializer(many=True)})
    def get(self, request):
        search = request.query_params.get("search")
        mine = request.query_params.get("mine", "").lower() in ("true", "1")
        qs = list_communities(user=request.user, search=search, mine=mine)

        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = CommunityListSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(request=CommunityCreateSerializer, responses={201: CommunityDetailSerializer})
    def post(self, request):
        serializer = CommunityCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        community = create_community(creator=request.user, **serializer.validated_data)
        out_serializer = CommunityDetailSerializer(community, context={"request": request})
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)


class CommunityDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: CommunityDetailSerializer})
    def get(self, request, commname: str):
        community = get_community_by_commname(commname=commname)
        assert_community_visible(community=community, viewer=request.user)
        serializer = CommunityDetailSerializer(community, context={"request": request})
        return Response(serializer.data)

    @extend_schema(request=DeleteCommunitySerializer, responses={204: None})
    def delete(self, request, commname: str):
        community = get_community_by_commname(commname=commname)
        serializer = DeleteCommunitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        delete_community(
            actor=request.user,
            community=community,
            confirm_commname=serializer.validated_data["confirm_commname"],
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(request=CommunityUpdateSerializer, responses={200: CommunityDetailSerializer})
    def patch(self, request, commname: str):
        community = get_community_by_commname(commname=commname)
        serializer = CommunityUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        community = update_community(
            actor=request.user, community=community, **serializer.validated_data
        )
        out_serializer = CommunityDetailSerializer(community, context={"request": request})
        return Response(out_serializer.data)


class CommunityGuidelinesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=CommunityGuidelinesSerializer, responses={200: CommunityDetailSerializer}
    )
    def patch(self, request, commname: str):
        community = get_community_by_commname(commname=commname)
        serializer = CommunityGuidelinesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        community = update_guidelines(
            actor=request.user,
            community=community,
            guidelines=serializer.validated_data["guidelines"],
        )
        out_serializer = CommunityDetailSerializer(community, context={"request": request})
        return Response(out_serializer.data)


class CommunityJoinView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses={201: CommunityMemberSerializer})
    def post(self, request, commname: str):
        community = get_community_by_commname(commname=commname)
        membership = join_community(user=request.user, community=community)
        serializer = CommunityMemberSerializer(membership, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommunityLeaveView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses={200: OpenApiTypes.OBJECT})
    def post(self, request, commname: str):
        community = get_community_by_commname(commname=commname)
        leave_community(user=request.user, community=community)
        return Response({"detail": "Successfully left community."}, status=status.HTTP_200_OK)


class CommunityMemberListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: CommunityMemberSerializer(many=True)})
    def get(self, request, commname: str):
        community = get_community_by_commname(commname=commname)
        assert_community_visible(community=community, viewer=request.user)
        state = request.query_params.get("state")
        members = list_community_members(community=community, state=state)

        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(members, request)
        serializer = CommunityMemberSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)


class CommunityMemberModerateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=MemberModerateSerializer, responses={200: CommunityMemberSerializer})
    def patch(self, request, commname: str, username: str):
        community = get_community_by_commname(commname=commname)
        serializer = MemberModerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        membership = moderate_member(
            actor=request.user,
            community=community,
            target_username=username,
            new_state=serializer.validated_data["current_state"],
        )
        return Response(CommunityMemberSerializer(membership, context={"request": request}).data)


class CommunityMemberPromoteView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses={200: CommunityMemberSerializer})
    def post(self, request, commname: str, username: str):
        community = get_community_by_commname(commname=commname)
        membership = promote_member(
            actor=request.user,
            community=community,
            target_username=username,
        )
        return Response(CommunityMemberSerializer(membership, context={"request": request}).data)


class CommunityMemberDemoteView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses={200: CommunityMemberSerializer})
    def post(self, request, commname: str, username: str):
        community = get_community_by_commname(commname=commname)
        membership = demote_member(
            actor=request.user,
            community=community,
            target_username=username,
        )
        return Response(CommunityMemberSerializer(membership, context={"request": request}).data)


class CommunityTransferLeadershipView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=TransferLeadershipSerializer, responses={200: CommunityMemberSerializer})
    def post(self, request, commname: str):
        community = get_community_by_commname(commname=commname)
        serializer = TransferLeadershipSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_leader = transfer_leadership(
            actor=request.user,
            community=community,
            new_leader_username=serializer.validated_data["new_leader_username"],
        )
        return Response(CommunityMemberSerializer(new_leader, context={"request": request}).data)


class CommunityArchiveView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses={200: CommunityDetailSerializer})
    def post(self, request, commname: str):
        community = get_community_by_commname(commname=commname)
        community = archive_community(actor=request.user, community=community)
        return Response(
            CommunityDetailSerializer(community, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )


class CommunityWalletView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: CommunityWalletSerializer})
    def get(self, request, commname: str):
        community = get_community_by_commname(commname=commname)

        if not request.user.is_staff:
            membership = CommunityMember.objects.filter(
                community=community, user=request.user
            ).first()
            if (
                not membership
                or membership.current_state != MemberState.ACTIVE
                or membership.role not in (MemberRole.COMM_ADMIN, MemberRole.LEADER)
            ):
                raise DomainError(
                    "You do not have permission to view this community wallet.",
                    code="permission_denied",
                    http_status=403,
                )

        wallet = ensure_community_wallet(community)
        return Response({"soap_balance": wallet.soap_balance})
