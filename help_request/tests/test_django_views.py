from django.http import HttpResponseRedirect
from django.test import TestCase
from django.urls import reverse, reverse_lazy
from django.contrib.auth import get_user_model

from help_request.models import StatusChoices, HelpRequest, PriorityChoices

UserModel = get_user_model()


class MainViewTestCase(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            username="testUser",
            password="testPassword"
        )

    def test_main_view_authenticated(self):
        self.client.login(username=self.user.username, password="testPassword")
        response = self.client.get(reverse('main_view'))
        self.assertEqual(response.status_code, 200)

    def test_main_view_not_authenticated(self):
        response = self.client.get(reverse('main_view'))
        self.assertEqual(response.status_code, 302)  # Redirects to not_authenticated_view


class AboutViewTestCase(TestCase):
    def test_main_view_authenticated(self):
        response = self.client.get(reverse('about_view'))
        self.assertEqual(response.status_code, 200)


class RequestListViewTestCase(TestCase):
    def setUp(self):
        self.superuser = UserModel.objects.create_superuser(
            username="admin",
            password="adminpassword",
        )
        self.user = UserModel.objects.create_user(
            username="testUser",
            password="testPassword",
        )

    def test_authenticated_superuser(self):
        self.client.login(username=self.superuser.username, password="adminpassword")

        response = self.client.get(reverse('requests:request_list_view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'request_list_view.html')

    def test_authenticated_user(self):
        self.client.login(username=self.user.username, password="testPassword")

        response = self.client.get(reverse('requests:request_list_view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'request_list_view.html')

    def test_not_authenticated(self):
        response = self.client.get(reverse('requests:request_list_view'))
        self.assertEqual(response.status_code, 302)
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(response.url, reverse('user:not_authenticated_view'))


class RequestDetailViewTestCase(TestCase):
    def setUp(self):
        self.superuser = UserModel.objects.create_superuser(
            username="admin",
            password="adminpassword",
        )
        self.user = UserModel.objects.create_user(
            username="testUser",
            password="testPassword",
        )
        self.request = HelpRequest.objects.create(
            subject="Request 1",
            text="Description 1",
            requester=self.user,
            priority=PriorityChoices.MEDIUM,
            status=StatusChoices.IN_PROCESS
        )

    def test_superuser_view(self):
        self.client.login(username=self.superuser.username, password="adminpassword")
        response = self.client.get(reverse('requests:request_detail_view', kwargs={'pk': self.request.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'request_detail_view.html')

    def test_user_view(self):
        self.client.login(username=self.user.username, password="testPassword")
        response = self.client.get(reverse('requests:request_detail_view', kwargs={'pk': self.request.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'request_detail_view.html')

    def test_user_redirect(self):
        self.client.login(username=self.user.username, password="testPassword")
        self.request.status = StatusChoices.ACTIVE
        self.request.save()
        response = self.client.get(reverse('requests:request_detail_view', kwargs={'pk': self.request.pk}))
        self.assertEqual(response.status_code, 302)  # Redirects to 'main_view'
        self.assertRedirects(response, reverse('main_view'))


class CreateRequestViewTestCase(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            username="testUser",
            password="testPassword"
        )

    def test_create_request_authenticated_user(self):
        self.client.login(username=self.user.username, password="testPassword")

        response = self.client.get(reverse('requests:create_request_view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_request_view.html')

        form_data = {
            'subject': 'Test Request',
            'text': 'Description of the request',
            'priority': PriorityChoices.LOW
        }
        response = self.client.post(reverse('requests:create_request_view'), form_data)
        self.assertEqual(response.status_code, 302)  # Redirects to the detail view

    def test_create_request_not_authenticated_user(self):
        response = self.client.get(reverse('requests:create_request_view'))
        self.assertEqual(response.status_code, 302)  # Redirects to the login page, as not authenticated
        self.assertRedirects(response, reverse('user:login_user_view'))


class UpdateRequestViewTestCase(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            username="testUser",
            password="testPassword"
        )
        self.other_user = UserModel.objects.create_user(
            username="otherUser",
            password="otherPassword"
        )
        self.request = HelpRequest.objects.create(
            subject="Test Request",
            text="Description of the request",
            requester=self.user,
            priority=PriorityChoices.LOW
        )

    def test_authenticated_user_can_access(self):
        self.client.login(username=self.user.username, password="testPassword")

        response = self.client.get(reverse('requests:update_request_view', kwargs={'pk': self.request.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'update_request_view.html')

    def test_not_requester_redirected_to_list_view(self):
        self.client.login(username=self.other_user.username, password="otherPassword")

        response = self.client.get(reverse('requests:update_request_view', kwargs={'pk': self.request.pk}))
        self.assertEqual(response.status_code, 302)  # Redirects to the list view
        self.assertRedirects(response, reverse('requests:request_list_view'))

    def test_requester_can_update(self):
        self.client.login(username=self.user.username, password="testPassword")

        updated_data = {
            'subject': 'Updated Request',
            'text': 'Updated description',
            'priority': PriorityChoices.HIGH
        }
        response = self.client.post(reverse('requests:update_request_view', kwargs={'pk': self.request.pk}), updated_data)
        self.assertEqual(response.status_code, 302)


class DeleteRequestViewTestCase(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            username="testUser",
            password="testPassword"
        )
        self.other_user = UserModel.objects.create_user(
            username="otherUser",
            password="otherPassword"
        )
        self.request = HelpRequest.objects.create(
            subject="Test Request",
            text="Description of the request",
            requester=self.user,
            priority=PriorityChoices.LOW
        )

    def test_authenticated_requester_can_delete(self):
        self.client.login(username=self.user.username, password="testPassword")

        response = self.client.get(reverse('requests:delete_request_view', kwargs={'pk': self.request.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'delete_request_view.html')

    def test_not_requester_redirected_to_list_view(self):
        self.client.login(username=self.other_user.username, password="otherPassword")

        response = self.client.get(reverse('requests:delete_request_view', kwargs={'pk': self.request.pk}))
        self.assertEqual(response.status_code, 302)  # Redirects to the list view
        self.assertRedirects(response, reverse('requests:request_list_view'))

    def test_requester_can_delete(self):
        self.client.login(username=self.user.username, password="testPassword")

        response = self.client.post(reverse('requests:delete_request_view', kwargs={'pk': self.request.pk}))
        self.assertEqual(response.status_code, 302)  # Redirects to the success URL
        self.assertRedirects(response, reverse('main_view'))


class ToCheckRequestsViewTestCase(TestCase):
    def setUp(self):
        self.superuser = UserModel.objects.create_superuser(
            username="adminUser",
            password="adminPassword"
        )
        self.user = UserModel.objects.create_user(
            username="testUser",
            password="testPassword"
        )
        self.active_request = HelpRequest.objects.create(
            subject="Active Request",
            text="Description of the active request",
            requester=self.user,
            priority=PriorityChoices.LOW,
            status=StatusChoices.ACTIVE,
        )
        self.inactive_request = HelpRequest.objects.create(
            subject="Inactive Request",
            text="Description of the inactive request",
            requester=self.user,
            priority=PriorityChoices.LOW,
            status=StatusChoices.APPROVED,
        )

    def test_superuser_can_access(self):
        self.client.login(username=self.superuser.username, password="adminPassword")

        response = self.client.get(reverse('requests:request_to_check_view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'request_list_view.html')
        self.assertEqual(len(response.context['requests']), 1)  # Should show only active requests

    def test_non_superuser_redirected_to_main_view(self):
        self.client.login(username=self.user.username, password="testPassword")

        response = self.client.get(reverse('requests:request_to_check_view'))
        self.assertEqual(response.status_code, 302)  # Redirects to the main view
        self.assertRedirects(response, reverse('main_view'))


class ForRestorationRequestsViewTestCase(TestCase):
    def setUp(self):
        self.superuser = UserModel.objects.create_superuser(
            username="adminUser",
            password="adminPassword"
        )
        self.user = UserModel.objects.create_user(
            username="testUser",
            password="testPassword"
        )
        self.active_request = HelpRequest.objects.create(
            subject="Active Request",
            text="Description of the active request",
            requester=self.user,
            priority=PriorityChoices.LOW,
            status=StatusChoices.FOR_RESTORATION,
        )
        self.inactive_request = HelpRequest.objects.create(
            subject="Non-active Request",
            text="Description of the non-active request",
            requester=self.user,
            priority=PriorityChoices.LOW,
            status=StatusChoices.APPROVED,
        )

    def test_superuser_can_access(self):
        self.client.login(username=self.superuser.username, password="adminPassword")

        response = self.client.get(reverse('requests:requests_for_restoration_view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'request_list_view.html')
        self.assertEqual(len(response.context['requests']), 1)  # Should show only active requests

    def test_non_superuser_redirected_to_main_view(self):
        self.client.login(username=self.user.username, password="testPassword")

        response = self.client.get(reverse('requests:requests_for_restoration_view'))
        self.assertEqual(response.status_code, 302)  # Redirects to the main view
        self.assertRedirects(response, reverse('main_view'))


class ApproveRequestViewTestCase(TestCase):
    def setUp(self):
        self.superuser = UserModel.objects.create_superuser(
            username="adminUser",
            password="adminPassword"
        )
        self.user = UserModel.objects.create_user(
            username="testUser",
            password="testPassword"
        )
        self.active_request = HelpRequest.objects.create(
            subject="Active Request",
            text="Description of the active request",
            requester=self.user,
            priority=PriorityChoices.LOW,
            status=StatusChoices.ACTIVE,
        )
        self.for_restoration_request = HelpRequest.objects.create(
            subject="Restoration Request",
            text="Description of the restoration request",
            requester=self.user,
            priority=PriorityChoices.LOW,
            status=StatusChoices.FOR_RESTORATION,
        )
        self.inactive_request = HelpRequest.objects.create(
            subject="Non-active Request",
            text="Description of the Non-active request",
            requester=self.user,
            priority=PriorityChoices.LOW,
            status=StatusChoices.APPROVED,
        )

    def test_superuser_can_approve_active_request(self):
        self.client.login(username=self.superuser.username, password="adminPassword")

        response = self.client.get(reverse('requests:approve_request_view', kwargs={'pk': self.active_request.pk}))
        self.assertEqual(response.status_code, 302)  # Redirects to the detail view
        self.active_request.refresh_from_db()  # Refresh the object from the database
        self.assertEqual(self.active_request.status, StatusChoices.APPROVED)

    def test_superuser_can_approve_for_restoration_request(self):
        self.client.login(username=self.superuser.username, password="adminPassword")

        response = self.client.get(reverse('requests:approve_request_view', kwargs={'pk': self.for_restoration_request.pk}))
        self.assertEqual(response.status_code, 302)  # Redirects to the detail view
        self.for_restoration_request.refresh_from_db()  # Refresh the object from the database
        self.assertEqual(self.for_restoration_request.status, StatusChoices.APPROVED)

    def test_non_superuser_cannot_approve(self):
        self.client.login(username=self.user.username, password="testPassword")

        response = self.client.get(reverse('requests:approve_request_view', kwargs={'pk': self.active_request.pk}))
        self.assertEqual(response.status_code, 302)  # Redirects to the main view
        self.active_request.refresh_from_db()  # Refresh the object from the database
        self.assertNotEqual(self.active_request.status, StatusChoices.APPROVED)

    def test_non_active_request_cannot_be_approved(self):
        self.client.login(username=self.superuser.username, password="adminPassword")
        old_status = self.inactive_request.status
        response = self.client.get(reverse('requests:approve_request_view', kwargs={'pk': self.inactive_request.pk}))
        self.assertEqual(response.status_code, 302)  # Redirects to the main view
        self.inactive_request.refresh_from_db()  # Refresh the object from the database
        self.assertEqual(self.inactive_request.status, old_status)