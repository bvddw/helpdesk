from django.http import HttpResponseRedirect
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, render, reverse
from .models import HelpRequest, StatusChoices, DeclinedRequest
from comments.forms import CommentForm
from .forms import HelpRequestCreateForm, HelpRequestUpdateForm, DeclinedRequestForm


class RequestListView(ListView):
    template_name = 'request_list_view.html'
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
        return self.model.objects.filter(requester=user.id,
                                         status__in=['Approved', 'Declined', 'In process', 'Completed'])


class RequestDetailView(DetailView):
    model = HelpRequest
    template_name = 'request_detail_view.html'
    context_object_name = 'current_request'
    form = CommentForm

    def get_object(self, queryset=None):
        pk = self.kwargs['pk']
        request_to_display = get_object_or_404(self.model, id=pk)
        return request_to_display

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            context = {
                self.context_object_name: self.get_object(),
            }
            if self.get_object().status == StatusChoices.IN_PROCESS:
                context['form'] = CommentForm()
            return render(request, self.template_name, context)
        if request.user == self.get_object().requester:
            if self.get_object().status == StatusChoices.ACTIVE:
                url = reverse('main_view')
                return HttpResponseRedirect(url)
            context = {
                self.context_object_name: self.get_object(),
            }
            if self.get_object().status == StatusChoices.IN_PROCESS:
                context['form'] = CommentForm()
            return render(request, self.template_name, context)
        url = reverse('main_view')
        return HttpResponseRedirect(url)

    def post(self, request, *args, **kwargs):
        if self.get_object().status == StatusChoices.IN_PROCESS:
            form = CommentForm(request.POST)
            if form.is_valid():
                author = request.user
                help_request = self.get_object()

                form.create_comment(author=author, help_request=help_request)
                url = reverse('requests:request_detail_view', kwargs={'pk': kwargs.get('pk')})
                return HttpResponseRedirect(url)
            else:
                context = {
                    self.context_object_name: self.get_object(),
                    'form': form,
                }
            return render(request, self.template_name, context)
        url = reverse('requests:request_detail_view', kwargs={'pk': kwargs.get('pk')})
        return HttpResponseRedirect(url)


class CreateRequestView(CreateView):
    model = HelpRequest
    template_name = 'create_request_view.html'
    form_class = HelpRequestCreateForm

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            url = reverse('user:login_user_view')
            return HttpResponseRedirect(url)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.requester = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('requests:request_detail_view', kwargs={'pk': self.object.pk})


class UpdateRequestView(UpdateView):
    model = HelpRequest
    template_name = 'update_request_view.html'
    form_class = HelpRequestUpdateForm
    pk_url_kwarg = 'pk'

    def get(self, request, *args, **kwargs):
        cur_request = get_object_or_404(HelpRequest, id=kwargs.get(self.pk_url_kwarg))
        if request.user != cur_request.requester:
            url = reverse('requests:request_list_view')
            return HttpResponseRedirect(url)
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('requests:request_detail_view', kwargs={'pk': self.object.pk})


class DeleteRequestView(DeleteView):
    model = HelpRequest
    template_name = 'delete_request_view.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'context'

    def get(self, request, *args, **kwargs):
        cur_request = get_object_or_404(HelpRequest, id=kwargs.get(self.pk_url_kwarg))
        if request.user != cur_request.requester:
            url = reverse('requests:request_list_view')
            return HttpResponseRedirect(url)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = kwargs.get('pk')
        return context

    def get_success_url(self):
        return reverse('main_view')


class ToCheckRequestsView(ListView):
    template_name = 'request_list_view.html'
    context_object_name = 'requests'
    model = HelpRequest

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_superuser:
            url = reverse('main_view')
            return HttpResponseRedirect(url)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return self.model.objects.filter(status=StatusChoices.ACTIVE).exclude(requester=self.request.user)


class ForRestorationRequestsView(ListView):
    template_name = 'request_list_view.html'
    context_object_name = 'requests'
    model = HelpRequest

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_superuser:
            url = reverse('main_view')
            return HttpResponseRedirect(url)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return self.model.objects.filter(status=StatusChoices.FOR_RESTORATION).exclude(requester=self.request.user)


class ApproveRequestView(View):
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        cur_request = get_object_or_404(HelpRequest, id=pk)
        if (
                cur_request.status == StatusChoices.ACTIVE or cur_request.status == StatusChoices.FOR_RESTORATION) and request.user.is_superuser and request.user != cur_request.requester:
            cur_request.status = StatusChoices.APPROVED
            cur_request.save()
            url = reverse('requests:request_detail_view', kwargs={'pk': pk})
            return HttpResponseRedirect(url)
        url = reverse('main_view')
        return HttpResponseRedirect(url)


class DeclineRequestView(CreateView):
    model = DeclinedRequest
    form_class = DeclinedRequestForm
    template_name = 'decline_request_view.html'

    def get(self, request, *args, **kwargs):
        request_to_dec = get_object_or_404(HelpRequest, id=kwargs.get('pk'))
        if request_to_dec.status not in [StatusChoices.ACTIVE, StatusChoices.FOR_RESTORATION] or (not request.user.is_superuser) or (request.user == request_to_dec.requester):
            return HttpResponseRedirect(reverse('main_view'))
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        request_to_dec = get_object_or_404(HelpRequest, id=self.kwargs.get('pk'))

        form.instance.declined_request = request_to_dec
        request_to_dec.status = StatusChoices.DECLINED
        request_to_dec.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('requests:request_detail_view', kwargs={'pk': self.kwargs.get('pk')})


class AskForReviewRequestView(View):
    def get(self, request, *args, **kwargs):
        cur_request = get_object_or_404(HelpRequest, id=kwargs.get('pk'))
        if request.user != cur_request.requester or cur_request.status != StatusChoices.DECLINED:
            url = reverse('main_view')
            return HttpResponseRedirect(url)
        declined_request = get_object_or_404(DeclinedRequest, declined_request=cur_request)
        declined_request.delete()
        cur_request.status = StatusChoices.FOR_RESTORATION
        cur_request.save()
        url = reverse('requests:request_detail_view', kwargs={'pk': self.kwargs.get('pk')})
        return HttpResponseRedirect(url)


class StartProcessingRequestView(View):
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        cur_request = get_object_or_404(HelpRequest, id=pk)
        if cur_request.status == StatusChoices.APPROVED and request.user.is_superuser and request.user != cur_request.requester:
            cur_request.status = StatusChoices.IN_PROCESS
            cur_request.save()
            url = reverse('requests:request_detail_view', kwargs={'pk': pk})
            return HttpResponseRedirect(url)
        url = reverse('main_view')
        return HttpResponseRedirect(url)


class CompleteProcessingRequestView(View):
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        cur_request = get_object_or_404(HelpRequest, id=pk)
        if cur_request.status == StatusChoices.IN_PROCESS and request.user.is_superuser and request.user != cur_request.requester:
            cur_request.status = StatusChoices.COMPLETED
            cur_request.save()
            url = reverse('requests:request_detail_view', kwargs={'pk': pk})
            return HttpResponseRedirect(url)
        url = reverse('main_view')
        return HttpResponseRedirect(url)
