from django.db import models
from user_app.models import MyUser
from help_request.models import HelpRequest
from django.utils import timezone


class Comment(models.Model):
    message = models.TextField()
    author = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='comments')
    help_request = models.ForeignKey(HelpRequest, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"comment -- {self.author} -- {self.help_request.subject}"
