import logging
from django.http import JsonResponse
from rest_framework.views import APIView
from .schema import schema

# Configure logger
logging.basicConfig(level=logging.INFO)

class WarehousesView(APIView):
    def get(self, request):
        logging.info('Fetching all warehouses')
        query = '''
        {
            allWarehouses {
                id
                name
                latitude
                longitude
            }
        }
        '''
        result = schema.execute(
            query,
            context_value={'request': request}  # Include request in the context
        )

        if result.errors:
            return JsonResponse({'errors': [str(error) for error in result.errors]}, status=400)

        # Explicitly handle data serialization for safe JSON responses
        return JsonResponse(result.data or {}, safe=False)
    