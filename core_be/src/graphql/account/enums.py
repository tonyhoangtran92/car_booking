import graphene

class UserTypeEnum(graphene.Enum):
    CUSTOMER = "customer"
    DRIVER = "driver"
    CALL_CENTER = "call_center"
    ADMIN = "admin"
    
    CHOICES = [
        (CUSTOMER, "customer"),
        (DRIVER, "driver"),
        (CALL_CENTER, "call_center"),
        (ADMIN, "admin")
    ]


class CarTypeEnum(graphene.Enum):
    FOUR_SEAT = "four_seat"
    SEVEN_SEAT = "seven_seat"
    ANY = "any"

    CHOICES = [
        (FOUR_SEAT, "four_seat"),
        (SEVEN_SEAT, "seven_seat"),
        (ANY, "any"),
    ]