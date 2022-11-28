from datetime import timedelta
from django.db import models

from ..core.models import ModelWithMetadata, UUIDModel
from ..core.fields import DynamicStorageFileField
from ..account.models import User
from . import *
from ..account import CarType
from phonenumber_field.modelfields import PhoneNumber, PhoneNumberField
from ..account.validators import validate_possible_number


class PossiblePhoneNumberField(PhoneNumberField):
    """Less strict field for phone numbers written to database."""

    default_validators = [validate_possible_number]

class Booking(ModelWithMetadata):
    class Meta:
        db_table = 'booking'
    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="customer_booking", blank=True, null=True)
    is_registered_user = models.BooleanField(default=True)
    phone_number = PossiblePhoneNumberField(blank=True, default="", db_index=True)
    driver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="driver_booked", blank=True, null=True)
    car_type = models.CharField(max_length=25, choices=CarType.CHOICES)
    booking_time = models.DateTimeField(auto_now_add=True)
    finish_time = models.DateTimeField(blank=True, null=True)
    booking_type = models.CharField(
        max_length=20, choices=BookingType.CHOICES, default=BookingType.ON_APP)
    departure = models.CharField(max_length=512)
    departure_position = models.JSONField(default=list, blank=True, null=True)
    destination = models.CharField(max_length=512)
    destination_position = models.JSONField(default=list, blank=True, null=True)
    status = models.CharField(
        max_length=30, choices=StatusType.CHOICES, default=StatusType.WAIT_FOR_CONFIRMED)
    total_distance = models.FloatField()
    total_fee = models.FloatField()
    cancel_count = models.PositiveIntegerField(default=0)
    gps_data = models.JSONField(default=list, blank=True, null=True)
    allow_driver_distance = models.PositiveIntegerField(default=1000)
    

class DriverConfirmBooking(ModelWithMetadata):
    class Meta:
        db_table = 'driver_confirm_booking'
    driver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="driver_confirm_booking")
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="booking_driver_confirm")
    distance = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


    
    