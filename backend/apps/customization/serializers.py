from rest_framework import serializers

from apps.customization.models import (
    CommunityInventoryItem,
    CustomizationItem,
    UserInventoryItem,
)


class CustomizationItemSerializer(serializers.ModelSerializer):
    is_owned = serializers.SerializerMethodField()
    is_equipped = serializers.SerializerMethodField()

    class Meta:
        model = CustomizationItem
        fields = [
            "id",
            "name",
            "code",
            "item_type",
            "scope",
            "description",
            "price",
            "metadata",
            "is_active",
            "created_at",
            "is_owned",
            "is_equipped",
        ]
        read_only_fields = fields

    def _get_community(self):
        """When serializing a community store, ownership/equipped refer to that community."""
        return self.context.get("community")

    def _get_user(self):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return request.user
        return None

    def _get_owned_ids(self):
        community = self._get_community()
        if community is not None:
            return set(
                CommunityInventoryItem.objects.filter(community=community).values_list(
                    "item_id", flat=True
                )
            )
        user = self._get_user()
        if not user:
            return set()
        cache_key = "_cached_user_inventory_ids"
        request = self.context.get("request")
        if request and hasattr(request, cache_key):
            return getattr(request, cache_key)
        owned_ids = set(
            UserInventoryItem.objects.filter(user=user).values_list("item_id", flat=True)
        )
        if request:
            setattr(request, cache_key, owned_ids)
        return owned_ids

    def _get_equipped_ids(self):
        community = self._get_community()
        owner = community if community is not None else self._get_user()
        if not owner or not owner.customization_json:
            return set()
        equipped_ids = set()
        for _slot, data in owner.customization_json.items():
            if isinstance(data, dict) and "id" in data:
                equipped_ids.add(data["id"])
        return equipped_ids

    def get_is_owned(self, obj) -> bool:
        return obj.id in self._get_owned_ids()

    def get_is_equipped(self, obj) -> bool:
        return obj.id in self._get_equipped_ids()


class CustomizationItemCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomizationItem
        fields = [
            "name",
            "code",
            "item_type",
            "scope",
            "description",
            "price",
            "metadata",
            "is_active",
        ]


class UserInventoryItemSerializer(serializers.ModelSerializer):
    item = CustomizationItemSerializer(read_only=True)
    is_equipped = serializers.SerializerMethodField()

    class Meta:
        model = UserInventoryItem
        fields = [
            "id",
            "item",
            "acquired_at",
            "is_equipped",
        ]
        read_only_fields = fields

    def get_is_equipped(self, obj) -> bool:
        request = self.context.get("request")
        user = request.user if request and request.user.is_authenticated else obj.user
        if not user or not user.customization_json:
            return False
        for _slot, data in user.customization_json.items():
            if isinstance(data, dict) and data.get("id") == obj.item_id:
                return True
        return False


class EquipCustomizationInputSerializer(serializers.Serializer):
    item_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
    )
    slots = serializers.DictField(
        child=serializers.IntegerField(allow_null=True),
        required=False,
    )

    def validate(self, attrs):
        if "item_ids" not in attrs and "slots" not in attrs:
            raise serializers.ValidationError("Either 'item_ids' or 'slots' must be provided.")
        return attrs


class PurchaseResponseSerializer(serializers.Serializer):
    inventory_item = UserInventoryItemSerializer()
    remaining_soap = serializers.IntegerField()


class CommunityInventoryItemSerializer(serializers.ModelSerializer):
    item = serializers.SerializerMethodField()
    is_equipped = serializers.SerializerMethodField()
    purchased_by_username = serializers.SerializerMethodField()

    class Meta:
        model = CommunityInventoryItem
        fields = ["id", "item", "acquired_at", "is_equipped", "purchased_by_username"]
        read_only_fields = fields

    def get_item(self, obj) -> dict:
        context = {**self.context, "community": obj.community}
        return CustomizationItemSerializer(obj.item, context=context).data

    def get_is_equipped(self, obj) -> bool:
        for data in (obj.community.customization_json or {}).values():
            if isinstance(data, dict) and data.get("id") == obj.item_id:
                return True
        return False

    def get_purchased_by_username(self, obj) -> str | None:
        return obj.purchased_by.username if obj.purchased_by_id else None


class EquipCommunityCustomizationInputSerializer(serializers.Serializer):
    slots = serializers.DictField(child=serializers.IntegerField(allow_null=True))


class CommunityPurchaseResponseSerializer(serializers.Serializer):
    inventory_item = CommunityInventoryItemSerializer()
    remaining_soap = serializers.IntegerField()
