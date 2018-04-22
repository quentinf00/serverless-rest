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
from s3_model import S3Model


def handle_api_error(func):
    @wraps(func)
    def wrapped_func(*args, **kwargs):
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
    return wrapped_func

class S3ApiRaw(object):
    s3_model_cls = S3Model

    @classmethod
    @handle_api_error
    def get(cls, event, context):
        obj_id = event['pathParameters']['id']
        return cls.s3_model_cls.load(obj_id)

    @classmethod
    @handle_api_error
    def put(cls, event, context):
        obj_id = event['pathParameters']['id']
        obj = cls.s3_model_cls.load(obj_id)

        updates = json.loads(event['body'])
        obj.update(updates)

        return cls.s3_model_cls.save(obj)

    @classmethod
    @handle_api_error
    def post(cls, event, context):
        obj = json.loads(event['body'])
        if 'id' in obj:
            raise Exception('Do not specify id in resource creation')
        return cls.s3_model_cls.save(obj)

    @classmethod
    @handle_api_error
    def delete(cls, event, context):
        obj_id = event['pathParameters']['id']
        return cls.s3_model_cls.delete_obj(obj_id)

    @classmethod
    @handle_api_error
    def all(cls, event, context):
        return cls.s3_model_cls.list_objs()

    @classmethod
    def get_api_methods(self):
        return self.get, self.post, self.put, self.delete, self.all

    @classmethod
    def get_athena_init_schema_handler(self):
        return athena.get_init_schema_handler(self)
