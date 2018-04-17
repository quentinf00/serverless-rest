import os

ATHENA_BUCKET = os.getenv('ATHENA_BUCKET', 'bucket')
BUCKET = os.getenv('BUCKET', 'bucket')
DATABASE_NAME = 'myathenadb'