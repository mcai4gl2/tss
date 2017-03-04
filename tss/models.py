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
    
    def delete(self):
        self.collection.delete_one({"_id": self.id})
        del self.series.slices[self.id]
        self.id = None
        
    def __repr__(self):
        return 'Slice[id={}, start={}, number_of_samples={}]'.format(self.id, self.start, self.num_of_samples)