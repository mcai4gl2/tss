import boto3


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

class Series(object):
    def __init__(self, db, collection, scope, name, frequency, columns=[], slices=[]):
        self.db = db
        self.collection = collection
        self.scope = scope
        self.name = name
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

    def add_slice(self, start, num_of_samples=0):
        new_slice_data = {'series_full_name': Series._series_full_name(self.scope, self.name),
                          'slice_id': Series._generate_slice_id()}
        table = db.Table(DATA_SCHEMA['TableName'])
        table.put_item(Item=new_slice_data)
        slice = SpareSlice(self.db, table, start, num_of_samples, self, new_slice['slice_id'])
        new_slice = {'start': start, 
                     'num_of_samples': num_of_samples, 
                     'id': slice.id, 
                     'is_sparse': slice.is_sparse}
        self.collection.update_item(Key={'scope': scope, 'name': name},
                                    UpdateExpression="SET slices = list_append(slices, :i)",
                                    ExpressionAttributeValues={':i': [new_slice]},
                                    ReturnValues="UPDATED_NEW")
        self.slices[slice.id] = slice
        return slice


class SpareSlice(object):
    def __init__(self, db, collection, start, num_of_samples, series=None, id=None):
        self.db = db
        self.collection = collection
        self.series = series
        self.id = id
        self.start = start
        self.num_of_samples = num_of_samples
        self.is_sparse = True

    