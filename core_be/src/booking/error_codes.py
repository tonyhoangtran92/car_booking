from enum import Enum


class BookingErrorCode(Enum):
    INVALID = "invalid"
    NOT_FOUND = "not_found"
    CANCELLED = "cancelled"
