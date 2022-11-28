
import base64
from datetime import datetime, timedelta
import decimal
import json
import logging
import re

from time import time as timer
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from constance import config

from graphql_jwt.exceptions import JSONWebTokenError
from graphql_jwt.middleware import JSONWebTokenMiddleware


from ..core.utils.firebase import verify_id_token_and_get_detail_user
from firebase_admin import exceptions, messaging

ERROR_CODE_FIELDS = [
    "errors",
]

LIST_OF_NOT_CHECK_ADMINISTRATOR_LOGIN_VERIFY_APIS = [
    "administratorForgotPassword",
    "administratorLogin",
    "administratorLoginVerify",
    "administratorResetPassword",
]

LIST_OF_RESET_LOGIN_APIS = [
    "administratorChangePassword",
    "administratorLogout",
]

UserModel = get_user_model()


class JWTMiddleware(JSONWebTokenMiddleware):
    def resolve(self, next, root, info, **kwargs):
        start = timer()
        request = info.context
        auth = request.headers.get("authorization", None)
        name_api = request.headers.get("api-name", None)

        user_info_on_firebase = None
        user_info_on_db = None

        if auth is not None:
            id_token = auth.split(" ")[1]
            try:
                user_info_on_db = UserModel.objects.get(id_token=id_token)
                dt_exp = user_info_on_db.expiration_time
                dt_now = datetime.now(timezone.utc)
                if dt_exp - dt_now < timedelta(0):
                    raise exceptions.UnauthenticatedError("Token is expired")
            except UserModel.DoesNotExist:
                if name_api == "logout":
                    return []
                user_info_on_firebase = verify_id_token_and_get_detail_user(
                    id_token)
        if user_info_on_db:
            request.user = user_info_on_db
        elif user_info_on_firebase:
            user_data = user_info_on_firebase.get("_data")
            firebase_uid = user_data.get("localId")
            user_email = user_data.get("email")
            user, _ = UserModel.objects.get_or_create(
                # firebase_uid=firebase_uid,  # TODO: uncomment me !?
                email=user_email)
            user.firebase_uid = firebase_uid
            user.id_token = id_token
            user.expiration_time = datetime.now(timezone.utc) + timedelta(days=90)
            if user.full_name is None:
                user.full_name = user_email.split('@')[0]
            user.save(update_fields=["expiration_time", "id_token", "full_name", "firebase_uid"])

        if not hasattr(request, "user"):
            request.user = AnonymousUser()
        response = super().resolve(next, root, info, **kwargs)
        self.logging_error_request(info, response)
        duration = round((timer() - start) * 1000, 2)
        if duration >= settings.API_MIN_TIME_TO_LOG:
            parent_type_name = str(root.__class__) if root else ''
            logging.warning(
                f"Taking too long: {parent_type_name}.{info.field_name}: {duration} ms")
        return response

    def get_body(self, info):
        headers = info.context.headers
        content_type = headers["Content-Type"]
        if "multipart/form-data" in content_type:
            body = info.context._post["operations"]
        elif "application/json" in content_type:
            body = info.context._body.decode("utf-8")
        return body

    def administrator_reset_login(self, info):
        is_administrator_reset_login = False
        if hasattr(info.context, "is_administrator_reset_login"):
            is_administrator_reset_login = getattr(info.context, "is_administrator_reset_login")
        body = self.get_body(info)
        if is_administrator_reset_login:
            for api_name in LIST_OF_RESET_LOGIN_APIS:
                if api_name in body:
                    return True

    

    def logging_error_request(self, info, response):
        if not hasattr(info.context, "logged"):  # show only once
            try:
                user = info.context.user
                headers = info.context.headers
                content_type = headers["Content-Type"]
                if "multipart/form-data" in content_type:
                    body = info.context._post["operations"]
                elif "application/json" in content_type:
                    body = info.context._body.decode("utf-8")

                json_body = json.loads(body)
                variables = json_body.get("variables")
                query = json_body.get("query", "")
                query = re.sub("\n", " ", str(query))
                query = re.sub(" +", " ", query)

                if user.is_authenticated:
                    user_pk = user.pk
                else:
                    user_pk = None
                response_dict = response.__dict__
                _rejection_handler0 = response_dict.get("_rejection_handler0")
                error = None
                for error_field in ERROR_CODE_FIELDS:
                    if hasattr(_rejection_handler0, error_field):
                        errors = getattr(
                            _rejection_handler0, error_field)
                        if errors:
                            error = errors[0].__dict__
                        break
                if error:  # handled error
                    self.logging_handled_error_request(
                        info, user_pk, body, variables, query, error)
                elif response._traceback:  # unknown error
                    self.logging_unknown_error_request(
                        info, user_pk, body, variables, query)
                else:
                    self.logging_normal_request(
                        info, user_pk, body, variables, query)
            except Exception as e:
                print(str(e))
        setattr(info.context, "logged", 1)

    def logging_hidden_request(self, info, user_pk, body, api_name, error=None):
        if error:
            logging.error(
                "\n::::::::: PK= %s\n::::::::: Query: %s\n::::::::: ERROR: %s",
                user_pk,
                api_name, error
            )
        else:
            logging.warning(
                "\n::::::::: PK= %s\n::::::::: Query: %s",
                user_pk,
                api_name,
            )

    def logging_handled_error_request(self,  info, user_pk, body, variables, query, error=None):
        logging.error(
            "\n::::::::: PK= %s\n::::::::: Variables: %s \n::::::::: Body: %s \n::::::::: ERROR: %s",
            user_pk,
            variables, query, error
        )

    def logging_unknown_error_request(self,  info, user_pk, body, variables, query, error=None):
        logging.error(
            "\n:::::::::::PK= %s\n::::::::: Variables: %s \n::::::::: Body: %s \n::::::::: Body: %s",
            user_pk,
            variables, query,
        )

    def logging_normal_request(self, info, user_pk, body, variables, query):
        logging.warning(
            "\n:::::::::::PK= %s\n::::::::: Variables: %s \n::::::::: Body: %s",
            user_pk,
            variables, query,
        )
