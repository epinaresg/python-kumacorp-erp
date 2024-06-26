from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from authentication.views import EmailTokenObtainPairView, RegisterView, UserDetailView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='user-registration'),
    path('token/', EmailTokenObtainPairView.as_view(), name='token-obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    path('user/', UserDetailView.as_view(), name='user_detail'),
]
