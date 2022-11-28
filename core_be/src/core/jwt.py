from django.utils.crypto import get_random_string
from django.conf import settings
from constance import config
from datetime import datetime, timedelta
from django.utils import timezone

def create_access_token(user):
    token=get_random_string(length=64)
    user.id_token = token
    user.expiration_time = datetime.now(timezone.utc) + timedelta(days=90)