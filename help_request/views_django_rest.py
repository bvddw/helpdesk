from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from comments.serializers import CommentSerializer
from .models import HelpRequest, StatusChoices, DeclinedRequest
from .permissions import RequesterOnly
from .serializers import RequestSerializer, DeclinedRequestSerializer


class RequestViewSet(ModelViewSet):
    queryset = HelpRequest.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [RequesterOnly]

    def get_queryset(self):
        queryset = HelpRequest.objects.all()
        if not self.request.user.is_superuser:
            queryset = HelpRequest.objects.filter(requester=self.request.user)

        priority_type = self.request.query_params.get('priority_type')
        status_type = self.request.query_params.get('status_type')

        if priority_type:
            queryset = queryset.filter(priority=priority_type).distinct()
        if status_type:
            queryset = queryset.filter(status=status_type).distinct()

        return queryset


class RestAllAdminsRequests(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = RequestSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        return HelpRequest.objects.filter(requester=self.request.user)


class RestForRestoration(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = RequestSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        return HelpRequest.objects.filter(status=StatusChoices.FOR_RESTORATION)


class RestActive(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = RequestSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        return HelpRequest.objects.filter(status=StatusChoices.ACTIVE)



class CommentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        help_request = get_object_or_404(HelpRequest, pk=self.kwargs.get('pk'))
        if not request.user.is_superuser and request.user != help_request.requester:
            return Response({"error": "Cannot check this help request."}, status=status.HTTP_403_FORBIDDEN)

        queryset = self.get_queryset()
        serializer = CommentSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        help_request = get_object_or_404(HelpRequest, pk=self.kwargs.get('pk'))
        if self.request.user == help_request.requester or self.request.user.is_superuser:
            return help_request.comments.all()

    def post(self, request, pk):
        help_request = get_object_or_404(HelpRequest, pk=pk)

        if help_request.status == StatusChoices.IN_PROCESS:
            serializer = CommentSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save(author=request.user, help_request=help_request)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Cannot add comments to this request."}, status=status.HTTP_403_FORBIDDEN)


class RestApprove(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        cur_request = get_object_or_404(HelpRequest, id=pk)
        if request.user == cur_request.requester:
            return Response({"error": "You cannot change status on yours request."}, status=status.HTTP_403_FORBIDDEN)

        if cur_request.status in [StatusChoices.ACTIVE, StatusChoices.FOR_RESTORATION]:
            cur_request.status = StatusChoices.APPROVED
            cur_request.save()

            serializer = RequestSerializer(instance=cur_request)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "This request cannot be approved."}, status=status.HTTP_400_BAD_REQUEST)


class RestDecline(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        cur_request = get_object_or_404(HelpRequest, id=pk)
        if request.user == cur_request.requester:
            return Response({"error": "You cannot change status on yours request."}, status=status.HTTP_403_FORBIDDEN)
        serializer = RequestSerializer(instance=cur_request)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        cur_request = get_object_or_404(HelpRequest, pk=pk)
        if request.user == cur_request.requester:
            return Response({"error": "You cannot change status on yours request."}, status=status.HTTP_403_FORBIDDEN)

        if cur_request.status == StatusChoices.ACTIVE:
            serializer = DeclinedRequestSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save(declined_request=cur_request)
                cur_request.status = StatusChoices.DECLINED
                cur_request.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Cannot decline this request."}, status=status.HTTP_400_BAD_REQUEST)


class RestStartProcessing(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        cur_request = get_object_or_404(HelpRequest, id=pk)
        if request.user == cur_request.requester:
            return Response({"error": "You cannot change status on yours request."}, status=status.HTTP_403_FORBIDDEN)

        if cur_request.status == StatusChoices.APPROVED:
            cur_request.status = StatusChoices.IN_PROCESS
            cur_request.save()

            serializer = RequestSerializer(instance=cur_request)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Cannot initiate processing for this request."},
                        status=status.HTTP_400_BAD_REQUEST)


class RestCompleteProcessing(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        cur_request = get_object_or_404(HelpRequest, id=pk)
        if request.user == cur_request.requester:
            return Response({"error": "You cannot change status on yours request."}, status=status.HTTP_403_FORBIDDEN)

        if cur_request.status == StatusChoices.IN_PROCESS:
            cur_request.status = StatusChoices.COMPLETED
            cur_request.save()

            serializer = RequestSerializer(instance=cur_request)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Cannot finish processing for this request."}, status=status.HTTP_400_BAD_REQUEST)


class RestResendReviewProcessing(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        cur_request = get_object_or_404(HelpRequest, id=pk)
        if request.user != cur_request.requester:
            return Response({"error": "You cannot resend review, because you are not a reviewer."},
                            status=status.HTTP_403_FORBIDDEN)
        if cur_request.status == StatusChoices.DECLINED:
            declined_req = get_object_or_404(DeclinedRequest, declined_request=cur_request)
            declined_req.delete()
            cur_request.status = StatusChoices.FOR_RESTORATION
            cur_request.save()

            serializer = RequestSerializer(instance=cur_request)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Cannot send this request for restoration."}, status=status.HTTP_400_BAD_REQUEST)

