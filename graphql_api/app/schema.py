import graphene
from graphene_django.types import DjangoObjectType
from .models import Player


class PlayerType(DjangoObjectType):
    class Meta:
        model = Player
        fields = "__all__"


class UpdatePlayer(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        full_name = graphene.String()
        birth_date = graphene.String()
        age = graphene.String()
        height_cm = graphene.String()
        weight_kgs = graphene.String()
        positions = graphene.String()
        nationality = graphene.String()
        overall_rating = graphene.String()
        potential = graphene.String()
        value_euro = graphene.String()
        wage_euro = graphene.String()
        preferred_foot = graphene.String()
        international_reputation = graphene.String()
        weak_foot = graphene.String()
        skill_moves = graphene.String()
        body_type = graphene.String()
        release_clause_euro = graphene.String()
        national_team = graphene.String()
        national_rating = graphene.String()
        national_team_position = graphene.String()
        national_jersey_number = graphene.String()
        crossing = graphene.String()
        finishing = graphene.String()
        heading_accuracy = graphene.String()
        short_passing = graphene.String()
        volleys = graphene.String()
        dribbling = graphene.String()
        curve = graphene.String()
        freekick_accuracy = graphene.String()
        long_passing = graphene.String()
        ball_control = graphene.String()
        acceleration = graphene.String()
        sprint_speed = graphene.String()
        agility = graphene.String()
        reactions = graphene.String()
        balance = graphene.String()
        shot_power = graphene.String()
        jumping = graphene.String()
        stamina = graphene.String()
        strength = graphene.String()
        long_shots = graphene.String()
        aggression = graphene.String()
        interceptions = graphene.String()
        positioning = graphene.String()
        vision = graphene.String()
        penalties = graphene.String()
        composure = graphene.String()
        marking = graphene.String()
        standing_tackle = graphene.String()
        sliding_tackle = graphene.String()

    player = graphene.Field(PlayerType)

    def mutate(self, info, id, **kwargs):
        try:
            player = Player.objects.get(id=id)
            for field, value in kwargs.items():
                if value is not None:
                    setattr(player, field, value)
            player.save()
            return UpdatePlayer(player=player)
        except Player.DoesNotExist:
            raise Exception(f'Player with ID {id} does not exist')


class Query(graphene.ObjectType):
    all_players = graphene.List(PlayerType, name=graphene.String())

    def resolve_all_players(self, info, name=None):
        if name:
            return Player.objects.filter(name__icontains=name)
        return Player.objects.all()


class Mutation(graphene.ObjectType):
    update_player = UpdatePlayer.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
