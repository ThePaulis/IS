from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection


class GetAllFiles(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM files")
            result = cursor.fetchall()
        files = [Book(id=row[0], name=row[1]) for row in result]
        return Response({"files": files}, status=status.HTTP_200_OK)
