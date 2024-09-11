from django.core.cache import cache
from django.utils.translation import gettext_lazy as _

from mail.tasks import send_mail_in_background
from config import settings
from users.services.token_utils import _add_code_to_redis


def _send_forget_password_code(email: str):
    previous_code = cache.get(f'{email}{settings.FORGET_PASSWORD_EMAIL_REDIS_KEY_POSTFIX}')
    if previous_code:
        return

    code = _add_code_to_redis(email, postfix=settings.FORGET_PASSWORD_EMAIL_REDIS_KEY_POSTFIX)
    email_message = _(f'Forget Password Code: {code}')

    send_mail_in_background.apply_async(
        kwargs={
            'to_email': email,
            'message': email_message,
            'title': _('Romina Forget Password Code')
        }
    )
