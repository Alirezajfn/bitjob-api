from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from drf_spectacular.utils import extend_schema_view, extend_schema

from rest_framework import mixins
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from users.api.filters import SelfFilterBacked
from users.api.serializers.register import RegisterUserSerializer
from users.api.serializers.user import UserRetrieveUpdateSerializer


@extend_schema_view(
    retrieve=extend_schema(description='The retrieve action is used to retrieve a user by username'),
    update=extend_schema(description='The update action is used to update the information of each user by '
                                     'himself with all the fields'),
    partial_update=extend_schema(description='The partial update action is used to update the information'
                                             ' of each user by himself with some of the fields'),
    create=extend_schema(description='The create action is used to register a new user with all the fields'),
)
class UserViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = get_user_model().objects.all()
    filter_backends = [SelfFilterBacked]

    lookup_field = 'username'
    lookup_url_kwarg = 'username'

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return RegisterUserSerializer

        return UserRetrieveUpdateSerializer

    # TODO: add change password view