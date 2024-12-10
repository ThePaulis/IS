from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers.file_serializer import FileUploadSerializer
import grpc
import api.grpc.server_Services_pb2 as server_services_pb2
import api.grpc.server_Services_pb2_grpc as server_services_pb2_grpc
import os

from rest_api_server.settings import GRPC_PORT, GRPC_HOST

class FileUploadView(APIView):
    def post(self, request):
        # Serialize the incoming request data (the file)
        serializer = FileUploadSerializer(data=request.data)

        if serializer.is_valid():
            file = serializer.validated_data['file']

            if not file:
                return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

            # Extract file name and extension
            file_name, file_extension = os.path.splitext(file.name)

            # Read the file content as bytes
            file_content = file.read()

            # Connect to the gRPC service
            channel = grpc.insecure_channel(f'{GRPC_HOST}:{GRPC_PORT}')
            stub = server_services_pb2_grpc.FileProcessingServiceStub(channel)

            # Prepare gRPC request
            grpc_request = server_services_pb2.FileRequest(
                file_name=file_name,  # Send the file name
                file=file_content      # Send the binary file content
            )

            # Send the file data to the gRPC service and get the response
            try:
                response = stub.ConvertCsvToXml(grpc_request)

                # Assuming the response contains the converted XML content
                return Response({
                    "file_name": file_name,
                    "file_extension": file_extension,
                    "converted_xml": response.xml_content  # Return the converted XML content
                }, status=status.HTTP_201_CREATED)

            except grpc.RpcError as e:
                return Response(
                    {"error": f"gRPC call failed: {e.details()}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
