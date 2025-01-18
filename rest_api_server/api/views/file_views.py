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

class GetSubXmlWarehouseView(APIView):
    def post(self, request):
        warehouse_name = request.data.get('warehouse_name')

        if not warehouse_name:
            warehouse_name = ''
        # Connect to the gRPC service
        channel = grpc.insecure_channel(f'{GRPC_HOST}:{GRPC_PORT}')
        stub = server_services_pb2_grpc.FileProcessingServiceStub(channel)
        xpath = f"//row[contains(translate(warehouse, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{warehouse_name.lower()}')]"        # Prepare gRPC request
        grpc_request = server_services_pb2.SubXmlRequest(
            xpath=xpath
        )

        # Send the request to the gRPC service and get the response
        try:
            response = stub.GetSubXml(grpc_request)
            return Response({"subxml_content": response.subxml_content}, status=status.HTTP_200_OK)
        except grpc.RpcError as e:
            return Response(
                {"error": f"gRPC call failed: {e.details()}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class GetSubXmPaymentMethodView(APIView):
    def post(self, request):
        payment = request.data.get('payment_method')

        if not payment:
            payment = ''
        # Connect to the gRPC service
        channel = grpc.insecure_channel(f'{GRPC_HOST}:{GRPC_PORT}')
        stub = server_services_pb2_grpc.FileProcessingServiceStub(channel)
        xpath = f"//row[contains(translate(payment, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{payment.lower()}')]"        # Prepare gRPC request
        grpc_request = server_services_pb2.SubXmlRequest(
            xpath=xpath
        )

        # Send the request to the gRPC service and get the response
        try:
            response = stub.GetSubXml(grpc_request)
            return Response({"subxml_content": response.subxml_content}, status=status.HTTP_200_OK)
        except grpc.RpcError as e:
            return Response(
                {"error": f"gRPC call failed: {e.details()}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class GetSubXmlProductLine(APIView):
    def post(self, request):
        product_line = request.data.get('product_line')

        if not product_line:
            product_line = ''
        # Connect to the gRPC service
        channel = grpc.insecure_channel(f'{GRPC_HOST}:{GRPC_PORT}')
        stub = server_services_pb2_grpc.FileProcessingServiceStub(channel)
        xpath = f"//row[contains(translate(product_line, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{product_line.lower()}')]"        # Prepare gRPC request
        grpc_request = server_services_pb2.SubXmlRequest(
            xpath=xpath
        )

        # Send the request to the gRPC service and get the response
        try:
            response = stub.GetSubXml(grpc_request)
            return Response({"subxml_content": response.subxml_content}, status=status.HTTP_200_OK)
        except grpc.RpcError as e:
            return Response(
                {"error": f"gRPC call failed: {e.details()}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )     
class FileUploadChunksView(APIView):
    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if not file:
            return Response({"error": "No file uploaded"}, status=400)
        # Connect to the gRPC service
        channel = grpc.insecure_channel(f'{GRPC_HOST}:{GRPC_PORT}')
        stub = server_services_pb2_grpc.SendFileServiceStub(channel)

        def generate_file_chunks(file, file_name, chunk_size=(64 * 1024)):
            try:
                while chunk := file.read(chunk_size):
                    yield server_services_pb2.SendFileChunksRequest(data=chunk, file_name=file_name)
            except Exception as e:
                print(f"Error reading file: {e}")
                raise # Let the exception propagate
        # Send file data to gRPC service
        try:
            response = stub.SendFileChunks(generate_file_chunks(file, file.name, (64 * 1024)))
            if response.success:
                return Response({"file_name": file.name}, status=status.HTTP_201_CREATED)
            return Response({"error": f": {response.message}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except grpc.RpcError as e:
            return Response({"error": f"gRPC call failed: {e.details()}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)