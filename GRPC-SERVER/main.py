from concurrent import futures
from settings import GRPC_SERVER_PORT, MAX_WORKERS, MEDIA_PATH, DBNAME, DBUSERNAME, DBPASSWORD, DBHOST, DBPORT, \
    RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PW
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
    expected_columns = [
        'name', 'full_name', 'birth_date', 'age', 'height_cm', 'weight_kgs',
        'positions', 'nationality', 'overall_rating', 'potential', 'value_euro',
        'wage_euro', 'preferred_foot', 'international_reputation', 'weak_foot',
        'skill_moves', 'body_type', 'release_clause_euro', 'national_team',
        'national_rating', 'national_team_position', 'national_jersey_number',
        'crossing', 'finishing', 'heading_accuracy', 'short_passing', 'volleys',
        'dribbling', 'curve', 'freekick_accuracy', 'long_passing', 'ball_control',
        'acceleration', 'sprint_speed', 'agility', 'reactions', 'balance', 'shot_power',
        'jumping', 'stamina', 'strength', 'long_shots', 'aggression', 'interceptions',
        'positioning', 'vision', 'penalties', 'composure', 'marking', 'standing_tackle',
        'sliding_tackle'
    ]

    df = pd.read_csv(file_path, encoding='ISO-8859-1')

    if list(df.columns) != expected_columns:
        raise ValueError(f"CSV file does not match the expected columns.")

    return df


def save_csv_file(file_name, file_content):
    temp_csv_file_path = os.path.join(MEDIA_PATH, f"{file_name}_temp.csv")
    with open(temp_csv_file_path, 'wb') as f:
        f.write(file_content)

    try:
        validate_csv(temp_csv_file_path)

        csv_file_path = os.path.join(MEDIA_PATH, f"{file_name}.csv")
        os.rename(temp_csv_file_path, csv_file_path)
        logger.info(f"CSV file saved successfully: {csv_file_path}")
        return csv_file_path
    except ValueError as e:
        os.remove(temp_csv_file_path)
        logger.error(f"CSV file validation failed: {str(e)}")
        raise


def convert_csv_to_xml(csv_file_path):
    df = validate_csv(csv_file_path)

    xml_content = df.to_xml(root_name="players", row_name="player", index=False)

    xml_file_path = os.path.join(MEDIA_PATH, f"{os.path.basename(csv_file_path).replace('.csv', '.xml')}")

    with open(xml_file_path, 'w', encoding='utf-8') as xml_file:
        xml_file.write(xml_content)

    logger.info(f"XML file saved successfully: {xml_file_path}")
    return xml_content, xml_file_path


def parse_xml(xml_content):
    xml_tree = etree.fromstring(xml_content.encode('utf-8'))
    players = xml_tree.xpath('//player')
    data = []

    for player in players:
        positions = player.xpath('positions/text()')[0].split(",")  # Handle comma-separated positions
        data.append({
            'name': player.xpath('name/text()')[0],
            'full_name': player.xpath('full_name/text()')[0],
            'birth_date': player.xpath('birth_date/text()')[0],
            'age': int(player.xpath('age/text()')[0]),
            'height_cm': float(player.xpath('height_cm/text()')[0]),
            'weight_kgs': float(player.xpath('weight_kgs/text()')[0]),
            'positions': positions,
            'nationality': player.xpath('nationality/text()')[0],
            'overall_rating': int(player.xpath('overall_rating/text()')[0]),
            'potential': int(player.xpath('potential/text()')[0]),
            'value_euro': float(player.xpath('value_euro/text()')[0]),
            'wage_euro': float(player.xpath('wage_euro/text()')[0]),
        })

    return data


def save_data_to_db(data, csv_file_path, xml_file_path):
    logger.info(f"Connecting to DB at {DBHOST}:{DBPORT}")
    conn = pg8000.connect(
        user=DBUSERNAME,
        password=DBPASSWORD,
        host=DBHOST,
        port=int(DBPORT),
        database=DBNAME
    )
    cursor = conn.cursor()

    create_files_table_query = """
        CREATE TABLE IF NOT EXISTS files (
            id SERIAL PRIMARY KEY,
            csv_path TEXT NOT NULL,
            xml_path TEXT NOT NULL
        );
    """
    cursor.execute(create_files_table_query)

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
            data = parse_xml(xml_content)
            save_data_to_db(data, csv_file_path, xml_file_path)
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
            cursor.execute("SELECT xml_path FROM files WHERE id = %s", (request.file_id,))
            result = cursor.fetchone()
            if not result:
                context.set_details(f"File with ID {request.file_id} not found")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return server_Services_pb2.SubXmlResponse(subxml_content="")

            xml_file_path = result[0]
            with open(xml_file_path, 'r', encoding='utf-8') as xml_file:
                xml_content = xml_file.read()

            xml_tree = etree.fromstring(xml_content.encode('utf-8'))
            subxml_tree = xml_tree.xpath(f"//row[warehouse='{request.warehouse_name}']")
            subxml_content = etree.tostring(subxml_tree, pretty_print=True, encoding='utf-8').decode('utf-8')

            return server_Services_pb2.SubXmlResponse(subxml_content=subxml_content)
        except Exception as e:
            logger.error(f"Error during GetSubXml: {str(e)}", exc_info=True)
            context.set_details(f"Error during GetSubXml: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_Services_pb2.SubXmlResponse(subxml_content="")


class SendFileService(server_Services_pb2_grpc.SendFileServiceServicer):
    def SendFileChunks(self, request_iterator, context):
        try:
            rabbit_connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT,
                                          credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PW)))
            rabbit_channel = rabbit_connection.channel()
            rabbit_channel.queue_declare(queue='csv_chunks')
            os.makedirs(MEDIA_PATH, exist_ok=True)
            file_name = None
            file_chunks = []  # Store all chunks in memory

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

            # Write the collected data to the file at the end
            with open(file_path, "wb") as f:
                f.write(file_content)

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
