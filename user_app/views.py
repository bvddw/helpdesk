from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.views import View
from django.views.generic import TemplateView

from .forms import LoginUserForm, RegistrateUserForm


class LoginUserView(LoginView):
    template_name = 'login_view.html'

    def get(self, request, **kwargs):
        form = LoginUserForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, **kwargs):
        form = LoginUserForm(request.POST)
        if form.is_valid():
            user = authenticate(**form.cleaned_data)
            if user is not None:
                login(request, user)
                url = reverse('main_view')
                return HttpResponseRedirect(url)
        return render(request, self.template_name, {'form': form})


class RegisterUserView(View):
    template_name = 'register_view.html'

    def get(self, request):
        form = RegistrateUserForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = RegistrateUserForm(request.POST)
        if form.is_valid():
            form.create_user()
            url = reverse('user:login_user_view')
            return HttpResponseRedirect(url)
        return render(request, self.template_name, {'form': form})


class LogoutUserView(View):
    def get(self, request):
        url = reverse('user:login_user_view')
        logout(request)
        return HttpResponseRedirect(url)


class NotAuthenticatedView(TemplateView):
    template_name = 'not_authenticated_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
