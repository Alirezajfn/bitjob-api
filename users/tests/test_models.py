import hashlib

from django.contrib.auth import get_user_model
from django.test import TestCase


class UserManagerTests(TestCase):

    def test_create_user(self):
        user = get_user_model().objects.create_user(email="normal@user.com", password="foo")
        self.assertEqual(user.email, "normal@user.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_with_empty_email_fails(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email="", password="foo")

    def test_create_superuser(self):
        admin_user = get_user_model().objects.create_superuser(email="super@user.com", password="foo")
        self.assertEqual(admin_user.email, "super@user.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
