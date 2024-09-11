from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from django_redis import get_redis_connection
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from config import settings


class SendRegistrationCodeTests(APITestCase):

    def setUp(self) -> None:
        self.dummy_email = 'test@test.com'
        self.email_key = f'{self.dummy_email}{settings.REGISTRATION_EMAIL_REDIS_KEY_POSTFIX}'
        self.url = reverse('users:send_registration_code')

    def test_with_correct_email(self):
        data = {
            'email': self.dummy_email
        }

        response = self.client.post(self.url, data)
        registration_code = cache.get(self.email_key)
        self.assertIsNotNone(registration_code)
        self.assertEquals(response.status_code, status.HTTP_202_ACCEPTED)

    def test_with_existing_email_fails(self):
        baker.make(get_user_model(), email=self.dummy_email)

        data = {
            'email': self.dummy_email
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
            'email': self.dummy_email
        }

        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def tearDown(self) -> None:
        get_redis_connection().flushall()
