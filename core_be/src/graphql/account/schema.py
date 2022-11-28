import graphene
from django.db.models import Q
from graphql_jwt.decorators import login_required, superuser_required
from constance import config

from .mutations import AccountUpdate, UserChangeAvailable, Logout, UserUpdateLocation, UserLogin, ConfigurationUpdate
from .types import User as UserType, Configuration
from ..core.fields import FilterInputConnectionField
from ...settings import CONSTANCE_CONFIG

class AccountQueries(graphene.ObjectType):
    me = graphene.Field(
        UserType, description="Return the currently authenticated user."
    )

    @login_required
    def resolve_me(self, info):
        current_user = info.context.user
        return current_user

    configuration_read = graphene.Field(
        Configuration,
        key=graphene.String(required=True),
        description="Return config value by a config key.",
    )

    @superuser_required
    def resolve_configuration_read(self, info, **kwargs):
        key = kwargs.get("key")
        
        value = getattr(config, key)
        return Configuration(key=key, value=value)


class AccountMutations(graphene.ObjectType):
    user_login = UserLogin.Field()
    account_update = AccountUpdate.Field()
    user_change_available = UserChangeAvailable.Field()
    logout = Logout.Field()
    user_update_location = UserUpdateLocation.Field()
    configuration_update = ConfigurationUpdate.Field()