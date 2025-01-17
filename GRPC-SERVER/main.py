from concurrent import futures
from settings import GRPC_SERVER_PORT, MAX_WORKERS, MEDIA_PATH, DBNAME, DBUSERNAME, DBPASSWORD, DBHOST, DBPORT, RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PW
import os
import grpc
import logging
import server_Services_pb2
import server_Services_pb2_grpc
import pandas as pd
import pg8000
from lxml import etree
import pika
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("FileService")

    
def validate_csv(file_path):
    expected_columns = ['date', 'warehouse', 'client_type', 'product_line', 'quantity', 'unit_price', 'total', 'payment']
    df = pd.read_csv(file_path, encoding='ISO-8859-1')
    if list(df.columns) != expected_columns:
        raise ValueError(f"CSV file does not match the expected pattern.")
    return df

def validate_xml_content(xml_content):
    xml_tree = etree.fromstring(xml_content.encode('utf-8'))
    with open("schema.xsd", 'r', encoding='utf-8') as schema_file:
        schema_content = schema_file.read()
    xml_schema = etree.XMLSchema(etree.fromstring(schema_content.encode('utf-8')))
    if not xml_schema.validate(xml_tree):
        raise ValueError(f"XML content does not match the expected schema.")
    return xml_tree

def save_csv_file(file_name, file_content):
    temp_csv_file_path = os.path.join(MEDIA_PATH, f"{file_name}_temp.csv")
    with open(temp_csv_file_path, 'wb') as f:
        f.write(file_content)
    
    try:
        # Validate the CSV content
        validate_csv(temp_csv_file_path)
        
        # If valid, rename the temporary file to the final file name
        csv_file_path = os.path.join(MEDIA_PATH, f"{file_name}")
        os.rename(temp_csv_file_path, csv_file_path)
        logger.info(f"CSV file saved successfully: {csv_file_path}")
        return csv_file_path
    except ValueError as e:
        # If invalid, delete the temporary file
        os.remove(temp_csv_file_path)
        logger.error(f"CSV file validation failed: {str(e)}")
        raise

def convert_csv_to_xml(csv_file_path):
    df = validate_csv(csv_file_path)
    xml_content = df.to_xml(root_name="data", row_name="row", index=False)
    validate_xml_content(xml_content)
    xml_path = save_xml_file(xml_content, csv_file_path)
    return xml_content, xml_path

def save_xml_file(xml_content, csv_file_path):
    xml_file_path = os.path.join(MEDIA_PATH, f"{os.path.basename(csv_file_path).replace('.csv', '.xml')}")
    with open(xml_file_path, 'w', encoding='utf-8') as xml_file:
        xml_file.write(xml_content)
    logger.info(f"XML file saved successfully: {xml_file_path}")
    return xml_file_path

def parse_xml(xml_content):
    xml_tree = etree.fromstring(xml_content.encode('utf-8'))
    rows = xml_tree.xpath('//row')
    data = []
    for row in rows:
        data.append({
            'date': row.xpath('date/text()')[0],
            'warehouse': row.xpath('warehouse/text()')[0],
            'client_type': row.xpath('client_type/text()')[0],
            'product_line': row.xpath('product_line/text()')[0],
            'quantity': int(row.xpath('quantity/text()')[0]),
            'unit_price': float(row.xpath('unit_price/text()')[0]),
            'total': float(row.xpath('total/text()')[0]),
            'payment': row.xpath('payment/text()')[0]
        })
    return data

def save_data_to_db(csv_file_path, xml_file_path):
    logger.info(f"Connecting to DB at {DBHOST}:{DBPORT}")
    conn = pg8000.connect(
        user=DBUSERNAME,
        password=DBPASSWORD,
        host=DBHOST,
        port=int(DBPORT),
        database=DBNAME
    )
    cursor = conn.cursor()

    # Create the tables if they don't exist
    create_files_table_query = """
        CREATE TABLE IF NOT EXISTS files (
            id SERIAL PRIMARY KEY,
            csv_path TEXT NOT NULL,
            xml_path TEXT NOT NULL
        );
    """
    cursor.execute(create_files_table_query)

    # Insert file paths into the files table
    insert_files_query = """
        INSERT INTO files (csv_path, xml_path) VALUES (%s, %s);
    """
    cursor.execute(insert_files_query, (csv_file_path, xml_file_path))
    conn.commit()
    conn.close()
    logger.info("Database operations completed successfully.")


