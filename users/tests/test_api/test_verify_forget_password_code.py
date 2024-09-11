from django.contrib.auth import get_user_model
from django.urls import reverse
from django_redis import get_redis_connection
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from config import settings
from tools.users.services.token_utils import _add_code_to_redis, _get_verified_email_value_from_cache


class VerifyForgetPasswordTests(APITestCase):

    def setUp(self) -> None:
        self.user = baker.make(get_user_model())
        self.dummy_email = self.user.email
        self.forget_password_code = _add_code_to_redis(
            self.dummy_email,
            postfix=settings.FORGET_PASSWORD_EMAIL_REDIS_KEY_POSTFIX
        )
        self.url = reverse('users:verify_forget_code')

    def test_with_valid_email_and_valid_code(self):
        data = {
            'email': self.dummy_email,
            'forget_code': self.forget_password_code
        }

        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, status.HTTP_202_ACCEPTED)

        value = _get_verified_email_value_from_cache(
            self.dummy_email,
            postfix=settings.VERIFIED_FORGET_PASSWORD_EMAIL_REDIS_KEY_POSTFIX
        )
        self.assertEquals(bool(value), True)

    def test_with_mismatching_forget_password_code(self):
        data = {
            'email': self.dummy_email,
            'forget_code': 123456
        }

        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_none_forget_password_code(self):
        data = {
            'email': self.dummy_email,
            'forget_code': 'None'
        }

        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_null_forget_password_code(self):
        data = {
            'email': self.dummy_email,
            'forget_code': 'null'
        }

        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_invalid_email(self):
        data = {
            'email': 'invalid_email',
            'forget_code': self.forget_password_code
        }

        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_valid_email_and_valid_stringy_code(self):
        data = {
            'email': self.dummy_email,
            'forget_code': str(self.forget_password_code)
        }

        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, status.HTTP_202_ACCEPTED)

        value = _get_verified_email_value_from_cache(
            self.dummy_email,
            postfix=settings.VERIFIED_FORGET_PASSWORD_EMAIL_REDIS_KEY_POSTFIX
        )
        self.assertEquals(bool(value), True)

    def tearDown(self) -> None:
        get_redis_connection().flushall()
