from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import status, mixins
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from users.services.registration import _check_email
from users.api.filters import SelfFilterBacked
from users.api.serializers import (SendRegistrationCodeSerializer,
                                   RegisterUserSerializer, CheckEmailSerializer,
                                   VerifyRegistrationCodeSerializer,
                                   UserRetrieveUpdateSerializer, UserChangePasswordSerializer,
                                   VerifyForgetCodeSerializer,
                                   UserResetPasswordSerializer, SendForgotPasswordCodeSerializer,
                                   UserProfileSerializer
                                   )


@extend_schema(request=CheckEmailSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def check_email_view(request, **kwargs):
    serializer = CheckEmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    result = _check_email(serializer.validated_data['email'])
    return Response(data=result, status=status.HTTP_200_OK)


@extend_schema(request=SendRegistrationCodeSerializer, responses={202: {}})
@api_view(['POST'])
@permission_classes([AllowAny])
def send_registration_code_view(request, **kwargs):
    serializer = SendRegistrationCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(status=status.HTTP_202_ACCEPTED)


@extend_schema(request=VerifyRegistrationCodeSerializer, responses={202: {}})
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_registration_code_view(request, **kwargs):
    serializer = VerifyRegistrationCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response(status=status.HTTP_202_ACCEPTED)


@extend_schema(request=SendForgotPasswordCodeSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def send_forget_password_code_view(request, **kwargs):
    serializer = SendForgotPasswordCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(status=status.HTTP_202_ACCEPTED)


@extend_schema(request=VerifyForgetCodeSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_forget_code_view(request, **kwargs):
    serializer = VerifyForgetCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response(status=status.HTTP_202_ACCEPTED)


@extend_schema(request=UserResetPasswordSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_view(request, **kwargs):
    serializer = UserResetPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(status=status.HTTP_202_ACCEPTED)


class UserViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
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

    @extend_schema(request=UserChangePasswordSerializer, responses={200: {}})
    @action(detail=True, methods=['patch'], url_path='change-password', url_name='change_password')
    def change_password(self, request, **kwargs):
        instance = self.get_object()
        serializer = UserChangePasswordSerializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        raise ValidationError(_('You can not delete your account'))


@extend_schema(responses=UserProfileSerializer)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile_view(request, **kwargs):
    data = UserProfileSerializer(instance=request.user).data
    return Response(data=data, status=status.HTTP_200_OK)
