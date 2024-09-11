from rest_framework.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

app_name = 'authentications'

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
