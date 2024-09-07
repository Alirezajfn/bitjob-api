from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('api/authenticate/', include('authentications.api.urls', namespace='authentications'),
         name='authentications'),
    path('api/users/', include('users.api.urls', namespace='users'), name='users'),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
