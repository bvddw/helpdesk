from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.views.generic import TemplateView, ListView
from help_request.models import HelpRequest


class MainView(ListView):
    template_name = 'index.html'
    context_object_name = 'requests'
    model = HelpRequest

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            url = reverse('user:not_authenticated_view')
            return HttpResponseRedirect(url)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.model.objects.all()
        user = self.request.user
        return self.model.objects.filter(requester=user.id)


class AboutView(TemplateView):
    template_name = "about.html"
