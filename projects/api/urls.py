from django.urls import path
from rest_framework.routers import DefaultRouter

from projects.api.views import ProjectViewSet, ProjectCategoryListView

app_name = 'projects'

router = DefaultRouter()
router.register('', ProjectViewSet, basename='project')

urlpatterns = [
    path('categories/', ProjectCategoryListView.as_view(), name='categories'),
]

urlpatterns += router.urls
