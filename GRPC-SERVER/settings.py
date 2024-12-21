import os

DBNAME = os.getenv('DBNAME', 'grpc')
DBUSERNAME = os.getenv('DBUSERNAME', 'postgres')
DBPASSWORD = os.getenv('DBPASSWORD', 'IS2002')
DBHOST = os.getenv('DBHOST', 'localhost')  
DBPORT = os.getenv('DBPORT', '5432')
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", "5672")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "user")
RABBITMQ_PW = os.getenv("RABBITMQ_PW", "password")

GRPC_SERVER_HOST = os.getenv('GRPC_SERVER_HOST', 'localhost')
GRPC_SERVER_PORT = os.getenv('GRPC_SERVER_PORT', '50052')
MAX_WORKERS = int(os.getenv('MAX_WORKERS', '10'))
MEDIA_PATH = os.getenv('MEDIA_PATH', f'{os.getcwd()}/app/media')