class FileProcessingService(server_Services_pb2_grpc.FileProcessingServiceServicer):
    def ConvertCsvToXml(self, request, context):
        try:
            csv_file_path = save_csv_file(request.file_name, request.file)
            xml_content, xml_file_path = convert_csv_to_xml(csv_file_path)
            save_data_to_db(csv_file_path, xml_file_path)
            return server_Services_pb2.CsvToXmlResponse(xml_content=xml_content)
        except Exception as e:
            logger.error(f"Error during CSV to XML conversion: {str(e)}", exc_info=True)
            context.set_details(f"Error during CSV to XML conversion: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_Services_pb2.CsvToXmlResponse(xml_content="")

    def GetSubXml(self, request, context):
        try:
            conn = pg8000.connect(
                user=DBUSERNAME,
                password=DBPASSWORD,
                host=DBHOST,
                port=int(DBPORT),
                database=DBNAME
            )
            cursor = conn.cursor()
            cursor.execute("SELECT xml_path FROM files")
            results = cursor.fetchall()
            if not results:
                context.set_details("No files found")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return server_Services_pb2.SubXmlResponse(subxml_content="")

            subxml_content = ""
            for result in results:
                xml_file_path = result[0]
                with open(xml_file_path, 'r', encoding='utf-8') as xml_file:
                    xml_content = xml_file.read()

                xml_tree = etree.fromstring(xml_content.encode('utf-8'))
                subxml_tree = xml_tree.xpath(f"{request.xpath}")
                if isinstance(subxml_tree, list):
                    subxml_content += ''.join([etree.tostring(element, pretty_print=True, encoding='utf-8').decode('utf-8') for element in subxml_tree])
                else:
                    subxml_content += etree.tostring(subxml_tree, pretty_print=True, encoding='utf-8').decode('utf-8')

            return server_Services_pb2.SubXmlResponse(subxml_content=subxml_content)
        except Exception as e:
            logger.error(f"Error during GetSubXml: {str(e)}", exc_info=True)
            context.set_details(f"Error during GetSubXml: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_Services_pb2.SubXmlResponse(subxml_content="")


class SendFileService(server_Services_pb2_grpc.SendFileServiceServicer):
    def SendFileChunks(self, request_iterator, context):
        try:
            rabbit_connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PW)))
            rabbit_channel = rabbit_connection.channel()
            logging.info("Connected to RabbitMQ")
            rabbit_channel.queue_declare(queue='csv_chunks')
            os.makedirs(MEDIA_PATH, exist_ok=True)
            file_name = None
            file_chunks = [] # Store all chunks in memory
            
            for chunk in request_iterator:
                if not file_name:
                    file_name = chunk.file_name
            
                # Collect the file data chunks
                file_chunks.append(chunk.data)
            
                # Send data chunk to the worker
                rabbit_channel.basic_publish(exchange='', routing_key='csv_chunks', body=chunk.data)
            
            # Send info that the file stream ended
            rabbit_channel.basic_publish(exchange='', routing_key='csv_chunks', body="__EOF__")
            
            # Combine all chunks into a single bytes object
            file_content = b"".join(file_chunks)
            file_path = os.path.join(MEDIA_PATH, file_name)
            logging.info(f"Received file: {file_path}")
            # Write the collected data to the file at the end
            save_csv_file(file_path, file_content)
            xml_content, xml_file_path = convert_csv_to_xml(file_path)
            save_data_to_db(file_path, xml_file_path)
            
            return server_Services_pb2.SendFileChunksResponse(success=True, message='File imported')
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            return server_Services_pb2.SendFileChunksResponse(success=False, message=str(e))

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS))
    server_Services_pb2_grpc.add_FileProcessingServiceServicer_to_server(FileProcessingService(), server)
    server_Services_pb2_grpc.add_SendFileServiceServicer_to_server(SendFileService(), server)

    server.add_insecure_port(f"[::]:{GRPC_SERVER_PORT}")
    logger.info(f"Starting server on port {GRPC_SERVER_PORT}")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    os.makedirs(MEDIA_PATH, exist_ok=True)
    serve()