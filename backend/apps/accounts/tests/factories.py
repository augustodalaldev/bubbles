from datetime import timedelta

import factory
from django.utils import timezone

from apps.accounts.models import User, UserConnection

DEFAULT_PASSWORD = "StrongPass123!"


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n:04d}")
    email = factory.LazyAttribute(lambda user: f"{user.username}@example.com")
    name = factory.Faker("name")
    birth_date = factory.LazyFunction(lambda: timezone.localdate() - timedelta(days=365 * 25))
    password = DEFAULT_PASSWORD

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        # Go through the manager so the password is hashed and fields are normalized.
        return model_class.objects.create_user(*args, **kwargs)


class UserConnectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserConnection

    follower = factory.SubFactory(UserFactory)
    followed = factory.SubFactory(UserFactory)
