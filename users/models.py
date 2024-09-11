from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.managers import CustomUserManager


def user_directory_path(instance, filename):
    return f'users_avatars/{instance.username}_avatar'


class User(AbstractUser):
    objects = CustomUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    username = models.CharField(max_length=150, unique=True)

    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=11, unique=True, null=True)
    avatar = models.ImageField(upload_to=user_directory_path, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['username', ]),
            models.Index(fields=['email', ]),
        ]

    @property
    def full_name(self):
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def delete(self, using=None, keep_parents=False):
        raise models.ProtectedError(_("delete is not allowed in RUser model."), self)
