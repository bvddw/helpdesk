from django.http import HttpResponseRedirect
from django.test import TestCase

from user_app.forms import RegistrateUserForm, LoginUserForm
from user_app.models import MyUser
from django.urls import reverse


class NotAuthenticatedViewTest(TestCase):
    def setUp(self):
        self.user = MyUser.objects.create_user(
            username="testUser",
            password="testPassword",
        )

    def test_not_authenticated_view_without_authentication(self):
        response = self.client.get(reverse('user:not_authenticated_view'))
        self.assertEqual(response.status_code, 200)

    def test_not_authenticated_view_authenticated(self):
        self.client.login(username=self.user.username, password="testPassword")
        response = self.client.get(reverse('user:not_authenticated_view'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('main_view'))


class LogoutUserViewTest(TestCase):
    def setUp(self):
        self.user = MyUser.objects.create_user(
            username='testUser',
            password='testPassword',
        )

    def test_logout_user(self):
        # Log the user in before attempting to log them out
        self.client.login(username=self.user.username, password='testPassword')
        response = self.client.get(reverse('user:logout_user_view'))

        # Check that the response is a HttpResponseRedirect
        self.assertIsInstance(response, HttpResponseRedirect)

        # Check that the URL in the response redirects to the login view
        self.assertEqual(response.url, reverse('user:login_user_view'))

    def test_logout_unauthenticated_user(self):
        response = self.client.get(reverse('user:logout_user_view'))

        # Check that the response is a HttpResponseRedirect
        self.assertIsInstance(response, HttpResponseRedirect)

        # Check that the URL in the response redirects to the login view
        self.assertEqual(response.url, reverse('user:login_user_view'))


class RegisterUserViewTest(TestCase):
    def setUp(self):
        self.valid_form_data = {
            'username': 'testUser',
            'password': 'testPassword',
            'confirm_password': 'testPassword',
        }

        self.invalid_form_data = {
            'username': 'testUser',
            'password': 'testPassword',
            'confirm_password': 'mismatchedPassword',
        }

    def test_get_registration_form(self):
        response = self.client.get(reverse('user:register_user_view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register_view.html')
        self.assertIsInstance(response.context['form'], RegistrateUserForm)

    def test_post_valid_registration_form(self):
        response = self.client.post(reverse('user:register_user_view'), self.valid_form_data)

        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(response.url, reverse('user:login_user_view'))
        self.assertTrue(MyUser.objects.filter(username='testUser').exists())

    def test_post_invalid_registration_form(self):
        response = self.client.post(reverse('user:register_user_view'), self.invalid_form_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register_view.html')
        self.assertFalse(response.context['form'].is_valid())
        self.assertFalse(MyUser.objects.filter(username='testUser').exists())


class LoginUserViewTest(TestCase):
    def setUp(self):
        self.user = MyUser.objects.create_user(
            username='testUser',
            password='testPassword',
        )
        self.valid_login_data = {
            'username': 'testUser',
            'password': 'testPassword',
        }
        self.invalid_login_data = {
            'username': 'testUser',
            'password': '',
        }

    def test_get_login_form_authenticated_user(self):
        self.client.login(username=self.user.username, password='testPassword')

        response = self.client.get(reverse('user:login_user_view'))
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(response.url, reverse('main_view'))

    def test_get_login_form_unauthenticated_user(self):
        response = self.client.get(reverse('user:login_user_view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login_view.html')
        self.assertIsInstance(response.context['form'], LoginUserForm)

    def test_post_valid_login_form(self):
        response = self.client.post(reverse('user:login_user_view'), self.valid_login_data)
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(response.url, reverse('main_view'))

    def test_post_invalid_login_form(self):
        response = self.client.post(reverse('user:login_user_view'), self.invalid_login_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login_view.html')
        self.assertIsInstance(response.context['form'], LoginUserForm)
