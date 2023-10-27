from datetime import timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from user_app.authentication import CustomTokenAuthentication
from helpdesk import settings


class CustomTokenAuthenticationTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(
            username='testUser',
            password='testPassword',
        )
        self.token = Token.objects.create(
            user=self.user,
            key='testToken',
        )
        self.auth = CustomTokenAuthentication()

    def test_authenticate_with_valid_token(self):
        user, token = self.auth.authenticate_credentials('testToken')
        self.assertEqual(user, self.user)
        self.assertEqual(token, self.token)

    def test_authenticate_with_invalid_token(self):
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate_credentials('invalidToken')

    def test_authenticate_for_inactive_user(self):
        self.user.is_active = False
        self.user.save()

        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate_credentials('testToken')

    def test_authenticate_with_expired_token(self):
        self.token.created = timezone.now() - timedelta(seconds=settings.TOKEN_INACTIVITY_EXPIRED_SECONDS + 10)
        self.token.save()

        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate_credentials('testToken')

        with self.assertRaises(Token.DoesNotExist):
            Token.objects.get(key='testToken')
