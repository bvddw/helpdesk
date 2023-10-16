from rest_framework.authentication import TokenAuthentication
from django.utils import timezone
from django.conf import settings
from rest_framework import exceptions


class CustomTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')

        if not token.user.is_authenticated:
            raise exceptions.AuthenticationFailed('User is not authenticated.')

        # Проверьте, если пользователь был неактивен более минуты, и удалите токен
        if not token.user.is_superuser and (timezone.now() - token.created).total_seconds() > settings.TOKEN_INACTIVITY_EXPIRED_SECONDS:
            token.delete()
            raise exceptions.AuthenticationFailed('Token deleted due to inactivity.')

        # Обновите время последней активности в токене
        token.created = timezone.now()
        token.save()

        return token.user, token
