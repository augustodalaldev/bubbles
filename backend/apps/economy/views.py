from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.economy.models import EconomySettings
from apps.economy.serializers import (
    EconomySettingsSerializer,
    EconomySettingsUpdateSerializer,
)
from apps.economy.services import update_economy_settings


class EconomySettingsView(APIView):
    def get_permissions(self):
        if self.request.method in ["PATCH", "PUT"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    @extend_schema(responses={200: EconomySettingsSerializer})
    def get(self, request):
        settings_obj = EconomySettings.load()
        serializer = EconomySettingsSerializer(settings_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=EconomySettingsUpdateSerializer,
        responses={200: EconomySettingsSerializer},
    )
    def patch(self, request):
        settings_obj = EconomySettings.load()
        serializer = EconomySettingsUpdateSerializer(settings_obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = update_economy_settings(actor=request.user, data=serializer.validated_data)
        return Response(EconomySettingsSerializer(updated).data, status=status.HTTP_200_OK)
