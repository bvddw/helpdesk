from django.test import TestCase
from django.contrib.auth.models import User
from help_request.forms import HelpRequestCreateForm, HelpRequestUpdateForm, DeclinedRequestForm
from help_request.models import HelpRequest, PriorityChoices


class HelpRequestCreateFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testUser',
            password='testPassword')

    def test_create_help_request(self):
        form_data = {
            'subject': 'Test Subject',
            'text': 'Test Text',
            'priority': PriorityChoices.HIGH,
        }
        form = HelpRequestCreateForm(data=form_data)
        self.assertTrue(form.is_valid())
        help_request = form.create_help_request(requester=self.user)
        self.assertEqual(help_request.subject, 'Test Subject')
        self.assertEqual(help_request.text, 'Test Text')
        self.assertEqual(help_request.priority, PriorityChoices.HIGH)
        self.assertEqual(help_request.requester, self.user)

    def test_form_validation(self):
        # Test form validation for invalid data
        invalid_form_data = {
            'subject': '',
            'text': 'Test Text',
            'priority': 'InvalidPriority',
        }
        form = HelpRequestCreateForm(data=invalid_form_data)
        self.assertFalse(form.is_valid())

    def test_empty_form(self):
        empty_form_data = {}
        form = HelpRequestCreateForm(data=empty_form_data)
        self.assertFalse(form.is_valid())


class HelpRequestUpdateFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testUser',
            password='testPassword',
        )
        self.request = HelpRequest.objects.create(
            subject='Test Subject',
            text='Test Text',
            priority=PriorityChoices.HIGH,
            requester=self.user,
        )

    def test_update_help_request(self):
        form_data = {
            'text': 'Updated Text',
            'priority': PriorityChoices.MEDIUM,
        }
        form = HelpRequestUpdateForm(data=form_data, instance=self.request)
        self.assertTrue(form.is_valid())
        updated_request = form.update_help_request(request_to_update=self.request)
        self.assertEqual(updated_request.text, 'Updated Text')
        self.assertEqual(updated_request.priority, PriorityChoices.MEDIUM)

    def test_form_validation(self):
        invalid_form_data = {
            'text': '',
            'priority': 'InvalidPriority',
        }
        form = HelpRequestUpdateForm(data=invalid_form_data, instance=self.request)
        self.assertFalse(form.is_valid())


class DeclinedRequestFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testUser',
            password='testPassword',
        )
        self.request = HelpRequest.objects.create(
            subject='Test Subject',
            text='Test Text',
            priority=PriorityChoices.HIGH,
            requester=self.user,
        )

    def test_create_declined_request(self):
        form_data = {
            'comment': 'Test Comment',
        }
        form = DeclinedRequestForm(data=form_data)
        self.assertTrue(form.is_valid())
        declined_request = form.create_declined_request(request_to_decline=self.request)
        self.assertEqual(declined_request.comment, 'Test Comment')
        self.assertEqual(declined_request.declined_request, self.request)

    def test_form_validation(self):
        invalid_form_data = {
            'comment': '',
        }
        form = DeclinedRequestForm(data=invalid_form_data)
        self.assertFalse(form.is_valid())
