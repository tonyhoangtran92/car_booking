import decimal
import graphene

from graphene.types import Scalar
from graphql.language import ast
from graphene.types.scalars import MIN_INT, MAX_INT

class CustomDecimal(graphene.Float):
    """Custom Decimal implementation.

    Returns Decimal as a float in the API,
    parses float to the Decimal on the way back.
    """

    @staticmethod
    def parse_literal(node):
        try:
            return decimal.Decimal(node.value)
        except decimal.DecimalException:
            return None

    @staticmethod
    def parse_value(value):
        try:
            # Converting the float to str before parsing it to Decimal is
            # necessary to keep the decimal places as typed
            value = str(value)
            return decimal.Decimal(value)
        except decimal.DecimalException:
            return None

class BigInt(Scalar):
    """
    BigInt is an extension of the regular Int field
        that supports Integers bigger than a signed
        32-bit integer.
    """
    @staticmethod
    def big_to_float(value):
        num = int(value)
        if num > MAX_INT or num < MIN_INT:
            return float(int(num))
        return num
    serialize = big_to_float
    parse_value = big_to_float
    @staticmethod
    def parse_literal(node):
        if isinstance(node, ast.IntValue):
            num = int(node.value)
            if num > MAX_INT or num < MIN_INT:
                return float(int(num))
            return num