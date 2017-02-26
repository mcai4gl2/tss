from pymongo import MongoClient
from bson.objectid import ObjectId

from config import Config as cfg
from models import Series, Slice


def get_mongo_db(config=None):
    if config is None:
        config = cfg
    client = MongoClient(cfg.MONGO_SERVER, cfg.MONGO_PORT)
    db = client[cfg.MONGO_DB_NAME]
    return db


def get_series(db=None, config=None, id=None):
    if db is None:
        db = get_mongo_db(config)
    if id is not None:
        if ObjectId.is_valid(id):
            cursor = db.series.find({"_id": ObjectId(id)})
        else:
            return []
    else:
        cursor = db.series.find({})
    series = [Series(db, 
                     db.series, 
                     series['_id'], 
                     series['name'], 
                     series['frequency'], 
                     series['columns'], 
                     _get_slices(db, config, series['slices'])) 
              for series in cursor]
    return series


def add_series(name, frequency, columns=[], db=None, config=None):
    if db is None:
        db = get_mongo_db(config)
    series = db.series
    new_series = {"name": name, "frequency": frequency, "columns": columns, "slices": []}
    result = series.insert_one(new_series)
    return Series(db, series, result.inserted_id, name, frequency)


def _get_slices(db=None, config=None, slices=None):
    if slices is None:
        return []
    if db is None:
        db = get_mongo_db(config)
    return [Slice(db, slice['start'], slice['num_of_samples'], None, slice.get('id', None)) for slice in slices]


def _clear_all(db=None, config=None):
    if db is None:
        db = get_mongo_db(config)
    result1 = db.series.delete_many({})
    result2 = db.data.delete_many({})
    return {'series': result1.deleted_count, 'data': result2.deleted_count}