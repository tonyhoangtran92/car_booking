default_app_config = "src.booking.apps.BookingConfig"


class BookingType:
    ON_APP = "on_app"
    BY_PHONE = "by_phone"

    CHOICES = [
        (ON_APP, "on_app"),
        (BY_PHONE, "by_phone"),
    ]

class StatusType:
    WAIT_FOR_CONFIRMED = "wait_for_confirmed"
    WAIT_FOR_DRIVER = "wait_for_driver"
    ON_GOING = "on_going"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    CHOICES = [
        (WAIT_FOR_CONFIRMED, "wait_for_confirmed"),
        (WAIT_FOR_DRIVER, "wait_for_driver"),
        (ON_GOING, "on_going"),
        (COMPLETED, "completed"),
        (CANCELLED, "cancelled"),
    ]
    