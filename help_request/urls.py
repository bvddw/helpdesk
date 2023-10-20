from rest_framework import routers
from django.urls import path, include
from . import views_django, views_django_rest

router = routers.SimpleRouter()
router.register("rest", views_django_rest.RequestViewSet)

urlpatterns = [
    # django rest paths
    path('rest/for-restoration/', views_django_rest.RestForRestoration.as_view(),
         name='rest_for_restoration'),
    path('rest/active/', views_django_rest.RestActive.as_view(),
         name='rest_active'),
    path('rest/all-admins-requests/', views_django_rest.RestAllAdminsRequests.as_view(),
         name='rest_all_requests'),
    path('', include(router.urls)),
    path('rest/<int:pk>/resend-review/', views_django_rest.RestResendReviewProcessing.as_view(),
         name='rest_resend_review'),
    path('rest/<int:pk>/approve/', views_django_rest.RestApprove.as_view(),
         name='rest_approve'),
    path('rest/<int:pk>/decline/', views_django_rest.RestDecline.as_view(),
         name='rest_decline'),
    path('rest/<int:pk>/start-processing/', views_django_rest.RestStartProcessing.as_view(),
         name='rest_init_processing'),
    path('rest/<int:pk>/complete-processing/', views_django_rest.RestCompleteProcessing.as_view(),
         name='rest_complete_processing'),
    path('rest/<int:pk>/comments/', views_django_rest.CommentsView.as_view(),
         name='create_comment'),

    # default django paths
    path('', views_django.UsersRequestListView.as_view(),
         name='users_request_list_view'),
    path('create-request/', views_django.CreateRequestView.as_view(),
         name='create_request_view'),
    path('update-request/<int:pk>/', views_django.UpdateRequestView.as_view(),
         name='update_request_view'),
    path('delete-request/<int:pk>/', views_django.DeleteRequestView.as_view(),
         name='delete_request_view'),
    path('request-detail/<int:pk>/', views_django.RequestDetailView.as_view(),
         name='request_detail_view'),
    path('all-requests/', views_django.AllRequestListView.as_view(),
         name='all_request_view'),
    path('requests-to-check/', views_django.ToCheckRequestsView.as_view(),
         name='request_to_check_view'),
    path('requests-for-restoration/', views_django.ForRestorationRequestsView.as_view(),
         name='requests_for_restoration_view'),
    path('request-for-restoration/<int:pk>/', views_django.AskForReviewRequestView.as_view(),
         name='ask_for_restoration'),
    path('approve-request/<int:pk>/', views_django.ApproveRequestView.as_view(),
         name='approve_request_view'),
    path('decline-request/<int:pk>/', views_django.DeclineRequestView.as_view(),
         name='decline_request_view'),
    path('start-processing-request/<int:pk>/', views_django.StartProcessingRequestView.as_view(),
         name='start_processing_request_view'),
    path('complete-processing-request/<int:pk>/', views_django.CompleteProcessingRequestView.as_view(),
         name='complete_processing_request_view'),
]
