from django.contrib.auth import get_user_model
from django.urls import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from config import settings
from tools.users.services.token_utils import _add_code_to_redis, _get_verified_email_value_from_cache


class VerifyRegistrationTests(APITestCase):

    def setUp(self) -> None:
        self.dummy_email = 'test@test.com'
        self.registration_code = _add_code_to_redis(
            self.dummy_email,
            postfix=settings.REGISTRATION_EMAIL_REDIS_KEY_POSTFIX
        )
        self.url = reverse('users:verify_registration_code')

    def test_with_existing_email(self):
        baker.make(get_user_model(), email=self.dummy_email)

        data = {
            'email': self.dummy_email,
            'registration_code': self.registration_code
        }

        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_expired_registration_code(self):
        data = {
            'email': 'test2@test2.com',
            'registration_code': 123456
        }

        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_mismatching_registration_code(self):
        data = {
            'email': self.dummy_email,
            'registration_code': 123456
        }

        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_none_registration_code(self):
        data = {
            'email': self.dummy_email,
            'registration_code': 'None'
        }

        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_null_registration_code(self):
        data = {
            'email': self.dummy_email,
            'registration_code': 'null'
        }

        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_valid_email_and_valid_code(self):
        data = {
            'email': self.dummy_email,
            'registration_code': self.registration_code
        }

        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, status.HTTP_202_ACCEPTED)

        value = _get_verified_email_value_from_cache(
            self.dummy_email,
            postfix=settings.VERIFIED_REGISTERED_EMAIL_REDIS_KEY_POSTFIX
        )
        self.assertEquals(bool(value), True)

    def test_with_valid_email_and_valid_stringy_code(self):
        data = {
            'email': self.dummy_email,
            'registration_code': str(self.registration_code)
        }

        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, status.HTTP_202_ACCEPTED)

        value = _get_verified_email_value_from_cache(
            self.dummy_email,
            postfix=settings.VERIFIED_REGISTERED_EMAIL_REDIS_KEY_POSTFIX
        )
        self.assertEquals(bool(value), True)
