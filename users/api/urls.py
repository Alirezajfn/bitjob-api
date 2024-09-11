from rest_framework.routers import DefaultRouter
from rest_framework.urls import path

from users.api.views import (send_registration_code_view, check_email_view,
                             verify_registration_code_view, UserViewSet, verify_forget_code_view,
                             reset_password_view,
                             send_forget_password_code_view, user_profile_view
                             )

app_name = 'users'

router = DefaultRouter()
router.register('', UserViewSet, basename='user')

urlpatterns = [

    path('check-email/', check_email_view, name='check_email'),
    path('verify-registration-code/', verify_registration_code_view, name='verify_registration_code'),
    path('send-registration-code/', send_registration_code_view, name='send_registration_code'),

    path('send-forget-passwoed-code/', send_forget_password_code_view, name='send_forget_password_code'),
    path('verify-forget-password-code/', verify_forget_code_view, name='verify_forget_code'),
    path('reset-password/', reset_password_view, name='reset_password'),

    path('profile/', user_profile_view, name='profile'),

]

urlpatterns += router.urls
