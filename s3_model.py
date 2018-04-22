import json
import boto3
import os
import uuid
from schema import Schema
import schema
import athena
import config

s3 = boto3.client('s3')

class S3Model(object):
    SCHEMA = Schema(dict)
    name = 'raw'

    @classmethod
    def get_name(cls):
        return cls.name

    @classmethod
    def validate(cls, obj):
        assert cls.SCHEMA._schema == dict or type(cls.SCHEMA._schema) == dict
        return cls.SCHEMA.validate(obj)

    @classmethod
    def save(cls, obj):
        object_id = obj.setdefault('id', str(uuid.uuid4()))
        obj = cls.validate(obj)
        s3.put_object(
            Bucket=config.BUCKET,
            Key=f'{cls.name}/{object_id}',
            Body=json.dumps(obj),
        )
        return obj

    @classmethod
    def load(cls, object_id):
        obj = s3.get_object(
            Bucket=config.BUCKET,
            Key=f'{cls.name}/{object_id}',
        )
        obj = json.loads(obj['Body'].read())
        return cls.validate(obj)

    @classmethod
    def delete_obj(cls, object_id):
        s3.delete_object(
            Bucket=config.BUCKET,
            Key=f'{cls.name}/{object_id}',
        )
        return {'deleted_id': object_id}

    @classmethod
    def list_ids(cls):
        bucket_content = s3.list_objects_v2(Bucket=config.BUCKET)

        object_ids = [
            file_path['Key'].lstrip(f'{cls.name}/')
            for file_path in bucket_content.get('Contents', [])
            if file_path['Size'] > 0
        ]

        return object_ids

    @classmethod
    def list_objs(cls):
        query =f"""
            SELECT * FROM {config.DATABASE_NAME}.{cls.name}
        """
        print(f'Running Query {query}')
        objs = athena.get_results(query)

        return objs


    @classmethod
    def get_athena_init_schema_handler(cls):
        return athena.get_init_schema_handler(cls)
