from datetime import datetime
import graphene
from graphql_jwt.decorators import login_required, superuser_required
from django.db import transaction
from django.db.models import Count, F, Value, Q
from constance import config
from notifications.signals import notify
from notifications.models import Notification as NotificationModel

from ...graphql.core.mutations import ModelMutation
from .types import Booking as BookingType, BookingCreateInput
from .enums import StatusTypeEnum, BookingTypeEnum
from .resolvers import resolve_distance
from ..core.types.common import BookingError
from ...booking.error_codes import BookingErrorCode

from ...booking.models import Booking as BookingModel, DriverConfirmBooking as DriverConfirmBookingModel
from ...account.models import User as UserModel
from ..account.enums import UserTypeEnum, CarTypeEnum
from ...core.utils.firebase import notify_by_fcm_tokens

class BookingCreate(ModelMutation):
    class Arguments:
        input = BookingCreateInput(
            description="Race create input", required=True
        )
    class Meta:
        description = "User create booking."
        model = BookingModel
        error_type_class = BookingError
        error_type_field = "errors"

    @classmethod
    @login_required
    def perform_mutation(cls, _root, info, **data):
        current_user=info.context.user
        instance = cls.get_instance(info, **data)
        data = data.get("input")
        cleaned_input = cls.clean_input(
                info=info, instance=instance, data=data
            )
        customer_id=None
        if data.get("customer_id") is not None:
            customer_id = data.get("customer_id")
            cleaned_input["is_registered_user"] = True
            if customer_id != current_user.id:  #call center book for register user
                if current_user.user_type != UserTypeEnum.CALL_CENTER.value:
                    return cls(
                    errors=[
                        BookingError(
                            message="You are invalid to book for this customer",
                            code=BookingErrorCode.INVALID,
                            field="customer_id"
                        )
                    ]
                )
                customer = UserModel.objects.get(id=customer_id)
                cleaned_input["customer"] = customer
                cleaned_input["phone_number"] = customer.phone_number
            else: #customer book for himself
                cleaned_input["customer"] = current_user
        else: #un_registered_user
            if current_user.user_type != UserTypeEnum.CALL_CENTER.value:
                return cls(
                    errors=[
                        BookingError(
                            message="You are invalid to book for this customer",
                            code=BookingErrorCode.INVALID,
                            field="customer_id"
                        )
                    ]
                )
            cleaned_input["is_registered_user"] = False
            cleaned_input["phone_number"] = data.get("phone_number")
        departure = data.get("departure")
        destination = data.get("destination")
        car_type = data.get("car_type")
        
        if customer_id != current_user.id:
            cleaned_input["booking_type"]=BookingTypeEnum.BY_PHONE.value
        else:
            cleaned_input["booking_type"]=BookingTypeEnum.ON_APP.value
        cleaned_input["booking_time"]=datetime.now()
        # departure_position = data.get("departure_position")[0]
        # destination_position = data.get("destination_position")[0]
        # cleaned_input["total_distance"]= resolve_distance(departure_position.get("lat"), departure_position.get("lng"), destination_position.get("lat"), destination_position.get("lng")) / 1000
        cleaned_input["total_distance"] = data.get("total_distance")
        cleaned_input["total_fee"]=cleaned_input["total_distance"] * config.PRICE_CHARGE_PER_KM

        instance = cls.construct_instance(instance, cleaned_input)
        cls.clean_instance(info, instance)
        cls.save(info, instance, cleaned_input)
        if current_user.fcm_token is not None:
                notify_by_fcm_tokens.delay(
                    fcm_tokens=[current_user.fcm_token],
                    message_title="[BOOKING] Congratulation!",
                    message_body="You've booked from {} with {} {}.".format(
                        departure, destination)
                )
        return cls.success_response(instance)

