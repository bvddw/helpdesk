from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.views.generic import TemplateView


class MainView(TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            url = reverse('user:not_authenticated_view')
            return HttpResponseRedirect(url)
        return super().get(request, *args, **kwargs)


class AboutView(TemplateView):
    template_name = "about.html"
