from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
        
class GetAllSales(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE VIEW sales_view AS
                SELECT 
                    s.id, s.date, s.total,
                    w.name AS warehouse,
                    c.type AS client_type,
                    p.line AS product_line,
                    s.quantity, s.unit_price,
                    pm.method AS payment
                FROM sales s
                JOIN warehouse w ON s.warehouse_id = w.id
                JOIN client_type c ON s.client_type_id = c.id
                JOIN product_line p ON s.product_line_id = p.id
                JOIN payment pm ON s.payment_id = pm.id;    

                """)
            cursor.execute("SELECT * FROM sales_view")
            result = cursor.fetchall()
            sales = [
                {
                    "id": row[0],
                    "date": row[1],
                    "warehouse": row[2],
                    "client_type": row[3],
                    "product_line": row[4],
                    "quantity": row[5],
                    "unit_price": row[6],
                    "total": row[7],
                    "payment": row[8]
                }
                for row in result
            ]
        return Response({"sales": sales}, status=status.HTTP_200_OK)