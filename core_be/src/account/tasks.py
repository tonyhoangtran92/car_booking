import time
from datetime import datetime, timedelta
from django.db import transaction
from django.db.models import Case, F, FloatField, IntegerField, Q, Sum, When
from ..account.models import User
from ..celeryconf import app


# @app.task
# def _update_driver_position():
    