class BookingChangeStatus(graphene.Mutation):
    errors = graphene.Field(
        graphene.List(
            graphene.NonNull(BookingError),
            description="List of errors that occurred executing the mutation.",
        ),
        default_value=[],
        required=True,
    )

    class Arguments:
        id = graphene.ID(
            description="Booking change status input", required=True
        )
        status = StatusTypeEnum(required=True)

    class Meta:
        description = "Admin/Staff change status of booking."
        error_type_field = "errors"

    @classmethod
    @login_required
    def mutate(cls, _root, info, **data):
        current_user = info.context.user
        booking_id = data.get("id")
        new_status = data.get("status")
        try:
            booking = BookingModel.objects.get(id = booking_id)
        except BookingModel.DoesNotExist:
            return cls(
                errors=[
                    BookingError(
                        message="Booking not found",
                        code=BookingErrorCode.NOT_FOUND,
                        field="booking_id"
                    )
                ]
            )
        if booking.driver != current_user and booking.customer != current_user:
            return cls(
                errors=[
                    BookingError(
                        message="You are invalid to change status for this booking",
                        code=BookingErrorCode.INVALID
                    )
                ]
            )
        if booking.status == data.get("status"):
            return cls(
                errors=[
                    BookingError(
                        message="New status is the same as current status",
                        code=BookingErrorCode.INVALID
                    )
                ]
            )
        if booking.status == StatusTypeEnum.CANCELLED.value:
            return cls(
                errors=[
                    BookingError(
                        message="This booking is already cancelled",
                        code=BookingErrorCode.CANCELLED
                    )
                ]
            )
        if new_status == StatusTypeEnum.CANCELLED.value:
            return cls(
                errors=[
                    BookingError(
                        message="Cannot cancel booking by this API",
                        code=BookingErrorCode.INVALID
                    )
                ]
            )
        if new_status == StatusTypeEnum.COMPLETED.value:
            return cls(
                errors=[
                    BookingError(
                        message="Cannot complete booking by this API",
                        code=BookingErrorCode.INVALID
                    )
                ]
            ) 
        booking.status = new_status
        booking.save(update_fields=["status"])
        return cls(
            errors=[]
        )

class BookingUpdateAllowDriverDistance(graphene.Mutation):
    errors = graphene.Field(
        graphene.List(
            graphene.NonNull(BookingError),
            description="List of errors that occurred executing the mutation.",
        ),
        default_value=[],
        required=True,
    )

    class Arguments:
        id = graphene.ID(
            description="Booking change status input", required=True
        )
        allow_driver_distance = graphene.Int(required=True)

    class Meta:
        description = "Booking update allow driver distance."
        error_type_field = "errors"

    @classmethod
    @login_required
    def mutate(cls, _root, info, **data):
        booking_id = data.get("id")
        allow_driver_distance = data.get("allow_driver_distance")
        try:
            booking = BookingModel.objects.get(id = booking_id)
        except BookingModel.DoesNotExist:
            return cls(
                errors=[
                    BookingError(
                        message="Booking not found",
                        code=BookingErrorCode.NOT_FOUND,
                        field="booking_id"
                    )
                ]
            )
        
        booking.allow_driver_distance = allow_driver_distance
        booking.save(update_fields=["allow_driver_distance"])
        return cls(
            errors=[]
        )

class BookingCancel(graphene.Mutation):
    errors = graphene.Field(
        graphene.List(
            graphene.NonNull(BookingError),
            description="List of errors that occurred executing the mutation.",
        ),
        default_value=[],
        required=True,
    )

    class Arguments:
        id = graphene.ID(
            description="Booking cancel input", required=True
        )

    class Meta:
        description = "User (Custommer or Driver) cancel booking."
        error_type_field = "errors"

    @classmethod
    @login_required
    def mutate(cls, _root, info, **data):
        booking_id = data.get("id")
        current_user = info.context.user
        try:
            booking = BookingModel.objects.get(id = booking_id)
        except BookingModel.DoesNotExist:
            return cls(
                errors=[
                    BookingError(
                        message="Booking not found",
                        code=BookingErrorCode.NOT_FOUND,
                        field="booking_id"
                    )
                ]
            )
        if current_user.is_superuser == True:
            booking.status = StatusTypeEnum.CANCELLED.value
            booking.finish_time = datetime.now()
            booking.save()
            if booking.customer is not None:
                notify.send(current_user, recipient=booking.customer, verb=f'Your booking has been cancelled', 
                            target=booking, 
                            description='cancelled')
        else:
            if booking.status != StatusTypeEnum.WAIT_FOR_CONFIRMED.value and booking.status != StatusTypeEnum.WAIT_FOR_DRIVER.value:
                return cls(
                    errors=[
                        BookingError(
                            message="Booking cannot be cancelled",
                            code=BookingErrorCode.INVALID,
                            field="booking.status"
                        )
                    ]
                )
            if booking.driver != current_user and booking.customer != current_user:
                return cls(
                    errors=[
                        BookingError(
                            message="You are invalid to cancel this booking",
                            code=BookingErrorCode.INVALID,
                            field="current user"
                        )
                    ]
                )
            if booking.driver == current_user:
                booking.cancel_count += 1
                if booking.cancel_count >= config.MAX_CANCEL_COUNT:
                    booking.status = StatusTypeEnum.CANCELLED.value
                    booking.finish_time = datetime.now()
                    if booking.customer is not None:
                        notify.send(current_user, recipient=booking.customer, verb=f'Your booking has been cancelled', 
                            target=booking, 
                            description='cancelled')
                else:
                    booking.status = StatusTypeEnum.WAIT_FOR_CONFIRMED.value
                    booking.driver = None
                    if booking.customer is not None:
                        notify.send(current_user, recipient=booking.customer, verb=f'Your driver has cancelled bookings, looking for another driver', 
                            target=booking, 
                            description='wait_for_confirmed')
                booking.save()
            elif booking.customer == current_user:
                booking.status = StatusTypeEnum.CANCELLED.value
                booking.finish_time = datetime.now()
                booking.save()
                notify.send(current_user, recipient=booking.driver, verb=f'Your booking has been cancelled', 
                        target=booking, 
                        description='cancelled')
        return cls(
            errors=[]
        )


