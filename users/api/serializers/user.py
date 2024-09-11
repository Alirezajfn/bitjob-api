from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as  _
from rest_framework import serializers
from rest_framework.serializers import ValidationError


class UserRetrieveUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            'username',
            'email',

            'mobile',
            'first_name',
            'last_name',
            'last_login',
            'avatar'

        ]

        extra_kwargs = {
            'email': {'read_only': True},
            'last_login': {'read_only': True},
        }

    def validate(self, attrs):
        username = attrs.get('username', None)
        if username:
            exists = get_user_model().objects.filter(username=username).exists()
            if exists:
                ValidationError(_('Chosen Username Exists'))

        return attrs


class UserChangePasswordSerializer(serializers.Serializer):
    previous_password = serializers.CharField(max_length=128, write_only=True, required=True)
    password = serializers.CharField(max_length=128, write_only=True, required=True)
    confirm_password = serializers.CharField(max_length=128, write_only=True, required=True)

    def validate(self, attrs):

        if self.instance.check_password(attrs['previous_password']) is False:
            raise ValidationError(_('Previous password does not match'))

        if not attrs.get('password') == attrs.get('confirm_password'):
            raise ValidationError(_('Passwords are not equal'))

        validate_password(attrs['password'], self.instance)

        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            'username',
            'email',

            'mobile',
            'first_name',
            'last_name',
            'last_login',
            'avatar',

        ]
        read_only_fields = fields
