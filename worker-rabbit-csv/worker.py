import pika
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

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger()
reassembled_data = []


def handle_invalid_dates_as_strings(df):
    df['birth_date'] = pd.to_datetime(df['birth_date'], errors='coerce').dt.strftime('%Y-%m-%d')
    df['birth_date'] = df['birth_date'].apply(lambda x: 'Invalid Date' if x == 'NaT' else x)

    return df

def save_csv_to_db(data):
    conn = pg8000.connect(user=DBUSERNAME, password=DBPASSWORD, database=DBNAME, host=DBHOST, port=DBPORT)
    cursor = conn.cursor()

    create_players_table_query = """
        CREATE TABLE IF NOT EXISTS players (
            id SERIAL PRIMARY KEY,
            name TEXT,
            full_name TEXT,
            birth_date TEXT,  
            age TEXT,
            height_cm TEXT,
            weight_kgs TEXT,
            positions TEXT,
            nationality TEXT,
            overall_rating TEXT,
            potential TEXT,
            value_euro TEXT,
            wage_euro TEXT,
            preferred_foot TEXT,
            international_reputation TEXT,
            weak_foot TEXT,
            skill_moves TEXT,
            body_type TEXT,
            release_clause_euro TEXT,
            national_team TEXT,
            national_rating TEXT,
            national_team_position TEXT,
            national_jersey_number TEXT,
            crossing TEXT,
            finishing TEXT,
            heading_accuracy TEXT,
            short_passing TEXT,
            volleys TEXT,
            dribbling TEXT,
            curve TEXT,
            freekick_accuracy TEXT,
            long_passing TEXT,
            ball_control TEXT,
            acceleration TEXT,
            sprint_speed TEXT,
            agility TEXT,
            reactions TEXT,
            balance TEXT,
            shot_power TEXT,
            jumping TEXT,
            stamina TEXT,
            strength TEXT,
            long_shots TEXT,
            aggression TEXT,
            interceptions TEXT,
            positioning TEXT,
            vision TEXT,
            penalties TEXT,
            composure TEXT,
            marking TEXT,
            standing_tackle TEXT,
            sliding_tackle TEXT
        );
    """
    cursor.execute(create_players_table_query)

    insert_players_query = """
        INSERT INTO players (
            name, full_name, birth_date, age, height_cm, weight_kgs, positions, nationality, overall_rating, potential,
            value_euro, wage_euro, preferred_foot, international_reputation, weak_foot, skill_moves, body_type,
            release_clause_euro, national_team, national_rating, national_team_position, national_jersey_number,
            crossing, finishing, heading_accuracy, short_passing, volleys, dribbling, curve, freekick_accuracy,
            long_passing, ball_control, acceleration, sprint_speed, agility, reactions, balance, shot_power, jumping,
            stamina, strength, long_shots, aggression, interceptions, positioning, vision, penalties, composure,
            marking, standing_tackle, sliding_tackle
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s
        );
    """

    for _, row in data.iterrows():

        cursor.execute(insert_players_query, (
            row['name'],
            row['full_name'],
            row['birth_date'],
            row['age'],
            row['height_cm'],
            row['weight_kgs'],
            row['positions'],
            row['nationality'],
            row['overall_rating'],
            row['potential'],
            row['value_euro'],
            row['wage_euro'],
            row['preferred_foot'],
            row['international_reputation'],
            row['weak_foot'],
            row['skill_moves'],
            row['body_type'],
            row['release_clause_euro'],
            row['national_team'],
            row['national_rating'],
            row['national_team_position'],
            row['national_jersey_number'],
            row['crossing'],
            row['finishing'],
            row['heading_accuracy'],
            row['short_passing'],
            row['volleys'],
            row['dribbling'],
            row['curve'],
            row['freekick_accuracy'],
            row['long_passing'],
            row['ball_control'],
            row['acceleration'],
            row['sprint_speed'],
            row['agility'],
            row['reactions'],
            row['balance'],
            row['shot_power'],
            row['jumping'],
            row['stamina'],
            row['strength'],
            row['long_shots'],
            row['aggression'],
            row['interceptions'],
            row['positioning'],
            row['vision'],
            row['penalties'],
            row['composure'],
            row['marking'],
            row['standing_tackle'],
            row['sliding_tackle']
        ))

    conn.commit()
    cursor.close()
    conn.close()


def process_message(ch, method, properties, body):
    str_stream = body.decode('utf-8')
    if str_stream == "__EOF__":
        print("EOF marker received. Finalizing...")
        file_content = b"".join(reassembled_data)
        csv_text = file_content.decode('utf-8')
        if len(reassembled_data) > 1:
            csvfile = StringIO(csv_text)
            df = pd.read_csv(csvfile)
            print(df)
            df = handle_invalid_dates_as_strings(df)
            save_csv_to_db(df)
            reassembled_data.clear()
    else:
        print(body)
        reassembled_data.append(body)


def main():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PW)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=process_message, auto_ack=True)
    logger.info("Waiting for messages...")
    channel.start_consuming()


if __name__ == '__main__':
    main()