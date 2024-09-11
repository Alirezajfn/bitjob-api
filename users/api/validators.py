from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError


def is_registered_before(email: str):
    exists = get_user_model().objects.filter(email=email).exists()
    if exists:
        raise ValidationError(_('Email already exists'))


def is_email_verified(email: str, postfix: str):
    value = cache.get(f'{email}{postfix}')
    if not value:
        raise ValidationError(_('Email has not been verified'))
