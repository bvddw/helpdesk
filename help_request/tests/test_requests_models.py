from django.test import TestCase
from help_request.models import HelpRequest, DeclinedRequest, StatusChoices, PriorityChoices
from user_app.models import MyUser


class HelpRequestTestCase(TestCase):
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
        )

    def test_request_str(self):
        self.assertEquals(
            str(self.help_request),
            f"{self.help_request.requester} -- {self.help_request.subject} -- {self.help_request.priority} -- {self.help_request.status}"
            )

    def test_default_status(self):
        self.assertEquals(StatusChoices.ACTIVE, self.help_request.status)

    def test_priority(self):
        self.assertEquals(PriorityChoices.MEDIUM, self.help_request.priority)


class DeclinedRequestTestCase(TestCase):
    def setUp(self):
        self.user = MyUser.objects.create(username="test_user", password="password")

        self.help_request = HelpRequest.objects.create(
            subject="Test Subject",
            text="Test Request",
            requester=self.user,
            priority=PriorityChoices.MEDIUM,
            status=StatusChoices.DECLINED,
        )

        self.declined_request = DeclinedRequest.objects.create(
            declined_request=self.help_request,
            comment="Test Comment",
        )

    def test_declined_request_str(self):
        self.assertEqual(
            str(self.declined_request),
            f"{self.help_request} -- declined"
        )

    def test_declined_request_status(self):
        self.assertEquals(StatusChoices.DECLINED, self.declined_request.declined_request.status)

    def test_declined_request_priority(self):
        self.assertEquals(PriorityChoices.MEDIUM, self.declined_request.declined_request.priority)
