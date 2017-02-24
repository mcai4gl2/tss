class Series(object):
    def __init__(self, collection, objectId, name, frequency, columns=[], slices=[]):
        self.collection = collection
        self.id = objectId
        self.name = name
        self.columns = columns
        self.frequency = frequency
        self.slices = slices
        
    def delete(self):
        self.collection.delete_one({"_id": self.id})
        
    def __repr__(self):
        return 'Series[id={}, name={}, columns={}, frequency={}]'.format(self.id, self.name, self.columns, self.frequency)

class Slice(object):
    def __init__(self, series, objectId, start, num_of_samples):
        self.series = series
        self.id = objectId
        self.start = start
        self.num_of_samples = num_of_samples
        
