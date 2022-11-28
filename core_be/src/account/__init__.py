from django.db import models

#default_app_config = "src.account.apps.AccountConfig"

class UserType:
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

class CarType:
    FOUR_SEAT = "four_seat"
    SEVEN_SEAT = "seven_seat"
    ANY = "any"
    
    CHOICES = [
        (FOUR_SEAT, "four_seat"),
        (SEVEN_SEAT, "seven_seat"),
        (ANY, "any")
    ]