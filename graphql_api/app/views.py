import logging
from django.http import JsonResponse
from rest_framework.views import APIView
from .schema import schema

# Configure logger
logging.basicConfig(level=logging.INFO)

class PlayersView(APIView):
    def get(self, request):
        logging.info('Fetching all players')
        query = '''
        {
            allPlayers {
                id
                name
                fullName
                birthDate
                age
                heightCm
                weightKgs
                positions
                nationality
                overallRating
                potential
                valueEuro
                wageEuro
                preferredFoot
                internationalReputation
                weakFoot
                skillMoves
                bodyType
                releaseClauseEuro
                nationalTeam
                nationalRating
                nationalTeamPosition
                nationalJerseyNumber
                crossing
                finishing
                headingAccuracy
                shortPassing
                volleys
                dribbling
                curve
                freekickAccuracy
                longPassing
                ballControl
                acceleration
                sprintSpeed
                agility
                reactions
                balance
                shotPower
                jumping
                stamina
                strength
                longShots
                aggression
                interceptions
                positioning
                vision
                penalties
                composure
                marking
                standingTackle
                slidingTackle
            }
        }
        '''
        result = schema.execute(
            query,
            context_value={'request': request}  # Include request in the context
        )

        if result.errors:
            logging.error(f"Errors occurred while fetching players: {result.errors}")
            return JsonResponse({'errors': [str(error) for error in result.errors]}, status=400)

        # Explicitly handle data serialization for safe JSON responses
        return JsonResponse(result.data or {}, safe=False)
