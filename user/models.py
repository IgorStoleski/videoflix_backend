from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model for Django that uses email instead of username for authentication.
    Attributes:
        email (models.EmailField): The email address of the user. Must be unique.
        username (models.CharField): The username of the user. This field is optional.
        first_name (models.CharField): The first name of the user. This field is optional.
        last_name (models.CharField): The last name of the user. This field is optional.
        is_staff (models.BooleanField): Designates whether the user can access the admin site.
        is_active (models.BooleanField): Designates whether this user should be treated as active. Unselect this instead of deleting accounts.
        date_joined (models.DateTimeField): The date the user account was created.
    Constants:
        USERNAME_FIELD (str): The name of the field that is used as the unique identifier.
        REQUIRED_FIELDS (list): A list of the field names that will be prompted for when creating a user via the createsuperuser management command.
    Methods:
        __str__(self): Returns a string representation of the user, which is their email address.
    Notes:
        Inherits from AbstractBaseUser for core authentication and PermissionsMixin for permission-related attributes.
    """
    email = models.EmailField(_("email address"), unique=True)
    username = models.CharField(max_length=30, blank=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email