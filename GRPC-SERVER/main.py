from concurrent import futures
from settings import GRPC_SERVER_PORT, MAX_WORKERS, MEDIA_PATH, DBNAME, DBUSERNAME, DBPASSWORD, DBHOST, DBPORT
import os
import grpc
import logging
import server_Services_pb2
import server_Services_pb2_grpc
import pandas as pd
import pg8000
from lxml import etree

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("FileService")


def validate_csv(file_path):
    expected_columns = ['date', 'warehouse', 'client_type', 'product_line', 'quantity', 'unit_price', 'total', 'payment']
    df = pd.read_csv(file_path, encoding='ISO-8859-1')
    if list(df.columns) != expected_columns:
        raise ValueError(f"CSV file does not match the expected pattern.")
    return df


def save_csv_file(file_name, file_content):
    temp_csv_file_path = os.path.join(MEDIA_PATH, f"{file_name}_temp.csv")
    with open(temp_csv_file_path, 'wb') as f:
        f.write(file_content)
    
    try:
        # Validate the CSV content
        validate_csv(temp_csv_file_path)
        
        # If valid, rename the temporary file to the final file name
        csv_file_path = os.path.join(MEDIA_PATH, f"{file_name}.csv")
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
    xml_file_path = os.path.join(MEDIA_PATH, f"{os.path.basename(csv_file_path).replace('.csv', '.xml')}")
    with open(xml_file_path, 'w', encoding='utf-8') as xml_file:
        xml_file.write(xml_content)
    logger.info(f"XML file saved successfully: {xml_file_path}")
    return xml_content, xml_file_path

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

    # Create the tables if they don't exist
    create_files_table_query = """
        CREATE TABLE IF NOT EXISTS files (
            id SERIAL PRIMARY KEY,
            csv_path TEXT NOT NULL,
            xml_path TEXT NOT NULL
        );
    """
    cursor.execute(create_files_table_query)

    create_warehouse_table_query = """
        CREATE TABLE IF NOT EXISTS warehouse (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );
    """
    cursor.execute(create_warehouse_table_query)

    create_payment_table_query = """
        CREATE TABLE IF NOT EXISTS payment (
            id SERIAL PRIMARY KEY,
            method TEXT NOT NULL UNIQUE
        );
    """
    cursor.execute(create_payment_table_query)

    create_client_type_table_query = """
        CREATE TABLE IF NOT EXISTS client_type (
            id SERIAL PRIMARY KEY,
            type TEXT NOT NULL UNIQUE
        );
    """
    cursor.execute(create_client_type_table_query)

    create_product_line_table_query = """
        CREATE TABLE IF NOT EXISTS product_line (
            id SERIAL PRIMARY KEY,
            line TEXT NOT NULL UNIQUE
        );
    """
    cursor.execute(create_product_line_table_query)

    create_sales_table_query = """
        CREATE TABLE IF NOT EXISTS sales (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            warehouse_id INTEGER NOT NULL REFERENCES warehouse(id),
            client_type_id INTEGER NOT NULL REFERENCES client_type(id),
            product_line_id INTEGER NOT NULL REFERENCES product_line(id),
            quantity INTEGER NOT NULL,
            unit_price NUMERIC NOT NULL,
            total NUMERIC NOT NULL,
            payment_id INTEGER NOT NULL REFERENCES payment(id)
        );
    """
    cursor.execute(create_sales_table_query)

    # Insert file paths into the files table
    insert_files_query = """
        INSERT INTO files (csv_path, xml_path) VALUES (%s, %s);
    """
    cursor.execute(insert_files_query, (csv_file_path, xml_file_path))

    # Insert data into the warehouse, payment, client_type, and product_line tables and get their IDs
    warehouse_ids = {}
    payment_ids = {}
    client_type_ids = {}
    product_line_ids = {}

    for row in data:
        warehouse_name = row['warehouse']
        payment_method = row['payment']
        client_type = row['client_type']
        product_line = row['product_line']

        if warehouse_name not in warehouse_ids:
            cursor.execute("INSERT INTO warehouse (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id;", (warehouse_name,))
            warehouse_id = cursor.fetchone()
            if warehouse_id:
                warehouse_ids[warehouse_name] = warehouse_id[0]
            else:
                cursor.execute("SELECT id FROM warehouse WHERE name = %s;", (warehouse_name,))
                warehouse_ids[warehouse_name] = cursor.fetchone()[0]

        if payment_method not in payment_ids:
            cursor.execute("INSERT INTO payment (method) VALUES (%s) ON CONFLICT (method) DO NOTHING RETURNING id;", (payment_method,))
            payment_id = cursor.fetchone()
            if payment_id:
                payment_ids[payment_method] = payment_id[0]
            else:
                cursor.execute("SELECT id FROM payment WHERE method = %s;", (payment_method,))
                payment_ids[payment_method] = cursor.fetchone()[0]

        if client_type not in client_type_ids:
            cursor.execute("INSERT INTO client_type (type) VALUES (%s) ON CONFLICT (type) DO NOTHING RETURNING id;", (client_type,))
            client_type_id = cursor.fetchone()
            if client_type_id:
                client_type_ids[client_type] = client_type_id[0]
            else:
                cursor.execute("SELECT id FROM client_type WHERE type = %s;", (client_type,))
                client_type_ids[client_type] = cursor.fetchone()[0]

        if product_line not in product_line_ids:
            cursor.execute("INSERT INTO product_line (line) VALUES (%s) ON CONFLICT (line) DO NOTHING RETURNING id;", (product_line,))
            product_line_id = cursor.fetchone()
            if product_line_id:
                product_line_ids[product_line] = product_line_id[0]
            else:
                cursor.execute("SELECT id FROM product_line WHERE line = %s;", (product_line,))
                product_line_ids[product_line] = cursor.fetchone()[0]

    # Insert data into the sales table
    insert_sales_query = """
        INSERT INTO sales (date, warehouse_id, client_type_id, product_line_id, quantity, unit_price, total, payment_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    """
    for row in data:
        cursor.execute(insert_sales_query, (
            row['date'],
            warehouse_ids[row['warehouse']],
            client_type_ids[row['client_type']],
            product_line_ids[row['product_line']],
            row['quantity'],
            row['unit_price'],
            row['total'],
            payment_ids[row['payment']]
        ))

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