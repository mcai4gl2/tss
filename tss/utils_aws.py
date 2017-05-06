import boto3

from models_aws import SERIES_SCHEMA, DATA_SCHEMA, Series

from . import FREQUENCIES


def get_dynamodb(config):
    return boto3.resource('dynamodb',
                          aws_access_key_id='anything',
                          aws_secret_access_key='anything',
                          region_name='us-west-2',
                          endpoint_url='http://localhost:8000')


def create_table(db=None, config=None):
    if db is None:
        db = get_dynamodb(config)
    db.create_table(**SERIES_SCHEMA)
    db.create_table(**DATA_SCHEMA)


def add_series(name, frequency, columns=[], db=None, config=None, scope='/'):
    if db is None:
        db = get_dynamodb(config)
    if frequency not in FREQUENCIES.keys():
        raise ValueError('frequency is not valid')
    new_series = {"scope": scope, "name": name, "frequency": frequency, "columns": columns, "slices": []}
    table = db.Table(SERIES_SCHEMA['TableName'])
    table.put_item(Item=new_series)
    return Series(db, table, scope, name, frequency, columns)

