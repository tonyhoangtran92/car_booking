from enum import Enum


class AccountErrorCode(Enum):
    INVALID = "invalid"
    INVALID_CREDENTIALS = "invalid_credentials"
    VERIFY_FAIL = "verify_fail"
    NOT_FOUND = "not_found"
    INVALID_FCM_TOKEN = "invalid_fcm_token"
    FCM_TOKEN_IS_UNCHANGED = "fcm_token_is_unchanged"
