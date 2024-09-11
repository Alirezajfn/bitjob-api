from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from django_redis import get_redis_connection
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from config import settings


class SendForgetPasswordCodeTests(APITestCase):
    def setUp(self):
        self.user = baker.make(get_user_model())
        self.email_key = f'{self.user.email}{settings.FORGET_PASSWORD_EMAIL_REDIS_KEY_POSTFIX}'
        self.url = reverse('users:send_forget_password_code')

    def test_with_correct_email(self):
        data = {
            'email': self.user.email
        }

        response = self.client.post(self.url, data)
        forget_password_code = cache.get(self.email_key)
        self.assertIsNotNone(forget_password_code)
        self.assertEquals(response.status_code, status.HTTP_202_ACCEPTED)

    def test_with_not_existing_email(self):
        data = {
            'email': 'test@test.com'
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_without_providing_email(self):
        data = {
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_already_having_not_expired_code(self):
        code = 1234
        cache.set(self.email_key, str(code))
        cache.expire_at(self.email_key, datetime.now() + timedelta(
            minutes=settings.CODE_EXPIRY_MINUTES)
                        )

        data = {
            'email': self.user.email
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def tearDown(self) -> None:
        get_redis_connection().flushall()
