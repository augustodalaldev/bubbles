import factory

from apps.accounts.tests.factories import UserFactory
from apps.communities.models import Community, CommunityMember, MemberRole, MemberState


class CommunityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Community

    commname = factory.Sequence(lambda n: f"comm_{n:04d}")
    name = factory.Faker("catch_phrase")
    description = factory.Faker("sentence")


class CommunityMemberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CommunityMember

    community = factory.SubFactory(CommunityFactory)
    user = factory.SubFactory(UserFactory)
    role = MemberRole.MEMBER
    current_state = MemberState.ACTIVE
