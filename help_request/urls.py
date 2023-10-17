from rest_framework import routers
from django.urls import path, include
from . import views

router = routers.SimpleRouter()
router.register("rest", views.RequestViewSet)

urlpatterns = [
    # django rest paths
    path('rest/for-restoration/', views.RestForRestoration.as_view(), name='rest_for_restoration'),
    path('', include(router.urls)),
    path('rest/<int:pk>/resend-review/', views.ResendReviewProcessing.as_view(), name='rest_resend_review'),
    path('rest/<int:pk>/approve/', views.RestApprove.as_view(), name='rest_approve'),
    path('rest/<int:pk>/decline/', views.RestDecline.as_view(), name='rest_decline'),
    path('rest/<int:pk>/start-processing/', views.RestStartProcessing.as_view(), name='rest_init_processing'),
    path('rest/<int:pk>/complete-processing/', views.RestCompleteProcessing.as_view(), name='rest_complete_processing'),
    path('rest/<int:pk>/comments/', views.CommentsView.as_view(), name='create_comment'),

    # default django paths
    path('', views.RequestListView.as_view(), name='request_list_view'),
    path('create-request/', views.CreateRequestView.as_view(), name='create_request_view'),
    path('update-request/<int:pk>', views.UpdateRequestView.as_view(), name='update_request_view'),
    path('delete-request/<int:pk>', views.DeleteRequestView.as_view(), name='delete_request_view'),
    path('request-detail/<int:pk>', views.RequestDetailView.as_view(), name='request_detail_view'),
    path('requests-to-check/', views.ToCheckRequestsView.as_view(), name='request_to_check_view'),
    path('requests-for-restoration/', views.ForRestorationRequestsView.as_view(), name='requests_for_restoration_view'),
    path('request-for-restoration/<int:pk>', views.AskForReviewRequestView.as_view(), name='ask_for_restoration'),
    path('approve-request/<int:pk>', views.ApproveRequestView.as_view(), name='approve_request_view'),
    path('decline-request/<int:pk>', views.DeclineRequestView.as_view(), name='decline_request_view'),
    path('start-processing-request/<int:pk>', views.StartProcessingRequestView.as_view(), name='start_processing_request_view'),
    path('complete-processing-request/<int:pk>', views.CompleteProcessingRequestView.as_view(), name='complete_processing_request_view'),
]