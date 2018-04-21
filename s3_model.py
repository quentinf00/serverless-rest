import json
import boto3
import os
import uuid
from schema import Schema
import schema
from functools import wraps
import sys
import athena
import config

s3 = boto3.client('s3')


def handle_api_error(func):
    @wraps(func)
    def wraped_func(*args, **kwargs):
        try:
            return {
                'statusCode': 200,
                'body': json.dumps(func(*args, **kwargs)),
            }
        except Exception as e:

            return {
        'statusCode': 500,
        'body': str(e),
    }
    return wraped_func

class S3Model(object):
    SCHEMA = Schema(dict)
    name = 'raw'

    @classmethod
    def validate(self, obj):
        assert self.SCHEMA._schema == dict or type(self.SCHEMA._schema) == dict
        return self.SCHEMA.validate(obj)

    @classmethod
    def save(self, obj):
        object_id = obj.setdefault('id', str(uuid.uuid4()))
        obj = self.validate(obj)
        s3.put_object(
            Bucket=config.BUCKET,
            Key=f'{self.name}/{object_id}',
            Body=json.dumps(obj),
        )
        return obj

    @classmethod
    def load(self, object_id):
        obj = s3.get_object(
            Bucket=config.BUCKET,
            Key=f'{self.name}/{object_id}',
        )
        obj = json.loads(obj['Body'].read())
        return S3Model.validate(obj)

    @classmethod
    def delete_obj(self, object_id):
        s3.delete_object(
            Bucket=config.BUCKET,
            Key=f'{self.name}/{object_id}',
        )
        return {'deleted_id': object_id}

    @classmethod
    def list_ids(self):
        bucket_content = s3.list_objects_v2(Bucket=config.BUCKET)

        object_ids = [
            file_path['Key'].lstrip(f'{self.name}/')
            for file_path in bucket_content.get('Contents', [])
            if file_path['Size'] > 0
        ]

        return object_ids

    @classmethod
    def list_objs(self):

        objs = athena.get_results(f"""
            SELECT * FROM {config.DATABASE_NAME}.{self.name}
        """)

        return objs

    @staticmethod
    @handle_api_error
    def get(event, context):
        obj_id = event['pathParameters']['id']

        status_code = 200
        return S3Model.load(obj_id)

    @staticmethod
    @handle_api_error
    def put(event, context):
        obj_id = event['pathParameters']['id']
        obj = S3Model.load(obj_id)

        updates = json.loads(event['body'])
        obj.update(updates)

        return S3Model.save(obj)

    @staticmethod
    @handle_api_error
    def post(event, context):
        obj = json.loads(event['body'])
        return S3Model.save(obj)

    @staticmethod
    @handle_api_error
    def delete(event, context):
        obj_id = event['pathParameters']['id']
        return S3Model.delete_obj(obj_id)

    @staticmethod
    @handle_api_error
    def all(event, context):
        return S3Model.list_objs()

    @classmethod
    def get_api_methods(self):
        return self.get, self.post, self.put, self.delete, self.all

    @classmethod
    def get_athena_init_schema_handler(self):
        return athena.get_init_schema_handler(self)
