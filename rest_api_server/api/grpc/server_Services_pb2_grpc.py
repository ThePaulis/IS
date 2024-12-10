# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import api.grpc.server_Services_pb2 as server__Services__pb2

GRPC_GENERATED_VERSION = '1.68.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in server_Services_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class FileProcessingServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ConvertCsvToXml = channel.unary_unary(
                '/server_services.FileProcessingService/ConvertCsvToXml',
                request_serializer=server__Services__pb2.FileRequest.SerializeToString,
                response_deserializer=server__Services__pb2.CsvToXmlResponse.FromString,
                _registered_method=True)


class FileProcessingServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def ConvertCsvToXml(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_FileProcessingServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'ConvertCsvToXml': grpc.unary_unary_rpc_method_handler(
                    servicer.ConvertCsvToXml,
                    request_deserializer=server__Services__pb2.FileRequest.FromString,
                    response_serializer=server__Services__pb2.CsvToXmlResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'server_services.FileProcessingService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('server_services.FileProcessingService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class FileProcessingService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def ConvertCsvToXml(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/server_services.FileProcessingService/ConvertCsvToXml',
            server__Services__pb2.FileRequest.SerializeToString,
            server__Services__pb2.CsvToXmlResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