class DriverFinishBooking(graphene.Mutation):
    errors = graphene.Field(
        graphene.List(
            graphene.NonNull(BookingError),
            description="List of errors that occurred executing the mutation.",
        ),
        default_value=[],
        required=True,
    )

    class Arguments:
        id = graphene.ID(
            description="Driver confirm finish the booking", required=True
        )

    class Meta:
        description = "Driver confirm finish the booking."
        error_type_field = "errors"

    @classmethod
    @login_required
    def mutate(cls, _root, info, **data):
        booking_id = data.get("id")
        current_user = info.context.user
        try:
            booking = BookingModel.objects.get(id = booking_id)
        except BookingModel.DoesNotExist:
            return cls(
                errors=[
                    BookingError(
                        message="Booking not found",
                        code=BookingErrorCode.NOT_FOUND,
                        field="booking_id"
                    )
                ]
            )
        if booking.status != StatusTypeEnum.ON_GOING.value:
            return cls(
                errors=[
                    BookingError(
                        message="Booking cannot be completed",
                        code=BookingErrorCode.INVALID,
                        field="booking.status"
                    )
                ]
            )
        if booking.driver != current_user:
            return cls(
                errors=[
                    BookingError(
                        message="You are invalid to finish this booking",
                        code=BookingErrorCode.INVALID,
                        field="current user"
                    )
                ]
            )
        driver_position = current_user.current_position[0]
        destination_position = booking.destination_position[0]
        different_distance = resolve_distance(driver_position.get("lat"), driver_position.get("lng"), destination_position.get("lat"), destination_position.get("lng"))
        if different_distance > config.ACCEPTABLE_DISTANCE_FINISH:
            return cls(
                errors=[
                    BookingError(
                        message="You take customer to wrong destination",
                        code=BookingErrorCode.INVALID,
                        field="destination position"
                    )
                ]
            )
        booking.finish_time = datetime.now()
        booking.status = StatusTypeEnum.COMPLETED.value
        booking.save()
        if booking.customer is not None:
            notify.send(current_user, recipient=booking.customer, verb=f'Your booking has completed', 
                            target=booking, 
                            description='completed')

        return cls(
            errors=[]
        )

