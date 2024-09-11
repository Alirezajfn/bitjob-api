from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from django_redis import get_redis_connection
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from config import settings
from tools.users.services.token_utils import _add_verified_email_to_redis


class UserCreateTests(APITestCase):

    def setUp(self) -> None:
        self.dummy_verified_email = 'verified@test.com'
        _add_verified_email_to_redis(
            self.dummy_verified_email,
            postfix=settings.VERIFIED_REGISTERED_EMAIL_REDIS_KEY_POSTFIX
        )
        self.url = reverse('users:user-list')
        self.correct_password = 'Strong_password1'

    def test_with_not_verified_email(self):
        data = {
            'email': 'not_verified@test.com',
            'password': self.correct_password,
            'confirm_password': self.correct_password
        }

        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(get_user_model().objects.count(), 0)

    def test_with_mismatching_password_and_confirm_password(self):
        data = {
            'email': self.dummy_verified_email,
            'password': 'password',
            'confirm_password': 'not_matiching'
        }

        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(get_user_model().objects.count(), 0)

    def test_create_user_with_verified_email(self):
        data = {
            'email': self.dummy_verified_email,
            'password': self.correct_password,
            'confirm_password': self.correct_password
        }

        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(get_user_model().objects.count(), 1)
        self.assertIsNotNone(get_user_model().objects.filter(email=self.dummy_verified_email))

    def test_create_user_initializes_username_and_salt(self):
        data = {
            'email': self.dummy_verified_email,
            'password': self.correct_password,
            'confirm_password': self.correct_password
        }

        self.client.post(self.url, data)
        user = get_user_model().objects.filter(email=self.dummy_verified_email).first()
        self.assertIsNotNone(user.username)
        self.assertIsNotNone(user.salt)

    def test_with_weak_password(self):
        data = {
            'email': self.dummy_verified_email,
            'password': 'Password',
            'confirm_password': 'Password'
        }

        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(get_user_model().objects.count(), 0)


class UserRetrieveUpdateDeleteTests(APITestCase):

    def setUp(self):
        self.user = baker.make(get_user_model())
        self.client.force_login(self.user)

        baker.make(get_user_model())
        baker.make(get_user_model())
        baker.make(get_user_model())

    def test_retrieve_someone_else_data_gets_is_not_possible(self):
        another_user = baker.make(get_user_model())

        url = reverse('users:user-detail', args=[another_user.id])

        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_someone_else_data_gets_is_not_possible(self):
        another_user = baker.make(get_user_model())

        url = reverse('users:user-detail', args=[another_user.id])
        data = {
            'first_name': 'new_first_name'
        }

        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
        another_user.refresh_from_db()
        self.assertNotEqual(another_user.first_name, data['first_name'])

    def test_retrieve_user_with_not_being_authenticated_is_not_possible(self):
        self.client.logout()

        url = reverse('users:user-list')

        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user_with_not_being_authenticated_is_not_possible(self):
        self.client.logout()

        url = reverse('users:user-detail', args=[self.user.id])
        data = {
            'first_name': 'new_first_name'
        }

        response = self.client.patch(url)
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.first_name, data['first_name'])

    def test_delete_user_not_allowed(self):
        url = reverse('users:user-detail', args=[self.user.id])

        response = self.client.delete(url)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(get_user_model().objects.filter(id=self.user.id))

    def test_update_user_data_successfully(self):
        url = reverse('users:user-detail', args=[self.user.username])
        data = {
            'first_name': 'new_first_name_new'
        }

        response = self.client.patch(url, data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, data['first_name'])

    def test_update_username_with_existing_username(self):
        existing_user = baker.make(get_user_model(), username='test')

        url = reverse('users:user-detail', args=[self.user.username])
        data = {
            'username': existing_user.username
        }

        response = self.client.patch(url, data)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.username, existing_user.username)

    def test_update_username_successfully(self):
        url = reverse('users:user-detail', args=[self.user.username])
        data = {
            'username': 'new_username'
        }

        response = self.client.patch(url, data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, data['username'])


