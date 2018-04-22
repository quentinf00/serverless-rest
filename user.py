from s3_api_raw import S3ApiRaw
from s3_model import S3Model
from schema import Schema

class User(S3Model):
    name = 'user'
    SCHEMA = Schema({
        'id': str,
        'first_name': str,
        'last_name': str,
        'birthday': str,
    })

class UserResource(S3ApiRaw):
    s3_model_cls = User

get, post, put, delete, all = UserResource.get_api_methods()
init_schema = User.get_athena_init_schema_handler()
