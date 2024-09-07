from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class UserRetrieveUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
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
