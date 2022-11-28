from decimal import Decimal
from django.conf import settings
import graphene
from graphene.types import Scalar
from graphql.language.ast import (
    FloatValue,
    IntValue,
    StringValue,
)
from uuid import UUID as _UUID
from graphql.language.printer import print_ast
from graphql.error import GraphQLError
from datetime import timedelta
from ..enums import AccountErrorCode, BookingErrorCode, CoreErrorCode
from ....core.utils import encode_integer_value, encode_float_value, encode_string_value, decode_integer_value, decode_float_value, decode_string_value, encode_duration_value, decode_duration_value


class Error(graphene.ObjectType):
    field = graphene.String(
        description=(
            "Name of a field that caused the error. A value of `null` indicates that "
            "the error isn't associated with a particular field."
        ),
        required=False,
    )
    message = graphene.String(description="The error message.")

    class Meta:
        description = "Represents an error in the input of a mutation."


class CoreError(Error):
    code = CoreErrorCode(description="The error code.", required=True)


class AccountError(Error):
    code = AccountErrorCode(description="The error code.", required=True)


class BookingError(Error):
    code = BookingErrorCode(description="The error code.", required=True)


class DateRange(graphene.ObjectType):
    gte = graphene.Date(description="Start date.")
    lte = graphene.Date(description="End date.")


class DateRangeInput(graphene.InputObjectType):
    gte = graphene.Date(description="Start date.", required=False)
    lte = graphene.Date(description="End date.", required=False)


class EncodableInt(graphene.Int):
    '''Encodable Int'''

    @staticmethod
    def serialize(value):
        return encode_integer_value(value)

    @classmethod
    def parse_literal(cls, node, _variables=None):
        if not isinstance(node, (StringValue, IntValue)):
            # if not isinstance(node, StringValue) and settings.IS_ENCODING_RESPONSE:
            raise GraphQLError(
                f"Cannot represent maybe-encoded-value: {print_ast(node)}"
            )
        return cls.parse_value(node.value)

    @staticmethod
    def parse_value(value):
        return decode_integer_value(value)


class EncodableFloat(Scalar):
    '''Encodable Float'''

    @staticmethod
    def serialize(value):
        return encode_float_value(value)

    @classmethod
    def parse_literal(cls, node, _variables=None):
        if not isinstance(node, (StringValue, IntValue, FloatValue)):
            # if not isinstance(node, StringValue) and settings.IS_ENCODING_RESPONSE:
            raise GraphQLError(
                f"Cannot represent maybe-encoded-value: {print_ast(node)}"
            )
        return cls.parse_value(node.value)

    @staticmethod
    def parse_value(value):
        return decode_float_value(value)


class EncodableString(Scalar):
    '''Encodable String'''

    @staticmethod
    def serialize(value):
        return encode_string_value(value)

    @classmethod
    def parse_literal(cls, node, _variables=None):
        if not isinstance(node, StringValue):
            # if not isinstance(node, StringValue) and settings.IS_ENCODING_RESPONSE:
            raise GraphQLError(
                f"Cannot represent maybe-encoded-value: {print_ast(node)}"
            )
        return cls.parse_value(node.value)

    @staticmethod
    def parse_value(value):
        return decode_string_value(value)

class EncodableDuration(Scalar):
    '''Encodable Duration'''

    @staticmethod
    def serialize(value):
        return encode_duration_value(value)

    @classmethod
    def parse_literal(cls, node, _variables=None):
        if not isinstance(node, (StringValue)):
            # if not isinstance(node, StringValue, IntValue) and settings.IS_ENCODING_RESPONSE:
            raise GraphQLError(
                f"Cannot represent maybe-encoded-value: {print_ast(node)}"
            )
        return cls.parse_value(node.value)

    @staticmethod
    def parse_value(value):
        return decode_duration_value(value)

class UUID(Scalar):
    """
    Leverages the internal Python implementation of UUID (uuid.UUID) to provide native UUID objects
    in fields, resolvers and input.
    """

    @staticmethod
    def serialize(uuid):
        if isinstance(uuid, str):
            uuid = _UUID(uuid)

        assert isinstance(
            uuid, _UUID), f"Expected UUID instance, received {uuid}"
        return str(uuid)

    @classmethod
    def parse_literal(cls, node, _variables=None):
        if isinstance(node, StringValue):
            return cls.parse_value(node.value)

    @staticmethod
    def parse_value(value):
        return _UUID(value)
