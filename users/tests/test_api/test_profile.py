from django.contrib.auth import get_user_model
from django.urls import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase


class UserProfileTests(APITestCase):

    def setUp(self) -> None:
        self.user = baker.make(get_user_model())

        self.client.force_login(self.user)
        self.url = reverse('users:profile')

    def test_get_profile_successfully(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_profile_without_being_login(self):
        self.client.logout()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_data_matches_as_expected(self):
        response = self.client.get(self.url)
        expected_data = {
            'username': self.user.username,
            'email': self.user.email,
            'mobile': self.user.mobile,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
        }
        actual_data = response.data

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(expected_data, actual_data)
