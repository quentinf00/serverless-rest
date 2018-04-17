from s3_model import S3Model
from schema import Schema

class User(S3Model):
    SCHEMA = Schema({
        'id': str,
        'first_name': str,
        'last_name': str,
        'birthday': str,
    })

get, post, put, delete, all = User.get_api_methods()
init_schema = User.get_athena_init_schema_handler()