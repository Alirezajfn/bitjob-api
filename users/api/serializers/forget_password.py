from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from config import settings
from users.api.validators import is_email_verified
from users.services.forget_password import _send_forget_password_code
from users.services.token_utils import _add_verified_email_to_redis


class SendForgotPasswordCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs['email']

        exists = get_user_model().objects.filter(email=email).exists()
        if not exists:
            raise ValidationError(_('Email does not exist'))

        email_key = f'{email}{settings.FORGET_PASSWORD_EMAIL_REDIS_KEY_POSTFIX}'
        value = cache.get(email_key)
        if value:
            raise ValidationError(
                _('Forget password code has been send already, please wait until it expires'))

        return attrs

    def create(self, validated_data):
        email = validated_data['email']
        _send_forget_password_code(email)
        return validated_data


class VerifyForgetCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    forget_code = serializers.IntegerField(required=True, allow_null=False)

    def validate(self, attrs):
        email = attrs['email']
        email_key = f'{email}{settings.FORGET_PASSWORD_EMAIL_REDIS_KEY_POSTFIX}'
        forget_code = attrs['forget_code']

        sent_forget_code = cache.get(email_key)

        exists = get_user_model().objects.filter(email=email).exists()
        if not exists:
            raise ValidationError(_('Email does not exists'))

        if not sent_forget_code:
            raise ValidationError(_('You have no recent forget code or the sent code has been expired '))

        if not int(forget_code) == int(sent_forget_code):
            raise ValidationError(_('Not Such Forget Code Found'))

        _add_verified_email_to_redis(email, postfix=settings.VERIFIED_FORGET_PASSWORD_EMAIL_REDIS_KEY_POSTFIX)

        return attrs


class UserResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(max_length=128, write_only=True, required=True)
    confirm_password = serializers.CharField(max_length=128, write_only=True, required=True)

    def validate(self, attrs):
        email = attrs['email']
        is_email_verified(email, postfix=settings.VERIFIED_FORGET_PASSWORD_EMAIL_REDIS_KEY_POSTFIX)

        if not attrs.get('password') == attrs.get('confirm_password'):
            raise ValidationError(_('Passwords are not equal'))

        validate_password(attrs.get('password'))
        cache.delete(f'{email}{settings.FORGET_PASSWORD_EMAIL_REDIS_KEY_POSTFIX}')
        cache.delete(f'{email}{settings.VERIFIED_FORGET_PASSWORD_EMAIL_REDIS_KEY_POSTFIX}')

        return attrs

    def save(self, **kwargs):
        email = self.validated_data['email']
        password = self.validated_data['password']
        user = get_user_model().objects.get(email=email)
        user.set_password(password)
        user.save()
        return user
