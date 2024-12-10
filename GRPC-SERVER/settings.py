import os

DBNAME = os.getenv('DBNAME', 'grpc')
DBUSERNAME = os.getenv('DBUSERNAME', 'postgres')
DBPASSWORD = os.getenv('DBPASSWORD', 'IS2002')
DBHOST = os.getenv('DBHOST', 'localhost')  
DBPORT = os.getenv('DBPORT', '5432')

GRPC_SERVER_PORT = os.getenv('GRPC_SERVER_PORT', '50052')
MAX_WORKERS = int(os.getenv('MAX_WORKERS', '10'))
MEDIA_PATH = os.getenv('MEDIA_PATH', f'{os.getcwd()}/app/media')
