from django.test import TestCase
from user_app.models import MyUser
from rest_framework.test import APIClient
from rest_framework import status
from help_request.models import HelpRequest, DeclinedRequest, StatusChoices, PriorityChoices
from help_request.serializers import RequestSerializer


class RequestViewSetTest(TestCase):
    def setUp(self):
        self.user = MyUser.objects.create_user(
            username='testUser',
            password='testPassword',
        )
        self.superuser = MyUser.objects.create_superuser(
            username='adminUser',
            password='adminPassword',
        )
        self.client = APIClient()
        self.help_request = HelpRequest.objects.create(
            subject='request1',
            text='text1',
            requester=self.user,
            priority=PriorityChoices.HIGH,
            status=StatusChoices.APPROVED,
        )

    def test_list_requests_as_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get('/requests/rest/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_requests_as_requester(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/requests/rest/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_requests_with_priority_filter(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get('/requests/rest/', {'priority_type': 'High'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_requests_with_status_filter(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get('/requests/rest/', {'status_type': 'Approved'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_requests_with_combined_filters(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get('/requests/rest/', {'priority_type': 'High', 'status_type': 'Approved'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_requests_unauthenticated(self):
        response = self.client.get('/requests/rest/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_request(self):
        self.client.force_authenticate(user=self.user)
        data = {'subject': 'new request', 'text': 'this is new request', 'priority': 'Medium'}
        response = self.client.post('/requests/rest/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_request(self):
        self.client.force_authenticate(user=self.user)
        data = {'priority': 'Low'}
        response = self.client.patch('/requests/rest/{}/'.format(self.help_request.id), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.help_request.refresh_from_db()
        self.assertEqual(self.help_request.priority, 'Low')

    def test_delete_request(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete('/requests/rest/{}/'.format(self.help_request.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class RestAllRequestsTest(TestCase):
    def setUp(self):
        self.user = MyUser.objects.create_user(
            username='testUser',
            password='testPassword',
        )
        self.superuser = MyUser.objects.create_superuser(
            username='adminUser',
            password='adminPassword',
        )
        self.client = APIClient()
        HelpRequest.objects.create(
            subject='request1',
            text='text1',
            requester=self.user,
            priority=PriorityChoices.LOW,
            status=StatusChoices.FOR_RESTORATION,
        )
        HelpRequest.objects.create(
            subject='request2',
            text='text2',
            requester=self.user,
            priority=PriorityChoices.MEDIUM,
            status=StatusChoices.FOR_RESTORATION,
        )
        HelpRequest.objects.create(
            subject='request3',
            text='text3',
            requester=self.superuser,
            priority=PriorityChoices.HIGH,
            status=StatusChoices.FOR_RESTORATION,
        )

    def test_get_requests_all_request_unauthorized(self):
        response = self.client.get('/requests/rest/all-requests/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_requests_for_restoration_by_admin_user(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get('/requests/rest/all-requests/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = RequestSerializer(HelpRequest.objects.all(), many=True)
        self.assertEqual(response.data, serializer.data)

    def test_get_requests_for_restoration_by_default_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/requests/rest/all-requests/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class RestForRestorationTest(TestCase):
    def setUp(self):
        self.user = MyUser.objects.create_user(
            username='testUser',
            password='testPassword',
        )
        self.superuser = MyUser.objects.create_superuser(
            username='adminUser',
            password='adminPassword',
        )
        self.client = APIClient()
        HelpRequest.objects.create(
            subject='request1',
            text='text1',
            requester=self.user,
            priority=PriorityChoices.LOW,
            status=StatusChoices.FOR_RESTORATION,
        )
        HelpRequest.objects.create(
            subject='request2',
            text='text2',
            requester=self.user,
            priority=PriorityChoices.MEDIUM,
            status=StatusChoices.FOR_RESTORATION,
        )
        HelpRequest.objects.create(
            subject='request3',
            text='text3',
            requester=self.superuser,
            priority=PriorityChoices.HIGH,
            status=StatusChoices.FOR_RESTORATION,
        )

    def test_get_requests_for_restoration_unauthorized(self):
        response = self.client.get('/requests/rest/for-restoration/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_requests_for_restoration_by_admin(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get('/requests/rest/for-restoration/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = RequestSerializer(HelpRequest.objects.filter(status=StatusChoices.FOR_RESTORATION), many=True)
        self.assertEqual(response.data, serializer.data)

    def test_get_requests_for_restoration_by_default_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/requests/rest/for-restoration/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CommentsViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = MyUser.objects.create_user(
            username='testUser',
            password='testPassword',
        )
        self.superuser = MyUser.objects.create_superuser(
            username='adminUser',
            password='adminPassword',
        )
        self.help_request = HelpRequest.objects.create(
            subject='request1',
            text='text1',
            priority=PriorityChoices.HIGH,
            requester=self.user,
            status=StatusChoices.IN_PROCESS,
        )
        self.comment_data = {
            'message': 'Test comment text',
        }

    def test_get_comments_as_requester(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/requests/rest/{self.help_request.pk}/comments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_comments_as_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(f'/requests/rest/{self.help_request.pk}/comments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_comments_unauthorized(self):
        response = self.client.get(f'/requests/rest/{self.help_request.pk}/comments/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_comment_as_requester(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/requests/rest/{self.help_request.pk}/comments/', self.comment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_comment_as_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.post(f'/requests/rest/{self.help_request.pk}/comments/', self.comment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_comment_with_invalid_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/requests/rest/{self.help_request.pk}/comments/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_comment_to_closed_request(self):
        self.help_request.status = StatusChoices.COMPLETED
        self.help_request.save()
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/requests/rest/{self.help_request.pk}/comments/', self.comment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class RestApproveTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = MyUser.objects.create_user(
            username='testUser',
            password='testPassword',
        )
        self.superuser = MyUser.objects.create_superuser(
            username='adminUser',
            password='adminPassword',
        )
        self.active_request = HelpRequest.objects.create(
            subject='request1',
            text='text1',
            priority=PriorityChoices.HIGH,
            requester=self.user,
            status=StatusChoices.ACTIVE,
        )
        self.restoration_request = HelpRequest.objects.create(
            subject='request1',
            text='text1',
            priority=PriorityChoices.HIGH,
            requester=self.user,
            status=StatusChoices.FOR_RESTORATION,
        )
        self.other_request = HelpRequest.objects.create(
            subject='request1',
            text='text1',
            priority=PriorityChoices.HIGH,
            requester=self.user,
            status=StatusChoices.COMPLETED,
        )

    def test_approve_active_request_unauthenticated(self):
        old_status = self.active_request.status
        response = self.client.get(f'/requests/rest/{self.active_request.pk}/approve/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.active_request.refresh_from_db()
        self.assertEqual(self.active_request.status, old_status)

    def test_approve_restoration_request_unauthenticated(self):
        old_status = self.restoration_request.status
        response = self.client.get(f'/requests/rest/{self.restoration_request.pk}/approve/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.restoration_request.refresh_from_db()
        self.assertEqual(self.restoration_request.status, old_status)

    def test_approve_other_request_unauthenticated(self):
        old_status = self.other_request.status
        response = self.client.get(f'/requests/rest/{self.other_request.pk}/approve/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.other_request.refresh_from_db()
        self.assertEqual(self.other_request.status, old_status)

    def test_approve_active_by_admin(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(f'/requests/rest/{self.active_request.pk}/approve/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.active_request.refresh_from_db()
        self.assertEqual(self.active_request.status, StatusChoices.APPROVED)

    def test_approve_for_restoration_by_admin(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(f'/requests/rest/{self.restoration_request.pk}/approve/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.restoration_request.refresh_from_db()
        self.assertEqual(self.restoration_request.status, StatusChoices.APPROVED)

    def test_approve_other_approved_request_by_admin(self):
        self.client.force_authenticate(user=self.superuser)
        old_status = self.other_request.status
        response = self.client.get(f'/requests/rest/{self.other_request.pk}/approve/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.other_request.refresh_from_db()
        self.assertEqual(self.other_request.status, old_status)

    def test_approve_active_by_default_user(self):
        self.client.force_authenticate(user=self.user)
        old_status = self.active_request.status
        response = self.client.get(f'/requests/rest/{self.active_request.pk}/approve/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.active_request.refresh_from_db()
        self.assertEqual(self.active_request.status, old_status)

    def test_approve_for_restoration_by_default_user(self):
        self.client.force_authenticate(user=self.user)
        old_status = self.restoration_request.status
        response = self.client.get(f'/requests/rest/{self.restoration_request.pk}/approve/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.restoration_request.refresh_from_db()
        self.assertEqual(self.restoration_request.status, old_status)

    def test_approve_other_approved_request_by_default_user(self):
        self.client.force_authenticate(user=self.user)
        old_status = self.other_request.status
        response = self.client.get(f'/requests/rest/{self.other_request.pk}/approve/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.other_request.refresh_from_db()
        self.assertEqual(self.other_request.status, old_status)


class RestStartProcessingTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = MyUser.objects.create_user(
            username='testUser',
            password='testPassword',
        )
        self.superuser = MyUser.objects.create_superuser(
            username='adminUser',
            password='adminPassword',
        )
        self.approve_request = HelpRequest.objects.create(
            subject='request1',
            text='text1',
            priority=PriorityChoices.HIGH,
            requester=self.user,
            status=StatusChoices.APPROVED,
        )
        self.declined_request = HelpRequest.objects.create(
            subject='request1',
            text='text1',
            priority=PriorityChoices.HIGH,
            requester=self.user,
            status=StatusChoices.DECLINED,
        )

    def test_start_processing_approved_request_unauthenticated(self):
        old_status = self.approve_request.status
        response = self.client.get(f'/requests/rest/{self.approve_request.pk}/start-processing/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.approve_request.refresh_from_db()
        self.assertEqual(self.approve_request.status, old_status)

    def test_start_processing_declined_request_unauthenticated(self):
        old_status = self.declined_request.status
        response = self.client.get(f'/requests/rest/{self.declined_request.pk}/start-processing/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.declined_request.refresh_from_db()
        self.assertEqual(self.declined_request.status, old_status)

    def test_start_processing_approved_request_by_admin(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(f'/requests/rest/{self.approve_request.pk}/start-processing/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.approve_request.refresh_from_db()
        self.assertEqual(self.approve_request.status, StatusChoices.IN_PROCESS)

    def test_start_processing_declined_request_by_admin(self):
        self.client.force_authenticate(user=self.superuser)
        old_status = self.declined_request.status
        response = self.client.get(f'/requests/rest/{self.declined_request.pk}/start-processing/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.declined_request.refresh_from_db()
        self.assertEqual(self.declined_request.status, old_status)

    def test_start_processing_approved_request_by_default_user(self):
        self.client.force_authenticate(user=self.user)
        old_status = self.approve_request.status
        response = self.client.get(f'/requests/rest/{self.approve_request.pk}/start-processing/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.approve_request.refresh_from_db()
        self.assertEqual(self.approve_request.status, old_status)

    def test_start_processing_declined_request_by_default_user(self):
        self.client.force_authenticate(user=self.user)
        old_status = self.declined_request.status
        response = self.client.get(f'/requests/rest/{self.declined_request.pk}/start-processing/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.declined_request.refresh_from_db()
        self.assertEqual(self.declined_request.status, old_status)


class RestCompleteProcessingTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = MyUser.objects.create_user(
            username='testUser',
            password='testPassword',
        )
        self.superuser = MyUser.objects.create_superuser(
            username='adminUser',
            password='adminPassword',
        )
        self.in_process_request = HelpRequest.objects.create(
            subject='request1',
            text='text1',
            priority=PriorityChoices.HIGH,
            requester=self.user,
            status=StatusChoices.IN_PROCESS,
        )
        self.other_request = HelpRequest.objects.create(
            subject='request1',
            text='text1',
            priority=PriorityChoices.HIGH,
            requester=self.user,
            status=StatusChoices.APPROVED,
        )

    def test_complete_processing_in_process_request_unauthenticated(self):
        old_status = self.in_process_request.status
        response = self.client.get(f'/requests/rest/{self.in_process_request.pk}/complete-processing/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.in_process_request.refresh_from_db()
        self.assertEqual(self.in_process_request.status, old_status)

    def test_complete_processing_other_request_unauthenticated(self):
        old_status = self.other_request.status
        response = self.client.get(f'/requests/rest/{self.other_request.pk}/complete-processing/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.other_request.refresh_from_db()
        self.assertEqual(self.other_request.status, old_status)

    def test_complete_processing_in_process_request_by_admin(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(f'/requests/rest/{self.in_process_request.pk}/complete-processing/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.in_process_request.refresh_from_db()
        self.assertEqual(self.in_process_request.status, StatusChoices.COMPLETED)

    def test_complete_processing_other_request_by_admin(self):
        self.client.force_authenticate(user=self.superuser)
        old_status = self.other_request.status
        response = self.client.get(f'/requests/rest/{self.other_request.pk}/complete-processing/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.other_request.refresh_from_db()
        self.assertEqual(self.other_request.status, old_status)

    def test_complete_processing_in_process_request_by_default_user(self):
        self.client.force_authenticate(user=self.user)
        old_status = self.in_process_request.status
        response = self.client.get(f'/requests/rest/{self.in_process_request.pk}/complete-processing/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.in_process_request.refresh_from_db()
        self.assertEqual(self.in_process_request.status, old_status)

    def test_complete_processing_other_request_by_default_user(self):
        self.client.force_authenticate(user=self.user)
        old_status = self.other_request.status
        response = self.client.get(f'/requests/rest/{self.other_request.pk}/complete-processing/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.other_request.refresh_from_db()
        self.assertEqual(self.other_request.status, old_status)


class RestResendReviewProcessingTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = MyUser.objects.create_user(
            username='testUser1',
            password='testPassword1',
        )
        self.user2 = MyUser.objects.create_user(
            username='testUser2',
            password='testPassword2',
        )
        self.superuser = MyUser.objects.create_superuser(
            username='adminUser',
            password='adminPassword',
        )
        self.other_request = HelpRequest.objects.create(
            subject='request1',
            text='text1',
            priority=PriorityChoices.HIGH,
            requester=self.user1,
            status=StatusChoices.APPROVED,
        )
        self.declined_request = HelpRequest.objects.create(
            subject='request1',
            text='text1',
            priority=PriorityChoices.HIGH,
            requester=self.user1,
            status=StatusChoices.DECLINED,
        )
        self.declined_request_with_reason = DeclinedRequest.objects.create(
            declined_request=self.declined_request,
            comment='Reason of declining',
        )

    def test_resend_review_declined_request_unauthenticated(self):
        old_status = self.declined_request.status
        response = self.client.get(f'/requests/rest/{self.declined_request.pk}/resend-review/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.declined_request.refresh_from_db()
        self.assertEqual(self.declined_request.status, old_status)

    def test_resend_review_other_request_unauthenticated(self):
        old_status = self.other_request.status
        response = self.client.get(f'/requests/rest/{self.other_request.pk}/resend-review/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.other_request.refresh_from_db()
        self.assertEqual(self.other_request.status, old_status)

    def test_resend_review_declined_request_by_admin(self):
        self.client.force_authenticate(user=self.superuser)
        old_status = self.declined_request.status
        response = self.client.get(f'/requests/rest/{self.declined_request.pk}/resend-review/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.declined_request.refresh_from_db()
        self.assertEqual(self.declined_request.status, old_status)

    def test_resend_review_other_request_by_admin(self):
        self.client.force_authenticate(user=self.superuser)
        old_status = self.other_request.status
        response = self.client.get(f'/requests/rest/{self.other_request.pk}/resend-review/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.other_request.refresh_from_db()
        self.assertEqual(self.other_request.status, old_status)

    def test_resend_review_declined_request_by_creator_user(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/requests/rest/{self.declined_request.pk}/resend-review/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.declined_request.refresh_from_db()
        self.assertEqual(self.declined_request.status, StatusChoices.FOR_RESTORATION)

    def test_resend_review_other_request_by_creator_user(self):
        self.client.force_authenticate(user=self.user1)
        old_status = self.other_request.status
        response = self.client.get(f'/requests/rest/{self.other_request.pk}/resend-review/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.other_request.refresh_from_db()
        self.assertEqual(self.other_request.status, old_status)

    def test_resend_review_declined_request_by_other_user(self):
        self.client.force_authenticate(user=self.user2)
        old_status = self.declined_request.status
        response = self.client.get(f'/requests/rest/{self.declined_request.pk}/resend-review/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.declined_request.refresh_from_db()
        self.assertEqual(self.declined_request.status, old_status)

    def test_resend_review_other_request_by_other_user(self):
        self.client.force_authenticate(user=self.user2)
        old_status = self.other_request.status
        response = self.client.get(f'/requests/rest/{self.other_request.pk}/resend-review/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.other_request.refresh_from_db()
        self.assertEqual(self.other_request.status, old_status)


class RestDecline(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = MyUser.objects.create_user(
            username='testUser',
            password='testPassword',
        )
        self.superuser = MyUser.objects.create_superuser(
            username='adminUser',
            password='adminPassword',
        )
        self.other_request = HelpRequest.objects.create(
            subject='request1',
            text='text1',
            priority=PriorityChoices.HIGH,
            requester=self.user,
            status=StatusChoices.APPROVED,
        )
        self.active_request = HelpRequest.objects.create(
            subject='request1',
            text='text1',
            priority=PriorityChoices.HIGH,
            requester=self.user,
            status=StatusChoices.ACTIVE,
        )
        self.data_for_decline = {
            'comment': 'Test reason of declining.',
            }

    def test_decline_active_request_unauthenticated(self):
        old_status = self.active_request.status
        response = self.client.post(f'/requests/rest/{self.active_request.pk}/decline/',
                                    data=self.data_for_decline,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.active_request.refresh_from_db()
        self.assertEqual(self.active_request.status, old_status)

    def test_decline_other_request_unauthenticated(self):
        old_status = self.other_request.status
        response = self.client.post(f'/requests/rest/{self.other_request.pk}/decline/',
                                    data=self.data_for_decline,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.other_request.refresh_from_db()
        self.assertEqual(self.other_request.status, old_status)

    def test_decline_active_request_by_admin(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.post(f'/requests/rest/{self.active_request.pk}/decline/',
                                    data=self.data_for_decline,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.active_request.refresh_from_db()
        self.assertEqual(self.active_request.status, StatusChoices.DECLINED)
        request_in_declined_table = DeclinedRequest.objects.last()
        self.assertEqual(request_in_declined_table.declined_request, self.active_request)

    def test_decline_other_request_by_admin(self):
        self.client.force_authenticate(user=self.superuser)
        old_status = self.other_request.status
        response = self.client.post(f'/requests/rest/{self.other_request.pk}/decline/',
                                    data=self.data_for_decline,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.other_request.refresh_from_db()
        self.assertEqual(self.other_request.status, old_status)

    def test_decline_active_request_by_default_user(self):
        self.client.force_authenticate(user=self.user)
        old_status = self.active_request.status
        response = self.client.post(f'/requests/rest/{self.active_request.pk}/decline/',
                                    data=self.data_for_decline,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.active_request.refresh_from_db()
        self.assertEqual(self.active_request.status, old_status)

    def test_decline_other_request_by_default_user(self):
        self.client.force_authenticate(user=self.user)
        old_status = self.other_request.status
        response = self.client.post(f'/requests/rest/{self.other_request.pk}/decline/',
                                    data=self.data_for_decline,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.other_request.refresh_from_db()
        self.assertEqual(self.other_request.status, old_status)

