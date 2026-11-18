from rest_framework import serializers

from apps.economy.models import EconomySettings


class EconomySettingsSerializer(serializers.ModelSerializer):
    updated_by_username = serializers.SerializerMethodField()

    class Meta:
        model = EconomySettings
        fields = [
            "id",
            "signup_grant",
            "support_cost",
            "author_credit",
            "community_credit",
            "bubblegram_profile_cost",
            "bubblegram_community_cost",
            "bubblepop_hours_per_soap",
            "bubblepop_min_hours",
            "bubblepop_max_hours",
            "founding_cost",
            "default_passive_earn_rate",
            "passive_interval_minutes",
            "passive_daily_cap",
            "updated_by",
            "updated_by_username",
            "updated_at",
        ]
        read_only_fields = ["id", "updated_by", "updated_by_username", "updated_at"]

    def get_updated_by_username(self, obj: EconomySettings) -> str | None:
        return obj.updated_by.username if obj.updated_by_id else None


class EconomySettingsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EconomySettings
        fields = [
            "signup_grant",
            "support_cost",
            "author_credit",
            "community_credit",
            "bubblegram_profile_cost",
            "bubblegram_community_cost",
            "bubblepop_hours_per_soap",
            "bubblepop_min_hours",
            "bubblepop_max_hours",
            "founding_cost",
            "default_passive_earn_rate",
            "passive_interval_minutes",
            "passive_daily_cap",
        ]
        extra_kwargs = {field: {"required": False} for field in fields}

    def validate(self, attrs):
        instance = self.instance or EconomySettings.load()
        min_hours = attrs.get("bubblepop_min_hours", instance.bubblepop_min_hours)
        max_hours = attrs.get("bubblepop_max_hours", instance.bubblepop_max_hours)
        if min_hours > max_hours:
            raise serializers.ValidationError(
                {"bubblepop_min_hours": "O mínimo de horas não pode ser maior que o máximo."}
            )

        hours_per_soap = attrs.get("bubblepop_hours_per_soap", instance.bubblepop_hours_per_soap)
        if hours_per_soap <= 0:
            raise serializers.ValidationError(
                {"bubblepop_hours_per_soap": "As horas por soap devem ser maiores que zero."}
            )

        interval = attrs.get("passive_interval_minutes", instance.passive_interval_minutes)
        if interval <= 0:
            raise serializers.ValidationError(
                {
                    "passive_interval_minutes": (
                        "O intervalo do ganho passivo deve ser maior que zero."
                    )
                }
            )

        return attrs
