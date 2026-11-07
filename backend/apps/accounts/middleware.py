from datetime import timedelta

from django.utils import timezone


class UpdateLastSeenMiddleware:
    """Updates User.last_seen_at on authenticated requests, throttled to at most once per minute."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            now = timezone.now()
            if not user.last_seen_at or (now - user.last_seen_at) > timedelta(seconds=60):
                type(user).objects.filter(pk=user.pk).update(last_seen_at=now)
                user.last_seen_at = now

        return response
