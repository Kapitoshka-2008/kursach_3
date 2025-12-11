from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from users.managers import CustomUserManager


class CustomUser(AbstractUser):
    """Application user that authenticates by email."""

    username = models.CharField(
        max_length=150,
        blank=True,
        help_text='Optional display name shown in the interface.',
    )
    email = models.EmailField('email address', unique=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(r'^[0-9+() -]{4,20}$', 'Недопустимый формат номера')],
    )
    country = models.CharField(max_length=100, blank=True)
    is_email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    @property
    def full_display_name(self):
        return self.get_full_name() or self.email

