from email.policy import default
from functools import partial
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import (
    URLValidator,
    validate_email,
)
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import JSONField  # type: ignore
from django.utils import timezone
from django.utils.crypto import get_random_string
from phonenumber_field.modelfields import PhoneNumber, PhoneNumberField
from datetime import datetime, timedelta
from constance import config
from ..core.models import ModelWithMetadata, UUIDModel
from ..core.utils.json_serializer import CustomJsonEncoder
from .validators import validate_possible_number
from . import *

class PossiblePhoneNumberField(PhoneNumberField):
    """Less strict field for phone numbers written to database."""

    default_validators = [validate_possible_number]


class UserManager(BaseUserManager):
    def create_user(
        self, email, password=None, is_staff=False, is_active=True, **extra_fields
    ):
        """Create a user instance with the given email and password."""
        email = UserManager.normalize_email(email)
        # Google OAuth2 backend send unnecessary username field
        extra_fields.pop("username", None)

        user = self.model(
            email=self.normalize_email(email),
            is_active=is_active,
            is_staff=is_staff,
            **extra_fields
        )
        token = get_random_string(length=64)
        user.id_token = token
        user.expiration_time = datetime.now(timezone.utc) + timedelta(days=90)
        if password:
            user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        return self.create_user(
            email=email, password=password, is_staff=True, is_superuser=True, **extra_fields
        )

    # def staff(self):
    #     return self.get_queryset().filter(is_staff=True)


class User(UUIDModel, PermissionsMixin, ModelWithMetadata, AbstractBaseUser):
    full_name = models.CharField(max_length=256, blank=True)
    phone_number = PossiblePhoneNumberField(blank=True, default="", db_index=True)
    date_of_birth = models.DateField(blank=True, null=True)
    citizen_identification = models.CharField(max_length=12, null=True, blank=True)
    user_type = models.CharField(max_length=25, choices=UserType.CHOICES, default=UserType.CUSTOMER)
    car_type = models.CharField(max_length=25, choices=CarType.CHOICES, null=True, blank=True)
    car_brand = models.CharField(max_length=256, null=True, blank=True)
    license_plate = models.CharField(max_length=256, null=True, blank=True)
    car_color = models.CharField(max_length=256, null=True, blank=True)
    avatar = models.ImageField(upload_to="user-avatars", blank=True, null=True, max_length=512)
    address = models.CharField(max_length=512, blank=True, null=True)
    current_position = models.JSONField(default=list, blank=True, null=True)
    is_available = models.BooleanField(default=False)
    
    id_token = models.CharField(max_length=1024, unique=True, blank=True, null=True)
    expiration_time = models.DateTimeField(null=True, blank=True)

    fcm_token = models.CharField(max_length=1024, unique=True, blank=True, null=True)
    fcm_token_updated_at = models.DateTimeField(null=True, blank=True)
    
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    jwt_token_key = models.CharField(
        max_length=12, default=partial(get_random_string, length=12)
    )

    USERNAME_FIELD = "email"

    objects = UserManager()


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._effective_permissions = None

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        try:
            validate_email(self.email)
        except ValidationError:
            pass
        return super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )
