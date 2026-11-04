import factory

from apps.accounts.tests.factories import UserFactory
from apps.social.models import Letter


class LetterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Letter

    sender = factory.SubFactory(UserFactory)
    recipient = factory.SubFactory(UserFactory)
    reply_to = None
    text = factory.Faker("paragraph")
