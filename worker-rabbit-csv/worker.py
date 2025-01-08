import pika
import json
import os
import logging
from io import StringIO
import pandas as pd
import pg8000
from datetime import datetime

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

# Configure
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger()
reassembled_data = []

def save_csv_to_db(data):
    """
    Save the processed player data into the PostgreSQL database.
    """
    conn = pg8000.connect(user=DBUSERNAME, password=DBPASSWORD, database=DBNAME, host=DBHOST, port=DBPORT)
    cursor = conn.cursor()

    # Create tables for normalized data storage (same as before)

    # Clean and prepare data
    data['birth_date'] = pd.to_datetime(data['birth_date'], errors='coerce').dt.date

    # Define default fill values for each column type
    fill_values = {
        'name': "",
        'full_name': "",
        'birth_date': None,  # None will handle the date columns
        'age': 0,
        'height_cm': 0,
        'weight_kgs': 0,
        'nationality': "",
        'preferred_foot': "",
        'international_reputation': 0,
        'weak_foot': 0,
        'skill_moves': 0,
        'body_type': "",
        'release_clause_euro': 0,
        'overall_rating': 0,
        'potential': 0,
        'national_rating': 0,
        'national_team': "",
        'national_team_position': "",
        'national_jersey_number': 0,
        'crossing': 0,
        'finishing': 0,
        'heading_accuracy': 0,
        'short_passing': 0,
        'volleys': 0,
        'dribbling': 0,
        'curve': 0,
        'freekick_accuracy': 0,
        'long_passing': 0,
        'ball_control': 0,
        'acceleration': 0,
        'sprint_speed': 0,
        'agility': 0,
        'reactions': 0,
        'balance': 0,
        'shot_power': 0,
        'jumping': 0,
        'stamina': 0,
        'strength': 0,
        'long_shots': 0,
        'aggression': 0,
        'interceptions': 0,
        'positioning': 0,
        'vision': 0,
        'penalties': 0,
        'composure': 0,
        'marking': 0,
        'standing_tackle': 0,
        'sliding_tackle': 0
    }

    # Fill missing values with specified defaults
    data.fillna(fill_values, inplace=True)

    # Insert data into tables
    for _, row in data.iterrows():
        # Skip rows with missing required fields (e.g., 'name' should never be empty)
        if pd.isna(row['name']) or row['name'] == "":
            logger.warning("Skipping row with missing 'name'.")
            continue

        # Insert into `player` table
        cursor.execute("""
            INSERT INTO player (
                name, full_name, birth_date, age, height_cm, weight_kgs, nationality, preferred_foot,
                international_reputation, weak_foot, skill_moves, body_type, release_clause_euro
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (name) DO NOTHING
            RETURNING id;
        """, (
            row['name'], row['full_name'], row['birth_date'], row['age'], row['height_cm'], row['weight_kgs'],
            row['nationality'], row['preferred_foot'], row['international_reputation'], row['weak_foot'],
            row['skill_moves'], row['body_type'], row['release_clause_euro']
        ))

        player_id = cursor.fetchone()
        if not player_id:
            cursor.execute("SELECT id FROM player WHERE name = %s;", (row['name'],))
            player_id = cursor.fetchone()[0]
        else:
            player_id = player_id[0]

        # Insert into `rating` table
        cursor.execute("""
            INSERT INTO rating (player_id, overall_rating, potential, national_rating)
            VALUES (%s, %s, %s, %s);
        """, (player_id, row['overall_rating'], row['potential'], row['national_rating']))

        # Insert into `team` table
        cursor.execute("""
            INSERT INTO team (player_id, national_team, national_team_position, national_jersey_number)
            VALUES (%s, %s, %s, %s);
        """, (player_id, row['national_team'], row['national_team_position'], row['national_jersey_number']))

        # Insert into `attributes` table
        cursor.execute("""
            INSERT INTO attributes (
                player_id, crossing, finishing, heading_accuracy, short_passing, volleys, dribbling, curve,
                freekick_accuracy, long_passing, ball_control, acceleration, sprint_speed, agility, reactions,
                balance, shot_power, jumping, stamina, strength, long_shots, aggression, interceptions, positioning,
                vision, penalties, composure, marking, standing_tackle, sliding_tackle
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (
            player_id, row['crossing'], row['finishing'], row['heading_accuracy'], row['short_passing'], row['volleys'],
            row['dribbling'], row['curve'], row['freekick_accuracy'], row['long_passing'], row['ball_control'],
            row['acceleration'], row['sprint_speed'], row['agility'], row['reactions'], row['balance'], row['shot_power'],
            row['jumping'], row['stamina'], row['strength'], row['long_shots'], row['aggression'], row['interceptions'],
            row['positioning'], row['vision'], row['penalties'], row['composure'], row['marking'], row['standing_tackle'],
            row['sliding_tackle']
        ))

    conn.commit()
    cursor.close()
    conn.close()


def process_message(ch, method, properties, body):
    """
    Process incoming RabbitMQ message containing CSV chunks.
    """
    global reassembled_data
    if body.decode('utf-8') == "__EOF__":
        csv_data = b"".join(reassembled_data).decode('utf-8')
        df = pd.read_csv(StringIO(csv_data))
        save_csv_to_db(df)
        reassembled_data = []  # Clear for the next file
    else:
        reassembled_data.append(body)

def main():
    """
    Main RabbitMQ consumer loop.
    """
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PW)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials)
    )
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=process_message, auto_ack=True)
    logger.info("Waiting for messages...")
    channel.start_consuming()

if __name__ == '__main__':
    main()
