from . import views
from django.urls import path

urlpatterns = [
    path('login/', views.LoginUserView.as_view(), name='login_user_view'),
    path('register/', views.RegisterUserView.as_view(), name='register_user_view'),
    path('logout/', views.LogoutUserView.as_view(), name='logout_user_view'),
    path('not-authenticated/', views.NotAuthenticatedView.as_view(), name='not_authenticated_view'),
]