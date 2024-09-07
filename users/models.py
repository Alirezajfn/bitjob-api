from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.db import models

from users.managers import CustomUserManager


class User(AbstractUser):
    objects = CustomUserManager()
    email = models.EmailField(unique=True)
    REQUIRED_FIELDS = ['email']

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to. A group represents a collection of users who have'
                    ' certain permissions.'),
        related_name="user_set_custom",
        related_query_name="user_custom",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="user_perm_set_custom",
        related_query_name="user_permission_custom",
    )

    class Meta:
        indexes = [
            models.Index(fields=['email', ]),
        ]
