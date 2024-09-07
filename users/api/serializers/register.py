from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from authentications.services.jwt import get_jwt_tokens_for_user
from config import settings
from users.api.validators import is_registered_before, is_email_verified
from users.services.registration import _send_registration_code
from users.services.token_utils import _add_verified_email_to_redis


class CheckEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class SendRegistrationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs['email']

        is_registered_before(email)

        email_key = f'{email}{settings.REGISTRATION_EMAIL_REDIS_KEY_POSTFIX}'
        value = cache.get(email_key)
        if value:
            raise ValidationError(
                _('Registration code has been send already, please wait until it expires'))

        return attrs

    def create(self, validated_data):
        email = validated_data['email']
        _send_registration_code(email)
        return validated_data


class VerifyRegistrationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    registration_code = serializers.IntegerField(required=True, allow_null=False)

    def validate(self, attrs):
        email = attrs['email']
        registration_code = attrs['registration_code']

        sent_registration_code = cache.get(f'{email}{settings.REGISTRATION_EMAIL_REDIS_KEY_POSTFIX}')
        is_registered_before(email)

        if not sent_registration_code:
            raise ValidationError(_('You have no recent registration code or the sent code has been expired '))

        if not int(registration_code) == int(sent_registration_code):
            raise ValidationError(_('Not Such Registration Code Found'))

        _add_verified_email_to_redis(email, postfix=settings.VERIFIED_REGISTERED_EMAIL_REDIS_KEY_POSTFIX)

        return attrs


class RegisterUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=128, required=True)
    password = serializers.CharField(max_length=128, write_only=True, required=True)
    confirm_password = serializers.CharField(max_length=128, write_only=True, required=True)

    class Meta:
        model = get_user_model()
        fields = [
            'username',
            'email',

            'password',
            'confirm_password'
        ]

    def validate(self, attrs):
        username = attrs['username']
        email = attrs['email']
        password = attrs['password']
        confirm_password = attrs['confirm_password']

        if get_user_model().objects.filter(username=username).exists():
            raise ValidationError(_('Username already exists'))

        if not password == confirm_password:
            raise ValidationError(_('Passwords mismatch'))

        validate_password(password)
        is_registered_before(email)
        is_email_verified(email, postfix=settings.VERIFIED_REGISTERED_EMAIL_REDIS_KEY_POSTFIX)

        cache.delete(f'{email}{settings.REGISTRATION_EMAIL_REDIS_KEY_POSTFIX}')
        cache.delete(f'{email}{settings.VERIFIED_REGISTERED_EMAIL_REDIS_KEY_POSTFIX}')

        return attrs

    def create(self, validated_data):
        instance = get_user_model().objects.create(email=validated_data['email'])
        instance.set_password(validated_data['password'])
        instance.save()
        return instance

    def to_representation(self, instance):
        data = super(RegisterUserSerializer, self).to_representation(instance)
        tokens = get_jwt_tokens_for_user(instance)
        data.update(tokens)

        return data
