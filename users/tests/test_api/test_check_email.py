from django.contrib.auth import get_user_model
from django.urls import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from config import settings


class CheckEmailTests(APITestCase):

    def setUp(self):
        self.dummy_email = 'test@test.com'
        self.url = reverse('users:check_email')

    def test_with_not_registered_email(self):
        data = {
            'email': self.dummy_email
        }

        response = self.client.post(self.url, data=data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        expected_data = {
            "exists": False,
            "registration_code_timeout": settings.CODE_EXPIRY_MINUTES
        }
        self.assertEquals(response.data, expected_data)

    def test_with_registered_email(self):
        baker.make(get_user_model(), email=self.dummy_email)

        data = {
            'email': self.dummy_email
        }

        response = self.client.post(self.url, data=data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        expected_data = {
            "exists": True,
            "registration_code_timeout": settings.CODE_EXPIRY_MINUTES
        }
        self.assertEquals(response.data, expected_data)
