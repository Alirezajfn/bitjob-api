from rest_framework.routers import DefaultRouter

from projects.api.views import ProjectViewSet

app_name = 'projects'

router = DefaultRouter()
router.register('', ProjectViewSet, basename='project')

urlpatterns = [

]
