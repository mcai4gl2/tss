import boto3

from models import Series as MongoSeries
from models import Slice as MongoSlice


SERIES_SCHEMA = {
    'TableName': 'Series',
    'KeySchema': [
        {
            'AttributeName': 'scope',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'name',
            'KeyType': 'RANGE'
        }
    ],
    'AttributeDefinitions': [
        {
            'AttributeName': 'scope',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'name',
            'AttributeType': 'S'
        }
    ],
    'ProvisionedThroughput': {
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
}

DATA_SCHEMA = {
    'TableName': 'Data',
    'KeySchema': [
        {
            'AttributeName': 'series_full_name',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'slice_id',
            'KeyType': 'RANGE'
        }
    ],
    'AttributeDefinitions': [
        {
            'AttributeName': 'series_full_name',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'slice_id',
            'AttributeType': 'S'
        }
    ],
    'ProvisionedThroughput': {
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
}

class Series(MongoSeries):
    def __init__(self, db, collection, scope, name, frequency, columns=[], slices=[]):
        self.db = db
        self.collection = collection
        self.scope = scope
        self.name = name
        self.full_name = Series._series_full_name(scope, name)
        self.columns = columns
        self.frequency = frequency
        self.slices = {slice.id: slice for slice in slices}
        for slice in slices:
            slice.series = self
    
    @staticmethod
    def _series_full_name(scope, name):
        if scope.endswith('/'):
            return scope + name
        else:
            return scope + '/' + name

    @staticmethod
    def _generate_slice_id():
        return str(len(self.slices) + 1)

    def delete(self):
        for slice in self.slices.values():
            slice.delete()
        self.collectio.delete_item(
            Key={'scope': self.scope, 'name': self.name}
        )

    def add_slice(self, start):
        new_slice_data = {'series_full_name': self.full_name,
                          'slice_id': Series._generate_slice_id(),
                          'data': []}
        table = db.Table(DATA_SCHEMA['TableName'])
        table.put_item(Item=new_slice_data)
        slice = SpareSlice(self.db, table, start, self, new_slice['slice_id'])
        new_slice = {'start': start, 
                     'id': slice.id, 
                     'is_sparse': slice.is_sparse}
        self.collection.update_item(Key={'scope': scope, 'name': name},
                                    UpdateExpression="SET slices = list_append(slices, :i)",
                                    ExpressionAttributeValues={':i': [new_slice]},
                                    ReturnValues="UPDATED_NEW")
        self.slices[slice.id] = slice
        return slice


class SpareSlice(MongoSlice):
    def __init__(self, db, collection, start, series=None, id=None):
        self.db = db
        self.collection = collection
        self.series = series
        self.id = id
        self.start = start
        self.is_sparse = True

    def add(self, data):
        if type(data) != dict:
            raise ValueError('input data is not of type dict')
        if len(data.keys()) == 0:
            return
        if not (isinstance(data.keys()[0], datetime) or isinstance(data.keys()[0], np.datetime64)):
            raise ValueError('input data key is not of type datetime')
        data = [{'timestamp': SparseSlice._format_timestamp(d), 
                 'data': self._transform_data(data[d])} for d in data.keys()]
        self.collection.update_item(Key={'series_full_name': self.series.full_name, 'slice_id': self.id},
                                    UpdateExpression="SET data = list_append(data, :i)",
                                    ExpressionAttributeValues={':i': data},
                                    ReturnValues="UPDATED_NEW")
        # Unlike mongo version, we don't update slice count on series document as dynamodb api doesn't allow it

 
    def get(self, data_from=None, data_to=None):
        data = self.collection.get_item(Key={'series_full_name': self.series.full_name, 'slice_id': self.id})['Item']['data']
        results = [[np.datetime64(d['timestamp'])] + d['data'] for d in data if 
                   (data_from is None or d['timestamp'] >= data_from) and 
                   (data_to is None or d['timestamp'] <= data_to)]
        return results
