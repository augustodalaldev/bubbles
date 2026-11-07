import factory
from django.utils import timezone

from apps.accounts.tests.factories import UserFactory
from apps.customization.models import CustomizationItem, CustomizationType, UserInventoryItem


class CustomizationItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomizationItem

    name = factory.Faker("word")
    code = factory.Sequence(lambda n: f"custom_item_{n:04d}")
    item_type = CustomizationType.AVATAR_FRAME
    description = factory.Faker("sentence")
    price = 10
    metadata = factory.LazyFunction(lambda: {"border_color": "#FFD700", "animation": "glow"})
    is_active = True
    created_at = factory.LazyFunction(timezone.now)


class UserInventoryItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserInventoryItem

    user = factory.SubFactory(UserFactory)
    item = factory.SubFactory(CustomizationItemFactory)
    acquired_at = factory.LazyFunction(timezone.now)
    transaction = None
