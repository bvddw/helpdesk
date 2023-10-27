from django.contrib.auth.models import User
from django.test import TestCase
from help_request.models import HelpRequest, StatusChoices, PriorityChoices, DeclinedRequest
from help_request.serializers import RequestSerializer, DeclinedRequestSerializer


class RequestSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testUser',
            password='testPassword',
        )
        self.data = {
            'subject': 'Test Subject',
            'text': 'Test Text',
            'priority': PriorityChoices.HIGH,
            'status': StatusChoices.APPROVED,  # but in instance we will have Active status
        }

    def test_create_request_serializer_with_request_context(self):
        request = self.client.get('/requests/rest/')
        request.user = self.user
        serializer = RequestSerializer(
            data=self.data,
            context={'request': request},
        )

        self.assertTrue(serializer.is_valid())
        instance = serializer.save()

        self.assertEqual(instance.subject, 'Test Subject')
        self.assertEqual(instance.text, 'Test Text')
        self.assertEqual(instance.priority, 'High')
        self.assertEqual(instance.status, StatusChoices.ACTIVE)  # Always active after creating
        self.assertEqual(instance.requester, self.user)


class DeclinedRequestSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testUser',
            password='testPassword',
        )
        self.request = HelpRequest.objects.create(
            subject='Test request',
            text='Text for test request',
            priority=PriorityChoices.HIGH,
            requester=self.user,
        )
        self.declined_request = DeclinedRequest.objects.create(
            declined_request=self.request,
            comment='Rest of declining',
        )

    def test_declined_request_serializer(self):
        serializer = DeclinedRequestSerializer(instance=self.declined_request)

        expected_data = {
            'id': self.declined_request.id,
            'comment': 'Rest of declining',
            'declined_request': str(self.request),
        }

        self.assertEqual(serializer.data, expected_data)
