from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.customization.models import CustomizationItem
from apps.customization.selectors import list_catalog_items, list_user_inventory
from apps.customization.serializers import (
    CustomizationItemCreateUpdateSerializer,
    CustomizationItemSerializer,
    EquipCustomizationInputSerializer,
    PurchaseResponseSerializer,
    UserInventoryItemSerializer,
)
from apps.customization.services import equip_customization, purchase_customization_item


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class CustomizationCatalogView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return [AllowAny()]

    @extend_schema(
        parameters=[
            OpenApiParameter("type", OpenApiTypes.STR, description="Filter by item type"),
            OpenApiParameter("search", OpenApiTypes.STR, description="Search by name or code"),
        ],
        responses={200: CustomizationItemSerializer(many=True)},
    )
    def get(self, request):
        item_type = request.query_params.get("type")
        search = request.query_params.get("search")
        items = list_catalog_items(item_type=item_type, search=search)

        paginator = StandardPagination()
        page = paginator.paginate_queryset(items, request)
        serializer = CustomizationItemSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        request=CustomizationItemCreateUpdateSerializer,
        responses={201: CustomizationItemSerializer},
    )
    def post(self, request):
        serializer = CustomizationItemCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save()
        return Response(
            CustomizationItemSerializer(item, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class CustomizationCatalogDetailView(APIView):
    def get_permissions(self):
        if self.request.method in ["PATCH", "DELETE"]:
            return [IsAdminUser()]
        return [AllowAny()]

    @extend_schema(responses={200: CustomizationItemSerializer})
    def get(self, request, pk: int):
        item = get_object_or_404(CustomizationItem, pk=pk)
        return Response(CustomizationItemSerializer(item, context={"request": request}).data)

    @extend_schema(
        request=CustomizationItemCreateUpdateSerializer,
        responses={200: CustomizationItemSerializer},
    )
    def patch(self, request, pk: int):
        item = get_object_or_404(CustomizationItem, pk=pk)
        serializer = CustomizationItemCreateUpdateSerializer(item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        return Response(CustomizationItemSerializer(updated, context={"request": request}).data)

    @extend_schema(responses={204: None})
    def delete(self, request, pk: int):
        item = get_object_or_404(CustomizationItem, pk=pk)
        item.is_active = False
        item.save(update_fields=["is_active"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class PurchaseCustomizationView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={201: PurchaseResponseSerializer},
    )
    def post(self, request, pk: int):
        item = get_object_or_404(CustomizationItem, pk=pk)
        inventory_item = purchase_customization_item(user=request.user, item=item)

        wallet = getattr(request.user, "wallet", None)
        if wallet:
            wallet.refresh_from_db()
            remaining_soap = wallet.soap_balance
        else:
            remaining_soap = 0

        response_data = {
            "inventory_item": UserInventoryItemSerializer(
                inventory_item, context={"request": request}
            ).data,
            "remaining_soap": remaining_soap,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class UserInventoryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter("type", OpenApiTypes.STR, description="Filter by item type"),
        ],
        responses={200: UserInventoryItemSerializer(many=True)},
    )
    def get(self, request):
        item_type = request.query_params.get("type")
        items = list_user_inventory(user=request.user, item_type=item_type)

        paginator = StandardPagination()
        page = paginator.paginate_queryset(items, request)
        serializer = UserInventoryItemSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)


class EquipCustomizationView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request):
        return Response(request.user.customization_json or {}, status=status.HTTP_200_OK)

    @extend_schema(
        request=EquipCustomizationInputSerializer,
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request):
        serializer = EquipCustomizationInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item_ids = serializer.validated_data.get("item_ids")
        slots = serializer.validated_data.get("slots")

        equipped = equip_customization(
            user=request.user,
            item_ids=item_ids,
            slots=slots,
        )
        return Response(equipped, status=status.HTTP_200_OK)
