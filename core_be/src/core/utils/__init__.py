import base64
import decimal
import re
import socket
from typing import Type

from django.conf import settings
from django.db.models import Model
from django.utils.timezone import datetime, pytz


def is_valid_ipv4(ip: str) -> bool:
    """Check whether the passed IP is a valid V4 IP address."""
    try:
        socket.inet_pton(socket.AF_INET, ip)
    except socket.error:
        return False
    return True


def is_valid_ipv6(ip: str) -> bool:
    """Check whether the passed IP is a valid V6 IP address."""
    try:
        socket.inet_pton(socket.AF_INET6, ip)
    except socket.error:
        return False
    return True


def generate_unique_slug(
    instance: Type[Model], slugable_value: str, slug_field_name: str = "slug",
) -> str:
    """Create unique slug for model instance.
    Args:
        instance: model instance for which slug is created
        slugable_value: value used to create slug
        slug_field_name: name of slug field in instance model

    """
    slug = str(slugable_value).strip().replace(' ', '_')
    slug = re.sub(r'(?u)[^-\w.]', '', slug)
    unique_slug: Union["SafeText", str] = slug
    ModelClass = instance.__class__
    extension = 1

    search_field = f"{slug_field_name}__iregex"
    pattern = rf"{slug}_\d+$|{slug}$"
    slug_values = (
        ModelClass._default_manager.filter(  # type: ignore
            **{search_field: pattern}
        )
        .exclude(pk=instance.pk)
        .values_list(slug_field_name, flat=True)
    )
    while unique_slug in slug_values:
        extension += 1
        unique_slug = f"{slug}_{extension}"

    return unique_slug


def is_integer(n):
    return isinstance(n, int) or str(n).isnumeric() or str(n).isdigit()


def is_float(n):
    try:
        float(n)
        return True
    except ValueError:
        return False


def encode_base64(s: str):
    if s is None or type(s) is not str:
        return s
    if settings.IS_DEBUG_ENCODING_VALUES:
        return s
    return_value_bytes = s.encode("utf-8")
    base64_bytes = base64.b64encode(return_value_bytes)
    base64_string = base64_bytes.decode("utf-8")
    return base64_string


def encode_number_value(n):
    if n is None or type(n) not in (str, int, float, decimal.Decimal) or str(n)[:1] in ('(', '{', '['):
        return n
    s = None
    if is_integer(n):
        s = settings.INTEGER_ENCODE_PREFIX + str(n)
    elif is_float(n):
        s = settings.FLOAT_ENCODE_PREFIX + str(n)
    if s is not None:
        return encode_base64(s)
    return n


def encode_integer_value(n):
    if not hasattr(settings, "IS_ENCODING_RESPONSE") or settings.IS_ENCODING_RESPONSE == False:
        return n
    if n is None or not is_integer(n):
        return n
    return encode_base64(settings.INTEGER_ENCODE_PREFIX + str(n))


def encode_float_value(n):
    if not hasattr(settings, "IS_ENCODING_RESPONSE") or settings.IS_ENCODING_RESPONSE == False:
        return n
    if n is None or not is_float(n):
        return n
    return encode_base64(settings.FLOAT_ENCODE_PREFIX + str(n))


def encode_string_value(v):
    if not hasattr(settings, "IS_ENCODING_RESPONSE") or settings.IS_ENCODING_RESPONSE == False or v is None or type(v) is not str:
        return v
    return encode_base64(settings.STRING_ENCODE_PREFIX + v)

def encode_duration_value(v):
    if not hasattr(settings, "IS_ENCODING_RESPONSE") or settings.IS_ENCODING_RESPONSE == False:
        return v
    return encode_base64(settings.DURATION_ENCODE_PREFIX + str(v))

def encode_value(v):
    if not hasattr(settings, "IS_ENCODING_RESPONSE") or settings.IS_ENCODING_RESPONSE == False:
        return v
    if is_integer(v):
        return encode_integer_value(v)
    elif is_float(v):
        return encode_float_value(v)
    else:
        return encode_string_value(v)


def decode_base64(coded_value, prefix):
    if coded_value is None or not isinstance(coded_value, str) or str(coded_value)[:1] in ('(', '{', '[') or is_integer(coded_value) or is_float(coded_value):
        return coded_value
    value = base64.b64decode(coded_value).decode("utf-8")
    return value.removeprefix(prefix)


def decode_integer_value(v):
    return decode_base64(v, settings.INTEGER_ENCODE_PREFIX)


def decode_float_value(v):
    return decode_base64(v, settings.FLOAT_ENCODE_PREFIX)


def decode_string_value(v):
    return decode_base64(v, settings.STRING_ENCODE_PREFIX)

def decode_duration_value(v):
    return decode_base64(v, settings.DURATION_ENCODE_PREFIX)
