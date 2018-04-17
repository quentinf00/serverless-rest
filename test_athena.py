from schema import Schema
from athena import get_table_model_from_schema

def test_plain_schema():
    SCHEMA = Schema({
        'id': str,
        'first_name': str,
        'last_name': str,
        'birthday': str,
    })
    assert get_table_model_from_schema(SCHEMA)== ('id STRING,\n'
                                                  'first_name STRING,\n'
                                                  'last_name STRING,\n'
                                                  'birthday STRING')