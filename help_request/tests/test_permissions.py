from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from help_request.models import HelpRequest, PriorityChoices, StatusChoices
from help_request.serializers import RequestSerializer
from django.contrib.auth.models import User


class RequesterOrReadOnlyPermissionTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testUser',
            password='testPassword',
        )
        self.other_user = User.objects.create_user(
            username='otherUser',
            password='otherPassword',
        )
        self.superuser = User.objects.create_superuser(
            username='adminUser',
            password='adminPassword',
        )
        self.request = HelpRequest.objects.create(
            subject='Test Request',
            text='Test text for test request',
            priority=PriorityChoices.HIGH,
            requester=self.user,
            status=StatusChoices.ACTIVE,
        )

    def test_requester_can_edit_own_request(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(f'/requests/rest/{self.request.pk}/',
                                     {'text': 'Updated text'},
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_requester_cannot_edit_other_request(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(f'/requests/rest/{self.request.pk}/',
                                     {'text': 'Updated text'},
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_requester_can_view_own_request(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/requests/rest/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = RequestSerializer(HelpRequest.objects.filter(requester=self.user), many=True)
        self.assertEqual(response.data, serializer.data)

    def test_requester_cannot_view_other_request(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(f'/requests/rest/{self.request.pk}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_can_view_any_request(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(f'/requests/rest/{self.request.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
