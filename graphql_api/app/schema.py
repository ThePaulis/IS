import graphene
from graphene_django.types import DjangoObjectType
from .models import Player


# Define an Enum for ordering
class OrderByEnum(graphene.Enum):
    NATIONALITY_ASC = "nationality"
    NATIONALITY_DESC = "-nationality"
    OVERALL_RATING_ASC = "overall_rating"
    OVERALL_RATING_DESC = "-overall_rating"
    AGE_ASC = "age"
    AGE_DESC = "-age"


# Define the PlayerType GraphQL type
class PlayerType(DjangoObjectType):
    class Meta:
        model = Player
        fields = "__all__"  # Include all fields from the Player model


# Define the Query class
class Query(graphene.ObjectType):
    all_players = graphene.List(
        PlayerType,
        order_by=OrderByEnum(description="Field to order by. Available options are defined in the OrderByEnum."),
    )

    def resolve_all_players(self, info, order_by=None):
        players = Player.objects.all()
        if order_by:
            players = players.order_by(order_by.value)  # Use `.value` to get the actual string value of the Enum
        return players


# Create the schema
schema = graphene.Schema(query=Query)
