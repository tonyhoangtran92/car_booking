from graphene_federation import build_schema

from .account.schema import AccountMutations, AccountQueries
from .booking.schema import BookingMutations, BookingQueries, NotificationQueries, NotificationMutations

class Query(
    AccountQueries,
    BookingQueries,
    NotificationQueries,
):
    pass


class Mutation(
    AccountMutations,
    BookingMutations,
    NotificationMutations,
):
    pass


schema = build_schema(Query, mutation=Mutation)
