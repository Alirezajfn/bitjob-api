import random
from datetime import datetime, timedelta

from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from config import settings


def _add_code_to_redis(email: str, postfix: str) -> int:
    random_code = _generate_random_number_with_size(settings.LENGTH_OF_TOKEN_CODE)
    is_set = cache.set(f'{email}{postfix}', str(random_code))
    cache.expire_at(f'{email}{postfix}', datetime.now() + timedelta(minutes=settings.CODE_EXPIRY_MINUTES))
    if not is_set:
        raise serializers.ValidationError(_('Error in sending code, please try again later'))

    return random_code


def _generate_random_number_with_size(number_of_digits: int) -> int:
    lower = 10 ** (number_of_digits - 1)
    upper = 10 ** number_of_digits - 1
    return random.randint(lower, upper)


def _add_verified_email_to_redis(email: str, postfix: str):
    cache.set(f'{email}{postfix}', 'True')
    cache.expire_at(
        f'{email}{postfix}',
        datetime.now() + timedelta(minutes=settings.EMAIL_STAY_VERIFIED_DURATION_MINUTEST)
    )


def _get_verified_email_value_from_cache(email: str, postfix: str) -> str:
    value = cache.get(f'{email}{postfix}')
    return value
