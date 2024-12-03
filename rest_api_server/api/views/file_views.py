from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.serializer.file_serializer import FileUploadSerializer
import grpc
import api.grpc.server_services_pb2 as server__services__pb2
import api.grpc.server_services_pb2_grpc as server__services__pb2_grpc
import os
from rest_api_server.settings import GRPC_HOST, GRPC_PORT
import logging

class FileUploadView(APIView):
    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data["file"]
            if not file:
                return Response({"error": "No file uploaded"}, status= status.HTTP_400_BAD_REQUEST)

            # Get MIME type using mimetypes
            file_name, file_extention = os.path.splitext(file.name)

            file_content = file.read()
            
            channel = grpc.insecure_channel(f"{GRPC_HOST}:{GRPC_PORT}")

            stub = server__services__pb2_grpc.SendFileServiceStub(channel)

            request = server__services__pb2.SendFileRequestBody(
                file_name= file_name,
                file_mime = file_extention,
                file = file_content
            )

            try:
                
                response = stub.SendFile(request)

                return Response({
                    "file_name": file_name,
                    "file_extention": file_extention
                }, status= status.HTTP_201_CREATED) 
            except grpc.RpcError as e:
                return Response({"error": f"gRPC call failed: {e.details()}"}, status= status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors,
                        status= status.HTTP_400_BAD_REQUEST)