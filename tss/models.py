from datetime import datetime

import numpy as np
import pandas as pd


FREQUENCIES = {'1d': np.timedelta64(1, 'D'),
               '1m': np.timedelta64(1, 'm'),
               '1s': np.timedelta64(1, 's')}


class Series(object):
    def __init__(self, db, collection, objectId, name, frequency, columns=[], slices=[]):
        self.db = db
        self.collection = collection
        self.id = objectId
        self.name = name
        self.columns = columns
        self.frequency = frequency
        self.slices = {slice.id: slice for slice in slices}
        for slice in slices:
            slice.series = self
        
    def delete(self):
        for slice in self.slices.values():
            slice.delete()
        self.collection.delete_one({"_id": self.id})
        self.id = None

    def add_slice(self, start, num_of_samples = 0):
        result = self.db.data.insert_one({'data': []})
        slice = Slice(self.db, start, num_of_samples, self, result.inserted_id)       
        self.collection.update({'_id': self.id}, 
                               {"$push": {"slices": {'start': start, 'num_of_samples': num_of_samples, 'id': slice.id}}},
                               upsert=False)
        self.slices[slice.id] = slice
        return slice
    
    def find_slice_starts_at(self, datetime):
        return filter(self.slices, lambda s: s.start == datetime)
    
    def get(self, data_from=None, data_to=None):
        results = pd.DataFrame(columns=self.columns + ['time'])
        frequency = FREQUENCIES[self.frequency]
        for slice in self.slices.values():
            start = slice.start
            end = slice.end
            if data_from is not None and data_from > start:
                start = data_from
            if data_to is not None and data_to < end:
                end = data_to
            data = slice.get(start, end)
            if data == []:
                continue
            start = np.datetime64(start)
            timestamps = [start + i * frequency for i in xrange(0, slice.num_of_samples)]
            slice_df = pd.DataFrame(data, columns=self.columns)
            slice_df['time'] = pd.Series(timestamps, index=slice_df.index)
            results = results.append(slice_df)
        results.set_index('time', inplace=True)
        return results
    
    def __repr__(self):
        return 'Series[id={}, name={}, columns={}, frequency={}]'.format(self.id, self.name, self.columns, self.frequency)
    

class Slice(object):
    def __init__(self, db, start, num_of_samples, series = None, id = None):
        self.db = db
        self.collection = db.data
        self.series = series
        self.id = id
        self.start = start
        self.num_of_samples = num_of_samples
    
    def add(self, data):
        self.collection.update({'_id': self.id}, 
                               {'$push': {'data': {'$each': data}}})
        self.series.collection.update({'_id': self.series.id,
                                       'slices.id': self.id},
                                      {'$inc': {'slices.$.num_of_samples': len(data)}})
        self.num_of_samples += len(data)
        
    def get(self, data_from=None, data_to=None):
        if self.num_of_samples == 0:
            return []
        frequency = FREQUENCIES[self.series.frequency]
        data = self.collection.find({'_id': self.id}, {'data': 1}).limit(1)[0]['data']
        start = np.datetime64(self.start)
        timestamps = [start + i * frequency for i in xrange(0, self.num_of_samples)]
        results = zip(timestamps, data)
        if data_from is not None:
            data_from = np.datetime64(data_from)
        else:
            data_from = start
        if data_to is not None:
            data_to = np.datetime64(data_to)
        else:
            data_to = timestamps[-1]
        return [r[1] for r in results if r[0] >= data_from and r[0] <= data_to]
    
    @property
    def end(self):
        frequency = FREQUENCIES[self.series.frequency]
        start = np.datetime64(self.start)
        return (start + self.num_of_samples * frequency).astype(datetime)
        
    def delete(self):
        self.collection.delete_one({"_id": self.id})
        del self.series.slices[self.id]
        self.id = None
        
    def __repr__(self):
        return 'Slice[id={}, start={}, number_of_samples={}]'.format(self.id, self.start, self.num_of_samples)