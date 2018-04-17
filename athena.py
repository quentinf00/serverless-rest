import os
import boto3
from time import sleep
import config
import schema

athena = boto3.client('athena')



PY_2_ATHENA_TYPE_MAPPING = {
    str: 'STRING',
    int: 'BIGINT',
    float: 'DOUBLE',
    bool: 'BOOLEAN',
}

def get_init_schema_handler(resource_class):
    schema = resource_class.SCHEMA
    name = resource_class.name

    def init_schema(event, context):
        db = get_results(f"""
            CREATE DATABASE IF NOT EXISTS {config.DATABASE_NAME}
            LOCATION 's3://{config.BUCKET}/';
        """, 'default')


        table = get_results(f"""
            CREATE EXTERNAL TABLE IF NOT exists {name} (
                {get_table_model_from_schema(schema)}
            )
            ROW FORMAT  serde 'org.openx.data.jsonserde.JsonSerDe'
            LOCATION 's3://{config.BUCKET}/{name}/';
        """)

        return db, table

    return init_schema

def get_results(query, database=config.DATABASE_NAME):
    query_id = hash(query)

    response = athena.start_query_execution(
        QueryString = query,
        QueryExecutionContext={
            'Database': database
        },
        ResultConfiguration={
            'OutputLocation': f's3://{config.ATHENA_BUCKET}/{query_id}'
        }
    )

    results = get_query_results(response['QueryExecutionId'])
    return results

def get_query_results(exec_id):

    while(not is_execution_done(exec_id)):
        sleep(1)

    results = athena.get_query_results(
        QueryExecutionId=exec_id,
    )

    return format_result(results)

def is_execution_done(exec_id):
    response = athena.get_query_execution(
        QueryExecutionId=exec_id,
    )
    print(response['QueryExecution']['Status']['State'])
    return response['QueryExecution']['Status']['State'] == 'SUCCEEDED'

def format_result(results):

    columns = [
        col['Label']
        for col in results['ResultSet']['ResultSetMetadata']['ColumnInfo']
    ]

    formatted_results = []

    for result in results['ResultSet']['Rows'][1:]:
        values = [list(field.values())[0] for field in result['Data']]

        formatted_results.append(
            dict(zip(columns, values))
        )

    return formatted_results



def get_table_model_from_schema(class_schema, current_table_model = ''):
    _schema = class_schema._schema

    if 'id' not in _schema:
        current_table_model += 'id STRING,\n'

    for key in _schema:
        if type(key) == schema.Optional:
            key = key._schema

        current_table_model += f'{key} {get_type_def(_schema[key])},\n'

    return current_table_model.strip(',\n')


def get_type_def(_schema):
    try:
        if type(_schema) == type:
            return PY_2_ATHENA_TYPE_MAPPING[_schema]

        if type(_schema) == schema.And:
            try:
                key_type = next(arg for arg in _schema._args if type(_schema) == type)
                return PY_2_ATHENA_TYPE_MAPPING[_schema]
            except:
                raise Exception('Please put the data type in the top level And')

        if type(_schema) == list:
            return f'array<{get_type_def(_schema[0])}>'

        if type(_schema) == dict:
            dict_def = ',\n'.join([f'`{k}`:{get_type_def(_schema[k])}' for k in _schema])
            return f'struct<{dict_def}>'

    except:
        pass

    raise Exception(f'Failed to get the type definition of _schema: {_schema}')
