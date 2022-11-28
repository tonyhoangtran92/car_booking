import graphene
from django.conf import settings
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.db import transaction
from graphql_jwt.decorators import login_required, superuser_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.validators import validate_email
from graphene.utils.thenables import maybe_thenable
from datetime import datetime
from constance import config
from constance.admin import ConstanceForm, get_values

from ...account.error_codes import AccountErrorCode
from ..core.types.common import AccountError
from ..core.mutations import BaseMutation, ModelDeleteMutation, ModelMutation
from .enums import *
from .types import User as UserType, AccountUpdateInput, PositionInput
from ...booking.models import Booking as BookingModel
from ..booking.enums import StatusTypeEnum
from graphql_jwt.decorators import (
    login_required,
    on_token_auth_resolve,
    superuser_required,
)

UserModel = get_user_model()

class AccountUpdate(ModelMutation):
    class Arguments:
        input = AccountUpdateInput(required=True)

    class Meta:
        description = "Update a registered user."
        model = UserModel
        error_type_class = AccountError
        error_type_field = "errors"

    @classmethod
    @superuser_required
    def perform_mutation(cls, _root, info, **data):
        data = data.get("input")
        user_id = data.get("id")
        try:
            instance = UserModel.objects.get(id = user_id)
        except UserModel.DoesNotExist:
            return cls(
                errors=[
                    AccountError(
                        message="User not found",
                        code=AccountErrorCode.NOT_FOUND
                    )
                ]
            )

        cleaned_input = cls.clean_input(
            info=info, instance=instance, data=data
        )
        instance = cls.construct_instance(instance, cleaned_input)
        cls.clean_instance(info, instance)
        cls.save(info, instance, cleaned_input)
        # cls._save_m2m(info, instance, cleaned_input)
        return cls.success_response(instance)


class Logout(BaseMutation):

    class Meta:
        description = "API logout"
        error_type_class = AccountError
        error_type_field = "errors"

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        current_user = info.context.user
        current_user.id_token = None
        current_user.save(update_fields=("id_token",))
        return cls(errors=[])


class UserChangeAvailable(graphene.Mutation):
    errors = graphene.Field(
        graphene.List(
            graphene.NonNull(AccountError),
            description="List of errors that occurred executing the mutation.",
        ),
        default_value=[],
        required=True,
    )

    class Arguments:
        status = graphene.Boolean(required=True)

    class Meta:
        description = "User change available status."
        error_type_field = "errors"

    @classmethod
    @login_required
    def mutate(cls, _root, info, **data):
        current_user = info.context.user
        new_status = data.get("status")
        if new_status == current_user.is_available:
            return cls(
                errors=[
                    AccountError(
                        message="New status is same as current available status",
                        code=AccountErrorCode.INVALID
                    )
                ]
            )
        if current_user.driver_booked.filter(Q(finish_time__isnull=True) & ~Q(status=StatusTypeEnum.CANCELLED.value)
            & ~Q(status=StatusTypeEnum.COMPLETED.value)).count() > 0:
            return cls(
                errors=[
                    AccountError(
                        message="You are on the ride, cannot change status",
                        code=AccountErrorCode.INVALID
                    )
                ]
            )
        current_user.is_available = new_status
        current_user.save(update_fields=("is_available",))
        return cls(errors=[])

class UserUpdateLocation(ModelMutation):

    class Arguments:
        input = PositionInput(required=True)

    class Meta:
        description = "Update a user location"
        model = UserModel
        error_type_class = AccountError
        error_type_field = "errors"

    @classmethod
    @login_required
    def perform_mutation(cls, _root, info, **data):
        current_user = info.context.user
        data = data.get("input")
        if data.current_position is not None:
            current_user.current_position = data.current_position
            current_user.save()
        return cls.success_response(current_user)


class UserLogin(BaseMutation):
    token = graphene.String()
    is_verified_email = graphene.Boolean()

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    class Meta:
        description = "User Login"
        error_type_class = AccountError
        error_type_field = "errors"

    @classmethod
    def validate_user(cls, user, password):
        if not user.check_password(password):
            return cls(
                errors=[
                    AccountError(
                        field="password",
                        message="Password is incorrect, please try again",
                        code=AccountErrorCode.INVALID,
                    )
                ]
            )

    @classmethod
    def perform_mutation(cls, root, info, **data):
        context = info.context
        email = data.get("email").lower()
        password = data.get("password")
        validate_email(email)
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return cls(
                errors=[
                    AccountError(
                        field="email",
                        message="Email does not exist, please try again",
                        code=AccountErrorCode.NOT_FOUND,
                    )
                ]
            )
        errors = cls.validate_user(user, password)
        if errors:
            return errors
        if hasattr(context, "user"):
            context.user = user

        result = cls(errors=[])
        payload = maybe_thenable((context, user, result), on_token_auth_resolve)
        user.id_token = payload.token
        user.expiration_time = datetime.now() + settings.JWT_EXPIRATION_DELTA
        user.save()
        return payload

class ConfigurationUpdate(graphene.Mutation):
    errors = graphene.Field(
        graphene.List(
            graphene.NonNull(AccountError),
            description="List of errors that occurred executing the mutation.",
        ),
        default_value=[],
        required=True,
    )

    class Meta:
        description = "Update a configuration"
        error_type_field = "errors"

    class Arguments:
        key = graphene.String(required=True, description="Configuration Key")
        value = graphene.Int(required=True, description="Configuration Value (Int ...)")

    @classmethod
    @superuser_required
    def mutate(cls, root, info, **data):
        key = data.get("key")
        value = data.get("value")
        try:
            form = ConstanceForm(initial=get_values())
            field = form.fields[key]
            clean_value = field.clean(field.to_python(value))
            setattr(config, key, clean_value)
        except KeyError as ex:
            return cls(
                errors=[
                    AccountError(
                        message="Unknown key: " + str(ex), code=AccountErrorCode.INVALID
                    )
                ]
            )
        except Exception as ex:
            return cls(
                errors=[AccountError(message=str(ex), code=AccountErrorCode.INVALID)]
            )

        return cls(errors=[])