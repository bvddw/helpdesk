from django import forms

from .models import Comment


class CommentForm(forms.Form):
    comment = forms.CharField(label="Comment", widget=forms.TextInput(
        attrs={
            "type": "text",
            "class": "form-control shadow",
            "id": "comment",
            "placeholder": "Comment",
            "name": "comment"
        }
    ))

    def create_comment(self, author, help_request):
        Comment.objects.create(
            message=self.cleaned_data['comment'],
            author=author,
            help_request=help_request,
        )