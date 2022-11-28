from graphene import relay
from graphene_django import DjangoObjectType

from ....core.models import CountryArea


class CountryArea(DjangoObjectType):
    class Meta:
        interfaces = (relay.Node,)
        model = CountryArea
