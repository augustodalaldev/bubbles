from datetime import timedelta

import factory
from django.utils import timezone

from apps.accounts.tests.factories import UserFactory
from apps.content.models import (
    Bubblegram,
    BubblegramMedia,
    BubblegramSupport,
    BubblegramType,
    Bubblepop,
    Comment,
    CommentSupport,
)


class BubblegramFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Bubblegram

    user = factory.SubFactory(UserFactory)
    community = None
    text = factory.Faker("sentence")
    type = BubblegramType.TEXT
    soap_count = 0


class BubblegramMediaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BubblegramMedia

    bubblegram = factory.SubFactory(BubblegramFactory, type=BubblegramType.MEDIA)
    media = factory.django.ImageField(color="blue")
    position = factory.Sequence(lambda n: n)


class BubblepopFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Bubblepop

    user = factory.SubFactory(UserFactory)
    image = factory.django.ImageField(color="green")
    description = factory.Faker("sentence")
    expires_at = factory.LazyFunction(lambda: timezone.now() + timedelta(hours=24))


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    bubblegram = factory.SubFactory(BubblegramFactory)
    user = factory.SubFactory(UserFactory)
    parent = None
    text = factory.Faker("sentence")
    soap_count = 0


class BubblegramSupportFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BubblegramSupport

    bubblegram = factory.SubFactory(BubblegramFactory)
    donor = factory.SubFactory(UserFactory)


class CommentSupportFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CommentSupport

    comment = factory.SubFactory(CommentFactory)
    donor = factory.SubFactory(UserFactory)
