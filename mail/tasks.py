from celery import shared_task

from mail.services.mail_manager import MailSenderManager


@shared_task
def send_mail_in_background(to_email: str, message: str, title: str, **kwargs):
    result = MailSenderManager().send(to_email, message, title, **kwargs)
    return result
