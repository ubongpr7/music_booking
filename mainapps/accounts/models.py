from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        user = self.create_user(email, password, **extra_fields)
        return user


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.

    This model uses the email address as the unique identifier for authentication
    and includes additional fields for phone number, verification status, and musician status.

    Attributes:
        email (EmailField): Unique email address of the user. Acts as the username.
        phone (CharField): Optional phone number for the user.
        is_verified (BooleanField): Indicates whether the user's email has been verified.
        is_musician (BooleanField): Indicates whether the user is a musician.
    """
    email = models.EmailField(blank=False, null=True, unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_musician = models.BooleanField(default=False)

    # Use email as the USERNAME_FIELD for authentication.
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        """
        Save the user instance ensuring the username is set to the email.

        """
        self.username = self.email
        super().save(*args, **kwargs)
