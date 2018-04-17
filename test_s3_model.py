import boto3
from unittest.mock import patch
from moto import mock_s3
from s3_model import S3Model
import json
from unittest import TestCase
from s3_model import S3Model
from schema import Schema, SchemaMissingKeyError

@mock_s3
@patch('s3_model.config.BUCKET', 'BUCKET')
def test_load():
    s3 = boto3.client('s3', region_name='eu-central-1')
    s3.create_bucket(Bucket='BUCKET')
    uid = 'toto'
    s3.put_object(
        Bucket='BUCKET',
        Key=f'raw/{uid}',
        Body=json.dumps({}),
    )

    obj = S3Model.load('toto')
    assert obj == {}

@mock_s3
@patch('s3_model.config.BUCKET', 'BUCKET')
def test_save():
    s3 = boto3.client('s3', region_name='eu-central-1')
    s3.create_bucket(Bucket='BUCKET')

    obj_saved = S3Model.save({})
    obj_loaded = S3Model.load(obj_saved['id'])

    assert obj_loaded == obj_saved

    obj_resaved = S3Model.save(obj_loaded)
    obj_reloaded = S3Model.load(obj_resaved['id'])

    assert obj_reloaded == obj_loaded

@mock_s3
@patch('s3_model.config.BUCKET', 'BUCKET')
def test_list_ids():
    s3 = boto3.client('s3', region_name='eu-central-1')
    s3.create_bucket(Bucket='BUCKET')

    obj_saved = S3Model.save({})
    obj_ids = S3Model.list_ids()

    assert obj_ids == [obj_saved['id']]

@mock_s3
@patch('s3_model.config.BUCKET', 'BUCKET')
def test_delete():
    s3 = boto3.client('s3', region_name='eu-central-1')
    s3.create_bucket(Bucket='BUCKET')

    obj_saved = S3Model.save({})

    obj_ids_before_delete = S3Model.list_ids()
    deleted_ids = S3Model.delete_obj(obj_saved['id'])
    obj_ids = S3Model.list_ids()

    assert obj_ids == []

@mock_s3
@patch('s3_model.config.BUCKET', 'BUCKET')
@patch('s3_model.uuid.uuid4', lambda : 'id_foo')
def test_api():
    s3 = boto3.client('s3', region_name='eu-central-1')
    s3.create_bucket(Bucket='BUCKET')

    event_create = {
        'body': b'{}'
    }
    resp_post = S3Model.post(event_create, None)
    assert resp_post == {'statusCode': 200, 'body': '{"id": "id_foo"}'}

    event_update = {
        'pathParameters': {'id': 'id_foo'},
        'body': b'{"new_field": "value"}',
    }
    resp_put = S3Model.put(event_update, None)
    assert resp_put == {'statusCode': 200, 'body': '{"id": "id_foo", "new_field": "value"}'}

    event_get = {
        'pathParameters': {'id': 'id_foo'}
    }
    resp_get = S3Model.get(event_get, None)
    assert resp_get == {'statusCode': 200, 'body': '{"id": "id_foo", "new_field": "value"}'}

    event_delete = {
        'pathParameters': {'id': 'id_foo'}
    }
    resp_delete = S3Model.delete(event_delete, None)
    assert resp_delete == {'statusCode': 200, 'body': '{"deleted_id": "id_foo"}'}


class TestSchemaValidation(TestCase):
    def test_save_with_schema_validation(self):
        class User(S3Model):
            SCHEMA = Schema({
                'first_name': str
            })

        with self.assertRaises(SchemaMissingKeyError):
            obj_saved = User.save({})
