from django.test import TestCase

from comments.models import Comment
from help_request.models import HelpRequest, StatusChoices, PriorityChoices
from user_app.models import MyUser


class CommentTestCase(TestCase):
    def setUp(self) -> None:
        self.user = MyUser.objects.create(
            username="test_user",
            password="password",
        )
        self.help_request = HelpRequest.objects.create(
            subject="test_subject",
            text="Request for testing.",
            requester=self.user,
            priority=PriorityChoices.MEDIUM,
            status=StatusChoices.IN_PROCESS,
        )
        self.comment = Comment.objects.create(
            message="My test comment",
            author=self.user,
            help_request=self.help_request,
        )

    def test_comment_str(self):
        self.assertEquals(
            str(self.comment),
            f"comment -- {self.comment.author} -- {self.comment.help_request.subject}"
            )
