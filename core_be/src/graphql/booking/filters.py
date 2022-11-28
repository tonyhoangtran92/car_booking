import django_filters
from ..booking.enums import BookingTypeEnum, StatusTypeEnum
from ..core.types import FilterInputObjectType
from ..core.filters import EnumFilter
from ...booking.models import Booking as BookingModel


def filter_booking_type_cass(qs, _, value):
    return qs.filter(booking_type=value)

def filter_status_type_class(qs, _, value):
    return qs.filter(status=value)

def filter_customer_class(qs, _, value):
    return qs.filter(customer__id=value)

def filter_driver_class(qs, _, value):
    return qs.filter(driver__id=value)


class BookingFilter(django_filters.FilterSet):
    booking_type = EnumFilter(input_class=BookingTypeEnum, method=filter_booking_type_cass)
    status_type = EnumFilter(input_class=StatusTypeEnum, method=filter_status_type_class)    
    customer_id = django_filters.Filter(method=filter_customer_class)
    driver_id = django_filters.Filter(method=filter_driver_class)

    class Meta:
        model = BookingModel
        fields = []

class BookingFilterInput(FilterInputObjectType):
    class Meta:
        filterset_class = BookingFilter