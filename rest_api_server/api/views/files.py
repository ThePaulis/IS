from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection

        
class GetAllFiles(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, csv_file_path, xml_file_path FROM files")
            result = cursor.fetchall()
            files = [
                {
                    "id": row[0],
                    "csv_file_path": row[1],
                    "xml_file_path": row[2]
                }
                for row in result
            ]
        return Response({"files": files}, status=status.HTTP_200_OK)