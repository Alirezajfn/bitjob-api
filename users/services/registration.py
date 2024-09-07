from dataclasses import dataclass, asdict

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _

from utils.background_tasks.tasks import send_mail_in_background
from config import settings
from users.services.token_utils import _add_code_to_redis


@dataclass(init=True, repr=True)
class UserEmailStatus:
    exists: bool = True
    registration_code_timeout: int = settings.CODE_EXPIRY_MINUTES

    dict = asdict


def _check_email(email: str) -> dict:
    exists = get_user_model().objects.filter(email=email).exists()
    if not exists:
        _send_registration_code(email)

    email_status = UserEmailStatus(exists)
    return email_status.dict()


def _send_registration_code(email: str):
    previous_code = cache.get(f'{email}{settings.REGISTRATION_EMAIL_REDIS_KEY_POSTFIX}')
    if previous_code:
        return

    code = _add_code_to_redis(email, postfix=settings.REGISTRATION_EMAIL_REDIS_KEY_POSTFIX)
    email_message = _(f'Registration Code : {code}')

    send_mail_in_background.apply_async(
        kwargs={
            'to_email': email,
            'message': email_message,
            'title': _('Bitjob Registration Code')
        }
    )
