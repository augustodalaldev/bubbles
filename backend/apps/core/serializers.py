from rest_framework import serializers

from apps.accounts.serializers import PublicUserSerializer
from apps.communities.serializers import CommunityListSerializer


class SearchResultSerializer(serializers.Serializer):
    query = serializers.CharField()
    users = PublicUserSerializer(many=True)
    communities = CommunityListSerializer(many=True)
