import json
import boto3
import os
import uuid
import datetime
from schema import Schema
from functools import wraps
import sys

BUCKET = os.getenv('BUCKET', 'bucket')
s3 = boto3.client('s3')


def handle_api_error(func):
    @wraps(func)
    def wraped_func(*args, **kwargs):
        try:
            return {
                'statusCode': 200,
                'body': json.dumps(func(*args, **kwargs))
            }
        except Exception as e:
            print(sys.exc_info())

            return {
        'statusCode': 500,
        'body': str(e),
    }
    return wraped_func


@handle_api_error
def get(event, context):
    print(event)
    user_id = event['pathParameters']['id']

    status_code = 200
    return User.load(user_id)


@handle_api_error
def put(event, context):
    print(event)
    user_id = event['pathParameters']['id']
    user = User.load(user_id)

    updates = json.loads(event['body'])
    user.update(updates)

    return User.save(user)



@handle_api_error
def post(event, context):
    print(event)
    user = json.loads(event['body'])
    return User.save(user)



@handle_api_error
def delete(event, context):
    print(event)
    user_id = event['pathParameters']['id']

    return User.delete(user_id)


@handle_api_error
def list(event, context):
    print(event)
    return [
        User.load(user_id)
        for user_id in User.list_ids()
    ]


class User(object):
    @staticmethod
    def validate(user):
        user_schema = Schema({
            'id': str,
            'first_name': str,
            'last_name': str,
            'birthday': str,
        })
        return user_schema.validate(user)

    @staticmethod
    def load(user_id):
        obj = s3.get_object(
            Bucket=BUCKET,
            Key=user_id,
        )
        user = json.loads(obj['Body'].read())
        return User.validate(user)

    @staticmethod
    def save(user):
        user_id = user.setdefault('id', str(uuid.uuid4()))
        user = User.validate(user)
        s3.put_object(
            Bucket=BUCKET,
            Key=user_id,
            Body=json.dumps(user),
        )
        return user

    @staticmethod
    def delete(user_id):
        s3.delete_object(
            Bucket=BUCKET,
            Key=user_id,
        )
        return {'deleted_id': user_id}

    @staticmethod
    def list_ids():
        bucket_content = s3.list_objects_v2(Bucket=BUCKET)

        user_ids = [
            file_path['Key']
            for file_path in bucket_content.get('Contents', [])
            if file_path['Size'] > 0
        ]

        return user_ids
