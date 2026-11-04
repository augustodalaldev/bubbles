from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError("The username must be set.")
        if not email:
            raise ValueError("The email must be set.")
        user = self.model(
            username=username.strip().lower(),
            email=email.strip().lower(),
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields["is_staff"] is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields["is_superuser"] is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        user = self._create_user(username, email, password, **extra_fields)
        try:
            from apps.economy.models import EconomySettings, Wallet

            settings_obj = EconomySettings.load()
            Wallet.objects.get_or_create(
                user=user,
                defaults={
                    "soap_balance": 0,
                    "passive_earn_rate": settings_obj.default_passive_earn_rate,
                },
            )
        except Exception:
            pass
        return user
