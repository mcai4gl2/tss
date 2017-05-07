import boto3

from models_aws import SERIES_SCHEMA, DATA_SCHEMA, Series, SpareSlice

from . import FREQUENCIES


def get_dynamodb(config=None):
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


def get_series(scope, name, db=None, config=None):
    if db is None:
        db = get_dynamodb(config)
    table = db.Table(SERIES_SCHEMA['TableName'])
    result = table.get_item(Key={'scope': scope, 'name': name})
    item = result['Item']
    return Series(db, table, scope, name, 
                  item['frequency'], 
                  item['columns'], 
                  _get_slices(db, config, Series._series_full_name(scope, name), item['slices'])) 


def add_series(name, frequency, columns=[], db=None, config=None, scope='/'):
    if db is None:
        db = get_dynamodb(config)
    if frequency not in FREQUENCIES.keys():
        raise ValueError('frequency is not valid')
    new_series = {"scope": scope, "name": name, "frequency": frequency, "columns": columns, "slices": []}
    table = db.Table(SERIES_SCHEMA['TableName'])
    table.put_item(Item=new_series)
    return Series(db, table, scope, name, frequency, columns)


def _get_slices(series_full_name, db=None, config=None, slices=None):
    if slices is None:
        return []
    if db is None:
        db = get_dynamodb(config)
    table = db.Table(DATA_SCHEMA['TableName'])
    return [SpareSlice(db, table, slice.start, None, slice.slice_id) for slice in slices]


def create_with_sparse_slices_from_df(df, scope, name, frequency, num_of_elements_per_slice, db=None, config=None):
    if df.shape[0] == 0:
        raise ValueError('df shall not be empty')
    
    first_index_value = df.iloc[0].name
    if not isinstance(first_index_value, datetime) and not isinstance(first_index_value, np.datetime64):
        raise ValueError("df's index can only either be of type datetime.datetime or numpy.datetime64")
    
    df.sort_index(inplace=True)
        
    series = add_series(name, frequency, list(df.columns), db, config, scope=scope)
    
    for chunk in (df[pos:pos + num_of_elements_per_slice] for pos in xrange(0, df.shape[0], num_of_elements_per_slice)):
        sparse_slice = series.add_slice(chunk.iloc[0].name)
        data = chunk.to_dict(orient='index')
        sparse_slice.add(data)
    return series
