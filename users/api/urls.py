from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.api.views import UserViewSet

app_name = 'users'

router = DefaultRouter()
router.register('', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls), name='users'),
]