class UserChangePasswordActionTests(APITestCase):

    def setUp(self):
        self.user = baker.make(get_user_model())
        self.initial_password = 'Strong_password1'
        self.user.set_password(self.initial_password)
        self.user.save()

        self.client.force_login(self.user)

    def test_change_password_successfully(self):
        url = reverse('users:user-change_password', args=[self.user.username])
        data = {
            'previous_password': self.initial_password,
            'password': 'Strong_password2',
            'confirm_password': 'Strong_password2',

        }

        response = self.client.patch(url, data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(data['password']))

    def test_change_others_password_is_not_possible(self):
        another_user = baker.make(get_user_model())
        user_pass = 'Strong_password1'
        another_user.set_password(user_pass)
        another_user.save()

        url = reverse('users:user-change_password', args=[another_user.id])
        data = {
            'previous_password': 'blah',
            'password': 'blah2',
            'confirm_password': 'blah2',

        }

        response = self.client.patch(url, data)
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
        another_user.refresh_from_db()
        self.assertTrue(another_user.check_password(user_pass))

    def test_change_password_without_being_authenticated_is_not_allowed(self):
        self.client.logout()
        url = reverse('users:user-change_password', args=[self.user.id])
        data = {
            'previous_password': self.initial_password,
            'password': 'Strong_password2',
            'confirm_password': 'Strong_password2',

        }

        response = self.client.patch(url, data)
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.initial_password))

    def test_changing_password_with_mismatching_new_passwords_not_possible(self):
        url = reverse('users:user-change_password', args=[self.user.username])
        data = {
            'previous_password': self.initial_password,
            'password': 'Strong_password2',
            'confirm_password': 'password',

        }

        response = self.client.patch(url, data)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.initial_password))

    def test_change_password_without_matching_previous_password(self):
        url = reverse('users:user-change_password', args=[self.user.username])
        data = {
            'previous_password': 'not previouse',
            'password': 'Strong_password2',
            'confirm_password': 'Strong_password2',

        }

        response = self.client.patch(url, data)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.initial_password))

    def test_change_password_without_special_characters(self):
        url = reverse('users:user-change_password', args=[self.user.username])
        data = {
            'previous_password': self.initial_password,
            'password': 'Strongpassword2',
            'confirm_password': 'Strongpassword2',

        }

        response = self.client.patch(url, data)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.initial_password))

    def test_change_password_with_less_than_8_characters(self):
        url = reverse('users:user-change_password', args=[self.user.username])
        data = {
            'previous_password': self.initial_password,
            'password': 'Strong2',
            'confirm_password': 'Strong2',

        }

        response = self.client.patch(url, data)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.initial_password))

    def test_change_password_with_no_numbers(self):
        url = reverse('users:user-change_password', args=[self.user.username])
        data = {
            'previous_password': self.initial_password,
            'password': 'Strong_password',
            'confirm_password': 'Strong_password',

        }

        response = self.client.patch(url, data)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.initial_password))

    def test_change_password_with_no_uppercase_letters(self):
        url = reverse('users:user-change_password', args=[self.user.username])
        data = {
            'previous_password': self.initial_password,
            'password': 'strong_password2',
            'confirm_password': 'strong_password2',

        }

        response = self.client.patch(url, data)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.initial_password))

    def test_change_password_with_no_lowercase_letters(self):
        url = reverse('users:user-change_password', args=[self.user.username])
        data = {
            'previous_password': self.initial_password,
            'password': 'STRONG_PASSWORD2',
            'confirm_password': 'STRONG_PASSWORD2',

        }

        response = self.client.patch(url, data)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.initial_password))


class UserResetPasswordTests(APITestCase):

    def setUp(self) -> None:
        self.user = baker.make(get_user_model())
        self.user.set_password('1234')
        self.user.save()
        self.verified_email_key = f'{self.user.email}{settings.VERIFIED_FORGET_PASSWORD_EMAIL_REDIS_KEY_POSTFIX}'

    def test_reset_password_successfully(self):
        url = reverse('users:reset_password')
        data = {
            'email': self.user.email,
            'password': 'Strong_password1',
            'confirm_password': 'Strong_password1'
        }

        cache.set(self.verified_email_key, True)

        response = self.client.post(url, data)
        self.assertEquals(response.status_code, status.HTTP_202_ACCEPTED)
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password('1234'))
        self.assertTrue(self.user.check_password('Strong_password1'))

    def test_reset_password_with_not_verified_email(self):
        url = reverse('users:reset_password')
        data = {
            'email': self.user.email,
            'password': 'Strong_password1',
            'confirm_password': 'Strong_password1'
        }

        response = self.client.post(url, data)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('1234'))
        self.assertFalse(self.user.check_password('Strong_password1'))

    def test_reset_password_with_not_existing_user(self):
        url = reverse('users:reset_password')
        data = {
            'email': 'test@test.com',
            'password': 'Strong_password1',
            'confirm_password': 'Strong_password1'
        }

        response = self.client.post(url, data)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_with_mismatching_passwords(self):
        url = reverse('users:reset_password')
        data = {
            'email': self.user.email,
            'password': 'Strong_password1',
            'confirm_password': 'Strong_password2'
        }

        cache.set(self.verified_email_key, True)

        response = self.client.post(url, data)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('1234'))
        self.assertFalse(self.user.check_password('Strong_password1'))
        self.assertFalse(self.user.check_password('Strong_password2'))

    def test_reset_password_after_time_expires(self):
        url = reverse('users:reset_password')
        data = {
            'email': self.user.email,
            'password': 'Strong_password1',
            'confirm_password': 'Strong_password1'
        }

        cache.set(self.verified_email_key, True)
        cache.expire(self.verified_email_key, 0)

        response = self.client.post(url, data)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('1234'))
        self.assertFalse(self.user.check_password('Strong_password1'))

    def test_reset_password_with_not_valid_password(self):
        url = reverse('users:reset_password')
        data = {
            'email': self.user.email,
            'password': 'weak',
            'confirm_password': 'weak'
        }

        cache.set(self.verified_email_key, True)
        response = self.client.post(url, data)

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('1234'))
        self.assertFalse(self.user.check_password('weak_password'))

    def tearDown(self) -> None:
        get_redis_connection().flushall()
