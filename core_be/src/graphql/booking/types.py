import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from notifications.models import Notification as NotificationModel
from ..core.types import Upload
from ...booking.models import Booking as BookingModel, DriverConfirmBooking as DriverConfirmBookingModel
from .enums import BookingTypeEnum, StatusTypeEnum

from ...account.models import User as UserModel
from ..core.connection import CountableDjangoObjectType
from .enums import *
from ..account.enums import CarTypeEnum

class CoordinateInput(graphene.InputObjectType):
    lat = graphene.NonNull(graphene.Float)
    lng = graphene.NonNull(graphene.Float)


class DriverConfirmBookingType(CountableDjangoObjectType):
    class Meta:
        description = "Represents driver confirm booking data."
        model = DriverConfirmBookingModel
        interfaces = [relay.Node]


class Booking(CountableDjangoObjectType):
    driver_confirm_booking = graphene.List(DriverConfirmBookingType)
    is_confirmed_by_driver = graphene.Boolean()

    class Meta:
        description = "Represents booking data."
        model = BookingModel
        interfaces = [relay.Node]

    @staticmethod
    def resolve_driver_confirm_booking(root, info):
        driver_confirm_booking = root.booking_driver_confirm.all()
        return driver_confirm_booking
    @staticmethod
    def resolve_is_confirmed_by_driver(root, info):
        current_user = info.context.user
        driver_confirm_booking = DriverConfirmBookingModel.objects.filter(driver=current_user, booking=root).first()
        if driver_confirm_booking is not None:
            return True
        else:
            return False

class BookingCreateInput(graphene.InputObjectType):
    customer_id = graphene.UUID()
    phone_number = graphene.String()
    car_type = graphene.Field(CarTypeEnum)
    departure = graphene.String()
    departure_position = graphene.List(graphene.NonNull(
        CoordinateInput), required=True)
    destination = graphene.String()
    destination_position = graphene.List(graphene.NonNull(
        CoordinateInput), required=True)
    total_distance = graphene.Float()

class Notification(CountableDjangoObjectType):
    class Meta:
        description = "Represents Notification data."
        model = NotificationModel