class DriverConfirmBooking(graphene.Mutation):
    errors = graphene.Field(
        graphene.List(
            graphene.NonNull(BookingError),
            description="List of errors that occurred executing the mutation.",
        ),
        default_value=[],
        required=True,
    )

    class Arguments:
        id = graphene.ID(
            description="Driver confirm to get the booking", required=True
        )

    class Meta:
        description = "Driver confirm to get the booking."
        error_type_field = "errors"

    @classmethod
    @login_required
    def mutate(cls, _root, info, **data):
        booking_id = data.get("id")
        current_user = info.context.user
        try:
            booking = BookingModel.objects.get(id = booking_id)
        except BookingModel.DoesNotExist:
            return cls(
                errors=[
                    BookingError(
                        message="Booking not found",
                        code=BookingErrorCode.NOT_FOUND,
                        field="booking_id"
                    )
                ]
            )
        if booking.status != StatusTypeEnum.WAIT_FOR_CONFIRMED.value:
            return cls(
                errors=[
                    BookingError(
                        message="Driver cannot confirm this booking",
                        code=BookingErrorCode.INVALID,
                        field="booking.status"
                    )
                ]
            )
        if current_user.driver_booked.filter(Q(finish_time__isnull=True) & ~Q(status=StatusTypeEnum.CANCELLED.value)
            & ~Q(status=StatusTypeEnum.COMPLETED.value)).count() > 0:
            return cls(
                errors=[
                    BookingError(
                        message="You are on the ride, cannot confirm this ride",
                        code=BookingErrorCode.INVALID
                    )
                ]
            )
        if current_user.driver_confirm_booking.filter(booking=booking):
            return cls(
                errors=[
                    BookingError(
                        message="You are already confirmed this booking",
                        code=BookingErrorCode.INVALID
                    )
                ]
            )
        booking_position = booking.departure_position[0]
        booking_lat = booking_position.get("lat")
        booking_lng = booking_position.get("lng")
        driver_position = current_user.current_position[0]
        driver_lat = driver_position.get("lat")
        driver_lng = driver_position.get("lng")
        distance = resolve_distance(booking_lat,booking_lng,driver_lat,driver_lng) / 1000
        DriverConfirmBookingModel.objects.create(booking=booking, driver=current_user, distance=distance)

        return cls(
            errors=[]
        )

class AdminChooseDriverForBooking(graphene.Mutation):
    errors = graphene.Field(
        graphene.List(
            graphene.NonNull(BookingError),
            description="List of errors that occurred executing the mutation.",
        ),
        default_value=[],
        required=True,
    )

    class Arguments:
        id = graphene.ID(
            description="DriverConfirmBooking ID", required=True
        )

    class Meta:
        description = "Admin choose driver for booking in list driver confirm booking."
        error_type_field = "errors"

    @classmethod
    @login_required
    def mutate(cls, _root, info, **data):
        _id = data.get("id")
        current_user = info.context.user
        try:
            driver_confirm_booking = DriverConfirmBookingModel.objects.get(id = _id)
        except BookingModel.DoesNotExist:
            return cls(
                errors=[
                    BookingError(
                        message="Driver confirm Booking not found",
                        code=BookingErrorCode.NOT_FOUND,
                        field="_id"
                    )
                ]
            )
        if driver_confirm_booking.booking.driver is not None:
            return cls(
                errors=[
                    BookingError(
                        message="This booking already have driver",
                        code=BookingErrorCode.INVALID,
                        field="booking.status"
                    )
                ]
            )
        if current_user.user_type != UserTypeEnum.ADMIN.value and current_user.user_type != UserTypeEnum.CALL_CENTER.value:
            return cls(
                errors=[
                    BookingError(
                        message="Invalid to choose the driver for booking",
                        code=BookingErrorCode.INVALID
                    )
                ]
            )
        booking = driver_confirm_booking.booking
        booking.driver = driver_confirm_booking.driver
        booking.status = StatusTypeEnum.WAIT_FOR_DRIVER.value
        booking.save()
        if booking.customer is not None:
            notify.send(current_user, recipient=booking.customer, verb=f'Your booking already has driver, please wait for driver', 
                            target=booking, 
                            description='wait_for_driver')
        notify.send(current_user, recipient=booking.driver, verb=f'You has been picked for this booking', 
                        target=booking, 
                        description='wait_for_driver')
        driver_confirm_booking_list = DriverConfirmBookingModel.objects.filter(booking=booking)
        for each_confirm in driver_confirm_booking_list:
            each_confirm.delete()

        return cls(
            errors=[]
        )

class NotificationMarkRead(graphene.Mutation):
    errors = graphene.Field(
        graphene.List(
            graphene.NonNull(BookingError),
            description="List of errors that occurred executing the mutation.",
        ),
        default_value=[],
        required=True,
    )

    class Arguments:
        id = graphene.ID(
            description="Notification ID", required=True
        )

    class Meta:
        description = "Mark read notification."
        error_type_field = "errors"

    @classmethod
    @login_required
    def mutate(cls, _root, info, **data):
        _id = data.get("id")
        current_user = info.context.user
        try:
            notification = current_user.notifications.get(id = _id)
        except NotificationModel.DoesNotExist:
            return cls(
                errors=[
                    BookingError(
                        message="Notification not found",
                        code=BookingErrorCode.NOT_FOUND,
                        field="_id"
                    )
                ]
            )
        notification.unread = False
        notification.save()