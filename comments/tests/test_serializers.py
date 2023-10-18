from django.test import TestCase
from comments.models import MyUser, HelpRequest, Comment
from comments.serializers import CommentSerializer


class CommentSerializerTest(TestCase):
    def setUp(self):
        self.user = MyUser.objects.create(
            username='testUser',
            password='testPassword'
        )

        self.request = HelpRequest.objects.create(
            subject='Test Request',
            text='Test Text',
            priority='High',
            requester=self.user,
        )

        self.comment = Comment.objects.create(
            message='Test Comment',
            author=self.user,
            help_request=self.request,
        )

    def test_comment_serializer(self):
        serializer = CommentSerializer(instance=self.comment)
        expected_data = {
            'message': 'Test Comment',
            'author': 'testUser',
        }
        self.assertEqual(serializer.data, expected_data)
