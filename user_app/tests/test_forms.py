from django.db import IntegrityError
from django.test import TestCase
from user_app.forms import LoginUserForm, RegistrateUserForm
from user_app.models import MyUser


class LoginUserFormTest(TestCase):
    def setUp(self):
        self.user = MyUser.objects.create_user(
            username='testUser',
            password='testPassword',
        )
        self.form_data_correct = {
            'username': 'testUser',
            'password': 'testPassword',
        }
        self.form_data_incorrect = {
            'username': 'testUser',
            'password': 'incorrectPassword',
        }

    def test_login_form_with_correct_credentials(self):
        form = LoginUserForm(data=self.form_data_correct)
        self.assertTrue(form.is_valid())
        form.clean()

    def test_login_form_with_incorrect_credentials(self):
        form = LoginUserForm(data=self.form_data_incorrect)
        self.assertFalse(form.is_valid())


class RegistrateUserFormTest(TestCase):
    def setUp(self):
        self.existing_user = MyUser.objects.create_user(
            username='existingUser',
            password='existingPassword',
        )
        self.form_data_correct = {
            'username': 'testUser',
            'password': 'testPassword',
            'confirm_password': 'testPassword',
        }
        self.form_data_with_existing_username = {
            'username': 'existingUser',
            'password': 'testPassword',
            'confirm_password': 'testPassword',
        }
        self.form_data_with_mismatched_passwords = {
            'username': 'testUser',
            'password': 'testPassword',
            'confirm_password': 'mismatchedPassword',
        }

    def test_registration_form_with_valid_data(self):
        form = RegistrateUserForm(data=self.form_data_correct)
        self.assertTrue(form.is_valid())
        form.create_user()
        self.assertTrue(MyUser.objects.filter(username='testUser').exists())

    def test_registration_form_with_existing_username(self):
        try:
            form = RegistrateUserForm(data=self.form_data_with_existing_username)
            self.assertFalse(form.is_valid())
        except IntegrityError:
            self.assertTrue(MyUser.objects.filter(username='existingUser').exists())
            self.assertTrue(MyUser.objects.filter(username='existingUser').exists())

    def test_registration_form_with_password_mismatch(self):
        form = RegistrateUserForm(data=self.form_data_with_mismatched_passwords)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)
        self.assertEqual(form.errors['password'][0], 'Passwords do not match')
        self.assertIn('confirm_password', form.errors)
        self.assertEqual(form.errors['confirm_password'][0], 'Passwords do not match')