from django.test import TestCase
from comments.models import MyUser, HelpRequest, Comment
from comments.forms import CommentForm


class CommentFormTest(TestCase):
    def setUp(self):
        self.user = MyUser.objects.create(
            username='testUser',
            password='testPassword',
        )

        self.request = HelpRequest.objects.create(
            subject='Test Request',
            text='Test Text',
            priority='High',
            requester=self.user,
        )

    def test_comment_form(self):
        form_data = {'comment': 'Test Comment Text'}
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())
        form.create_comment(author=self.user, help_request=self.request)
        comment = Comment.objects.get(message='Test Comment Text')
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.help_request, self.request)
