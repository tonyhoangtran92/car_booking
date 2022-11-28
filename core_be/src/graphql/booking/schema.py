from xmlrpc.client import boolean
import graphene
from django.db.models import F, Q
from graphql_jwt.decorators import login_required, superuser_required
from django.core.exceptions import ValidationError
from notifications.signals import notify

from ...booking.models import Booking as BookingModel
from .mutations import BookingCreate, BookingChangeStatus, BookingCancel, DriverFinishBooking, \
            DriverConfirmBooking, AdminChooseDriverForBooking, NotificationMarkRead, \
            BookingUpdateAllowDriverDistance
from .types import Booking as BookingType, Notification as NotificationType
from .filters import BookingFilterInput
from .enums import BookingTypeEnum, StatusTypeEnum
from ..core.fields import FilterInputConnectionField

from django.db.models import Sum, F, Window, Case, Value, When
from django.db.models.functions import DenseRank

from ...account.models import User as UserModel
from ..account.types import User as UserType, OffenLocation
from ..account.enums import UserTypeEnum
from .resolvers import resolve_distance

class BookingQueries(graphene.ObjectType):
    booking_read = graphene.Field(
        BookingType,
        id=graphene.ID(),
        description="Return booking details info."
    )

    def resolve_booking_read(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return BookingModel.objects.get(pk=id)

    bookings_wait_for_confirmed = graphene.Field(
        graphene.List(BookingType), description="Return list of booking that wait for confirmed."
    )

    @login_required
    def resolve_bookings_wait_for_confirmed(self, info):
        return BookingModel.objects.filter(status=StatusTypeEnum.WAIT_FOR_CONFIRMED.value)

    bookings_wait_for_driver = graphene.Field(
        graphene.List(BookingType), description="Return list of booking that wait for driver."
    )

    @login_required
    def resolve_bookings_wait_for_driver(self, info):
        return BookingModel.objects.filter(status=StatusTypeEnum.WAIT_FOR_DRIVER.value)
    
    bookings_completed = graphene.Field(
        graphene.List(BookingType), description="Return list of booking that completed."
    )

    @login_required
    def resolve_bookings_completed(self, info):
        return BookingModel.objects.filter(status=StatusTypeEnum.COMPLETED.value)
    
    bookings_on_going = graphene.Field(
        graphene.List(BookingType), description="Return list of booking that on going."
    )

    @login_required
    def resolve_bookings_on_going(self, info):
        return BookingModel.objects.filter(status=StatusTypeEnum.ON_GOING.value)

    registered_user_recent_booking = graphene.Field(
        graphene.List(BookingType), 
        user_id = graphene.UUID(required=True),
        description="Return list of booking that user completed."
    )

    @login_required
    def resolve_registered_user_recent_booking(self, info, **kwargs):
        user_id = kwargs.get('user_id')
        return BookingModel.objects.filter(status=StatusTypeEnum.COMPLETED.value, customer_id = user_id)
    
    unregistered_user_recent_booking = graphene.Field(
        graphene.List(BookingType), 
        phone_number = graphene.String(required=True),
        description="Return list of booking that user completed."
    )

    @login_required
    def resolve_unregistered_user_recent_booking(self, info, **kwargs):
        phone_number = kwargs.get('phone_number')
        return BookingModel.objects.filter(status=StatusTypeEnum.COMPLETED.value, phone_number = phone_number)
    
    # bookings = FilterInputConnectionField(
    #     BookingType,
    #     filter=BookingFilterInput(description="Filter options for booking"),
    # )

    # @superuser_required
    # def resolve_bookings(self, info, query=None, sort_by=None, **kwargs):
    #     return BookingModel.objects.all()

    my_bookings = graphene.Field(
        graphene.List(BookingType), description="Return list of booking that current user book."
    )

    @login_required
    def resolve_my_bookings(self, info):
        current_user = info.context.user
        return BookingModel.objects.filter(customer=current_user)
    
    my_rides = graphene.Field(
        graphene.List(BookingType), description="Return list of ride that current user is driver."
    )

    @login_required
    def resolve_my_rides(self, info):
        current_user = info.context.user
        return BookingModel.objects.filter(driver=current_user)

    offen_location_user = graphene.Field(
        graphene.List(OffenLocation), 
        phone_number = graphene.String(),
        description="Return list of offen location by user - based on phone number."
    )

    @login_required
    def resolve_offen_location_user(self, info, **kwargs):
        phone_number = kwargs.get('phone_number')
        offen_locations = []
        bookings = BookingModel.objects.filter(phone_number=phone_number)
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

    my_current_booking = graphene.Field(
        BookingType, 
        description="Return current booking of user."
    )

    @login_required
    def resolve_my_current_booking(self, info):
        current_user = info.context.user
        return current_user.customer_booking.filter(~Q(status=StatusTypeEnum.COMPLETED.value), ~Q(status=StatusTypeEnum.CANCELLED.value)).last()

    my_current_ride = graphene.Field(
        BookingType, 
        description="Return current booking of a driver."
    )

    @login_required
    def resolve_my_current_ride(self, info):
        current_user = info.context.user
        return current_user.driver_booked.filter(Q(status=StatusTypeEnum.WAIT_FOR_DRIVER.value) | Q(status=StatusTypeEnum.ON_GOING.value)).last()

    #query 5 arounding driver within 1km and 5km after 30seconds
    booking_driver_arround_one_km = graphene.Field(
        graphene.List(UserType), 
        booking_id = graphene.ID(required=True),
        description="Return list driver arround 1km with the customer booking"
    )

    def resolve_booking_driver_arround_one_km(self, info, **kwargs):
        booking_id = kwargs.get('booking_id')
        booking=BookingModel.objects.get(pk=booking_id)
        booking_position = booking.departure_position[0]
        booking_lat = booking_position.get("lat")
        booking_lng = booking_position.get("lng")
        result = []
        available_driver = UserModel.objects.filter(Q(user_type=UserTypeEnum.DRIVER.value), Q(is_active=True), ~Q(driver_booked__status=StatusTypeEnum.WAIT_FOR_DRIVER.value),  ~Q(driver_booked__status=StatusTypeEnum.ON_GOING.value))
        if available_driver is not None:
            for driver in available_driver:
                driver_position = driver.current_position[0]
                driver_lat = driver_position.get("lat")
                driver_lng = driver_position.get("lng")
                if resolve_distance(booking_lat,booking_lng,driver_lat,driver_lng) <=1000:
                    result.append(driver)
        for driver in result:
            notify.send(
                driver, recipient=driver, verb=f'You can confirm this booking', 
                target=booking, 
                description='wait_for_confirmed'

            )
        return result


    booking_driver_arround_five_km = graphene.Field(
        graphene.List(UserType), 
        booking_id = graphene.ID(required=True),
        description="Return list driver arround 5km with the customer booking"
    )

    def resolve_booking_driver_arround_five_km(self, info, **kwargs):
        booking_id = kwargs.get('booking_id')
        booking=BookingModel.objects.get(pk=booking_id)
        booking_position = booking.departure_position[0]
        booking_lat = booking_position.get("lat")
        booking_lng = booking_position.get("lng")
        result = []
        available_driver = UserModel.objects.filter(Q(user_type=UserTypeEnum.DRIVER.value), Q(is_active=True), ~Q(driver_booked__status=StatusTypeEnum.WAIT_FOR_DRIVER.value),  ~Q(driver_booked__status=StatusTypeEnum.ON_GOING.value))
        for driver in available_driver:
            driver_position = driver.current_position[0]
            driver_lat = driver_position.get("lat")
            driver_lng = driver_position.get("lng")
            if resolve_distance(booking_lat,booking_lng,driver_lat,driver_lng) <=5000:
                result.append(driver)
        for driver in result:
            notify.send(
                driver, recipient=driver, verb=f'You can confirm this booking', 
                target=booking, 
                description='wait_for_confirmed'
            )
        return result




class NotificationQueries(graphene.ObjectType):
    my_unread_notification = graphene.Field(
        NotificationType, description="Return list of unread notification"
    )

    @login_required
    def resolve_my_unread_notification(self, info):
        current_user = info.context.user
        return current_user.notifications.unread().order_by("timestamp").last()

class BookingMutations(graphene.ObjectType):
    booking_create = BookingCreate.Field()
    booking_change_status = BookingChangeStatus.Field()
    booking_update_allow_driver_distance = BookingUpdateAllowDriverDistance.Field()
    booking_cancel = BookingCancel.Field()
    driver_finish_booking = DriverFinishBooking.Field()
    driver_confirm_booking = DriverConfirmBooking.Field()
    admin_choose_driver_for_booking = AdminChooseDriverForBooking.Field()

class NotificationMutations(graphene.ObjectType):
    notification_mark_read = NotificationMarkRead.Field()
