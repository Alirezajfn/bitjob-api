from celery import shared_task

from mail.services.mail_manager import MailSenderManager


@shared_task(name='sending_email_in_background')
def send_mail_in_background(to_email: str, message: str, title: str, **kwargs):
    status = MailSenderManager().send(to_email, message, title, **kwargs)
    return status
