from django import forms
from .models import HelpRequest, PriorityChoices, DeclinedRequest, StatusChoices


class HelpRequestCreateForm(forms.ModelForm):
    class Meta:
        model = HelpRequest
        fields = ['subject', 'text', 'priority']

    subject = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control shadow',
            'placeholder': 'Subject',
        })
    )

    text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control shadow',
            'placeholder': 'Description',
            'rows': 6,
        })
    )

    priority = forms.ChoiceField(
        choices=PriorityChoices.CHOICES,
        widget=forms.Select(attrs={'class': 'form-control shadow'}),
    )

    def create_help_request(self, requester):
        help_request = HelpRequest.objects.create(
            subject=self.cleaned_data['subject'],
            text=self.cleaned_data['text'],
            requester=requester,
            priority=self.cleaned_data['priority'],
        )
        return help_request


class HelpRequestUpdateForm(forms.ModelForm):
    class Meta:
        model = HelpRequest
        fields = ['subject', 'text', 'priority']

    subject = forms.CharField(
        max_length=255,
        required=False,
        disabled=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control shadow',
            'placeholder': 'Subject',
        })
    )

    text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control shadow',
            'placeholder': 'Description',
            'rows': 6,
        })
    )

    priority = forms.ChoiceField(
        choices=PriorityChoices.CHOICES,
        widget=forms.Select(attrs={'class': 'form-control shadow'}),
    )

    def update_help_request(self, request_to_update):
        request_to_update.text = self.cleaned_data['text']
        request_to_update.priority = self.cleaned_data['priority']
        request_to_update.save()
        return request_to_update


class DeclinedRequestForm(forms.ModelForm):
    class Meta:
        model = DeclinedRequest
        fields = ['comment']

    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control shadow',
            'placeholder': 'Description',
            'rows': 6,
        })
    )

    def create_declined_request(self, request_to_decline):
        declined_request = DeclinedRequest.objects.create(
            declined_request=request_to_decline,
            comment=self.cleaned_data['comment'],
        )
        return declined_request
