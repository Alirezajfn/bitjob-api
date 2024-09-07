import logging

from config import settings
from django.core import mail as django_mail
from django.core.mail import get_connection
from django.core.mail.backends.smtp import EmailBackend


logger = logging.getLogger(__name__)


class MailSenderManager:
    """
    This class is responsible for sending emails using django core mail
    """
    def __init__(self, connection: EmailBackend = None):
        self.connection = connection
        if self.connection is None:
            self.connection = get_connection(settings.EMAIL_BACKEND)

    def send(self, to_email: list, message: str, title: str, **kwargs):
        """
        This method is responsible for sending emails using django core mail
        :param to_email: list of emails
        :param message: message of email
        :param title: title of email
        :param kwargs: other arguments
        :return: number of successful emails
        """
        try:
            successes = django_mail.send_mail(subject=title,
                                              message=message,
                                              from_email=settings.env('EMAIL_HOST_USER'),
                                              recipient_list=to_email,
                                              connection=self.connection,
                                              **kwargs
                                              )
            return successes

        except Exception as e:
            logger.error(e)
