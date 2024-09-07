from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from authentications.services.jwt import get_jwt_tokens_for_user


class RegisterUserSerializer(serializers.ModelSerializer):
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
        username = attrs.get('username', None)
        email = attrs['email']
        password = attrs['password']
        confirm_password = attrs['confirm_password']

        if not password == confirm_password:
            raise ValidationError(_('Passwords mismatch'))

        validate_password(password)

        if username:
            exists = get_user_model().objects.filter(username=username).exists()
            if exists:
                ValidationError(_('Chosen Username Exists'))

        if email:
            exists = get_user_model().objects.filter(email=email).exists()
            if exists:
                ValidationError(_('Chosen Email Exists'))

        return attrs

    def create(self, validated_data):
        instance = get_user_model().objects.create(
            email=validated_data['email'],
            username=validated_data['username']
        )
        instance.set_password(validated_data['password'])
        instance.save()
        return instance

    def to_representation(self, instance):
        """
        Add tokens to the response
        """
        data = super(RegisterUserSerializer, self).to_representation(instance)
        tokens = get_jwt_tokens_for_user(instance)
        data.update(tokens)

        return data
