import pika
import json
import os
import logging
from io import StringIO
import pandas as pd
import pg8000

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", "5672")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "user")
RABBITMQ_PW = os.getenv("RABBITMQ_PW", "password")
QUEUE_NAME = 'csv_chunks'
DBHOST = os.getenv('DBHOST', 'localhost')
DBUSERNAME = os.getenv('DBUSERNAME', 'myuser')
DBPASSWORD = os.getenv('DBPASSWORD', 'mypassword')
DBNAME = os.getenv('DBNAME', 'mydatabase')
DBPORT = os.getenv('DBPORT', '5432')

# Configure logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger()
reassembled_data = []  # Declare reassembled_data at the module level

def save_csv_to_db(data):
    conn = pg8000.connect(user=DBUSERNAME, password=DBPASSWORD, database=DBNAME, host=DBHOST, port=DBPORT)
    cursor = conn.cursor()

    create_warehouse_table_query = """
        CREATE TABLE IF NOT EXISTS warehouse (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            latitude NUMERIC,
            longitude NUMERIC
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

    # Insert data into the warehouse, payment, client_type, and product_line tables and get their IDs
    warehouse_ids = {}
    payment_ids = {}
    client_type_ids = {}
    product_line_ids = {}

    # Hardcoded latitude and longitude values for the warehouses
    warehouse_locations = {
        'Central': {'latitude': 39.8283, 'longitude': -98.5795},  # Geographic center of the contiguous United States
        'North': {'latitude': 47.6062, 'longitude': -122.3321},  # Seattle, WA
        'West': {'latitude': 34.0522, 'longitude': -118.2437},    # Los Angeles, CA
        'East': {'latitude': 40.7128, 'longitude': -74.0060},     # New York City, NY
        'South': {'latitude': 29.7604, 'longitude': -95.3698},    # Houston, TX
    }

    for _, row in data.iterrows():
        warehouse_name = row['warehouse']
        payment_method = row['payment']
        client_type = row['client_type']
        product_line = row['product_line']

        if warehouse_name not in warehouse_ids:
            cursor.execute(
                "INSERT INTO warehouse (name, latitude, longitude) VALUES (%s, %s, %s) ON CONFLICT (name) DO NOTHING RETURNING id;",
                (warehouse_name, warehouse_locations[warehouse_name]['latitude'], warehouse_locations[warehouse_name]['longitude'])
            )
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
    for _, row in data.iterrows():
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
    cursor.close()
    conn.close()

def process_message(ch, method, properties, body):
    # body is a CSV chunk.
    str_stream = body.decode('utf-8')
    if str_stream == "__EOF__":
        print("EOF marker received. Finalizing...")
        file_content = b"".join(reassembled_data)
        csv_text = file_content.decode('utf-8')
        if len(reassembled_data) > 1:
            csvfile = StringIO(csv_text)
            df = pd.read_csv(csvfile)
            print(df)
            save_csv_to_db(df)
            reassembled_data.clear()  # Clear the list after processing
    else:
        print(body)
        reassembled_data.append(body)

def main():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PW)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=process_message, auto_ack=True)
    logger.info("Waiting for messages...")
    channel.start_consuming()

if __name__ == '__main__':
    main()