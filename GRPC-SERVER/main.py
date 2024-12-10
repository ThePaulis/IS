from concurrent import futures
from settings import GRPC_SERVER_PORT, MAX_WORKERS, MEDIA_PATH, DBNAME, DBUSERNAME, DBPASSWORD, DBHOST, DBPORT
import os
import grpc
import logging
import server_Services_pb2
import server_Services_pb2_grpc
import pandas as pd
import pg8000

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("FileService")


class FileProcessingService(server_Services_pb2_grpc.FileProcessingServiceServicer):
    def ConvertCsvToXml(self, request, context):
        try:
            # Save the uploaded CSV file
            csv_file_path = os.path.join(MEDIA_PATH, f"{request.file_name}.csv")
            with open(csv_file_path, 'wb') as f:
                f.write(request.file)

            logger.info(f"CSV file saved successfully: {csv_file_path}")

            # Read the CSV file into a DataFrame
            df = pd.read_csv(csv_file_path, encoding='ISO-8859-1')

            # Convert the DataFrame to XML
            xml_content = df.to_xml(root_name="data", row_name="row", index=False)

            # Save the XML content to a file
            xml_file_path = os.path.join(MEDIA_PATH, f"{request.file_name}.xml")
            with open(xml_file_path, 'w', encoding='utf-8') as xml_file:
                xml_file.write(xml_content)

            logger.info(f"XML file saved successfully: {xml_file_path}")

            # Save file paths to the database
            logger.info(f"Connecting to DB at {DBHOST}:{DBPORT}")
            conn = pg8000.connect(
                user=DBUSERNAME,
                password=DBPASSWORD,
                host=DBHOST,
                port=int(DBPORT),
                database=DBNAME
            )
            cursor = conn.cursor()

            # Create the files table if it doesn't exist
            create_table_query = """
                CREATE TABLE IF NOT EXISTS files (
                    id SERIAL PRIMARY KEY,
                    csv_file_path TEXT NOT NULL,
                    xml_file_path TEXT NOT NULL
                );
            """
            cursor.execute(create_table_query)

            # Insert file paths into the table
            insert_query = """
                INSERT INTO files (csv_file_path, xml_file_path) VALUES (%s, %s);
            """
            cursor.execute(insert_query, (csv_file_path, xml_file_path))

            conn.commit()
            conn.close()

            logger.info("Database operations completed successfully.")

            return server_Services_pb2.CsvToXmlResponse(xml_content=xml_content)

        except Exception as e:
            logger.error(f"Error during CSV to XML conversion: {str(e)}", exc_info=True)
            context.set_details(f"Error during CSV to XML conversion: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_Services_pb2.CsvToXmlResponse(xml_content="")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS))
    server_Services_pb2_grpc.add_FileProcessingServiceServicer_to_server(FileProcessingService(), server)

    server.add_insecure_port(f"[::]:{GRPC_SERVER_PORT}")
    logger.info(f"Starting server on port {GRPC_SERVER_PORT}")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    os.makedirs(MEDIA_PATH, exist_ok=True)
    serve()
