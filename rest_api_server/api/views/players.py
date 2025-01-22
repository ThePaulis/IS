from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection

class GetAllPlayers(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM players")  # Replace with your actual table/view name
            result = cursor.fetchall()

            players = [
                {
                    "id": row[0],
                    "name": row[1],
                    "full_name": row[2],
                    "birth_date": row[3],
                    "age": row[4],
                    "height_cm": row[5],
                    "weight_kgs": row[6],
                    "positions": row[7],
                    "nationality": row[8],
                    "overall_rating": row[9],
                    "potential": row[10],
                    "value_euro": row[11],
                    "wage_euro": row[12],
                    "preferred_foot": row[13],
                    "international_reputation": row[14],
                    "weak_foot": row[15],
                    "skill_moves": row[16],
                    "body_type": row[17],
                    "release_clause_euro": row[18],
                    "national_team": row[19],
                    "national_rating": row[20],
                    "national_team_position": row[21],
                    "national_jersey_number": row[22],
                    "crossing": row[23],
                    "finishing": row[24],
                    "heading_accuracy": row[25],
                    "short_passing": row[26],
                    "volleys": row[27],
                    "dribbling": row[28],
                    "curve": row[29],
                    "freekick_accuracy": row[30],
                    "long_passing": row[31],
                    "ball_control": row[32],
                    "acceleration": row[33],
                    "sprint_speed": row[34],
                    "agility": row[35],
                    "reactions": row[36],
                    "balance": row[37],
                    "shot_power": row[38],
                    "jumping": row[39],
                    "stamina": row[40],
                    "strength": row[41],
                    "long_shots": row[42],
                    "aggression": row[43],
                    "interceptions": row[44],
                    "positioning": row[45],
                    "vision": row[46],
                    "penalties": row[47],
                    "composure": row[48],
                    "marking": row[49],
                    "standing_tackle": row[50],
                    "sliding_tackle": row[51]
                }
                for row in result
            ]

        return Response({"players": players}, status=status.HTTP_200_OK)
