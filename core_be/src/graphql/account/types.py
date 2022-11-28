from constance import config
from django.contrib.auth import get_user_model
import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from datetime import datetime, timedelta
from django.db.models import F, Q

from ..core.types import Upload
from ..core.connection import CountableConnection, CountableDjangoObjectType
from .enums import UserTypeEnum, CarTypeEnum
from ...booking.models import Booking as BookingModel
from ..booking.types import Booking, CoordinateInput
from ..booking.enums import StatusTypeEnum
from ..booking.resolvers import resolve_distance

class OffenLocation(graphene.ObjectType):
    location = graphene.String()
    booking_count = graphene.Int()

class User(DjangoObjectType):
    offen_location = graphene.List(OffenLocation)
    available_booking_for_driver = graphene.List(Booking)

    class Meta:
        description = "Represents user data."
        interfaces = (relay.Node,)
        model = get_user_model()
        only_fields = [
            "id",
            "full_name",
            "phone_number",
            "date_of_birth",
            "citizen_identification",
            "car_type",
            "car_brand",
            "license_plate",
            "car_color",
            "address",
            "is_available",
            "email",
            "user_type",
            "is_active",
            "current_position"
        ]

    @staticmethod
    def resolve_offen_location(root, info):
        current_user = info.context.user
        offen_locations = []
        bookings = current_user.customer_booking.all()
        for booking in bookings:
            check = False
            for offen_location in offen_locations:
                if booking.destination == offen_location.location:
                    offen_location.booking_count += 1
                    check = True
            if check == False:
                offen_locations.append(OffenLocation(location=booking.destination, booking_count=1))
        def get_booking_count(e):
            return e.booking_count
        offen_locations.sort(reverse=True, key=get_booking_count)
        return offen_locations
    
    @staticmethod
    def resolve_available_booking_for_driver(root, info):
        current_user = info.context.user
        if current_user.user_type != UserTypeEnum.DRIVER.value:
            return None
        if current_user.is_active == False:
            return None
        if current_user.driver_booked.filter(Q(status = StatusTypeEnum.WAIT_FOR_DRIVER.value), Q(status = StatusTypeEnum.ON_GOING.value)).count() > 0:
            return None
        
        result = []
        driver_position = current_user.current_position[0]
        driver_lat = driver_position.get("lat")
        driver_lng = driver_position.get("lng")
        available_booking = BookingModel.objects.filter(status=StatusTypeEnum.WAIT_FOR_CONFIRMED.value)
        for booking in available_booking:
            booking_position = booking.departure_position[0]
            booking_lat = booking_position.get("lat")
            booking_lng = booking_position.get("lng")
            if resolve_distance(booking_lat,booking_lng,driver_lat,driver_lng) <= booking.allow_driver_distance:
                if booking.car_type == CarTypeEnum.ANY.value:
                    result.append(booking)
                elif booking.car_type == current_user.car_type:
                    result.append(booking)
        return result




class PositionInput(graphene.InputObjectType):
    current_position = graphene.List(graphene.NonNull(
        CoordinateInput), required=True)


class AccountUpdateInput(graphene.InputObjectType):
    id = graphene.UUID(required=True)
    full_name = graphene.String(description="Full name.")
    phone_number = graphene.String()
    date_of_birth = graphene.Date()
    citizen_identification = graphene.String()
    user_type = graphene.Field(UserTypeEnum)
    car_type = graphene.Field(CarTypeEnum)
    car_brand = graphene.String()
    license_plate = graphene.String()
    car_color = graphene.String()
    avatar = Upload()
    address = graphene.String()
    email = graphene.String(description="The email address of the user.")
    is_staff = graphene.Boolean()

class Configuration(graphene.ObjectType):
    key = graphene.String()
    value = graphene.Int()