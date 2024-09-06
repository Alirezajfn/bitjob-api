from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('api/authenticate/', include('authentications.api.urls', namespace='authentications'),
         name='authentications'),
]
