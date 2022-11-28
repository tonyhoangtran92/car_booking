from constance import config
from datetime import datetime, timedelta
from django.db import transaction
from django.db.models import Case, F, FloatField, IntegerField, Q, Sum, When
from notifications.signals import notify
from ...celeryconf import app
from ...booking.models import Booking as BookingModel, DriverConfirmBooking
from .enums import StatusTypeEnum

@app.task
def _auto_choose_driver_for_booking():
    now=datetime.utcnow()
    booking_lists = BookingModel.objects.filter(status = StatusTypeEnum.WAIT_FOR_CONFIRMED.value)
    if booking_lists is not None:
        for booking in booking_lists:
            if now-booking.booking_time > timedelta(minutes=1):
                driver_confirm_list = booking.booking_driver_confirm.all()
                if driver_confirm_list is not None:
                    small_distance = driver_confirm_list.first().distance
                    for driver_confirm in driver_confirm_list:
                        if driver_confirm.distance < small_distance:
                            small_distance=driver_confirm.distance
                    driver_choose = None
                    for driver_confirm in driver_confirm_list:
                        if driver_confirm.distance == small_distance:
                            driver_choose=driver_confirm.driver
                    driver_confirm_list.delete()
                    booking.status=StatusTypeEnum.WAIT_FOR_DRIVER.value
                    booking.driver=driver_choose
                    booking.save(update_fields=["status", "driver"])