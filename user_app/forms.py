from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

from .models import MyUser


class LoginUserForm(forms.Form):
    username = forms.CharField(label="Username", widget=forms.TextInput(
        attrs={
            "type": "text",
            "class": "form-control shadow",
            "id": "username",
            "placeholder": "Username",
            "name": "username"
        }
    ))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(
        attrs={
            "type": "password",
            "class": "form-control shadow",
            "id": "password",
            "placeholder": "Password",
            "name": "password"
        }
    ))

    def clean(self):
        if not authenticate(**self.cleaned_data):
            raise ValidationError('Incorrect username or password.')


class RegistrateUserForm(forms.Form):
    username = forms.CharField(label="Username", widget=forms.TextInput(
        attrs={
            "type": "text",
            "class": "form-control shadow",
            "id": "username",
            "placeholder": "Username",
            "name": "username"
        }
    ))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(
        attrs={
            "type": "password",
            "class": "form-control shadow",
            "id": "password",
            "placeholder": "Password",
            "name": "password"
        }
    ))
    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(
        attrs={
            "type": "password",
            "class": "form-control shadow",
            "id": "confirmPassword",
            "placeholder": "Confirm Password",
            "name": "confirm_password"
        }
    ))

    def create_user(self):
        del self.cleaned_data["confirm_password"]
        MyUser.objects.create_user(**self.cleaned_data)

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            MyUser.objects.get(username=username)
            raise ValidationError("User with this username already registered.")
        except MyUser.DoesNotExist:
            return username

    def clean(self):
        password = self.cleaned_data["password"]
        confirm_password = self.cleaned_data["confirm_password"]
        if password != confirm_password:
            self.add_error("password", "Passwords do not match")
            self.add_error("confirm_password", "Passwords do not match")
