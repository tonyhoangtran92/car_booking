from enum import Enum


class CoreErrorCode(Enum):
    GRAPHQL_ERROR = "graphql_error"
    UNKNOWN_ERROR = "unknown_error" # aka. exception
    KEY_ERROR = "key_error" # aka. exception
    INVALID = "invalid"
    NOT_FOUND = "not_found"
    NOT_SUPPORT = "not_support"
    PROCESSING_ERROR = "processing_error"
    REQUIRED = "required"
    TIMEOUT = "timeout"
    TOO_SHORT = "too_short"
    UNIQUE = "unique"
    VERIFY_FAIL = "verify_fail"
