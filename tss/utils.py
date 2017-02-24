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
    series = [Series(db.series, series['_id'], series['name'], series['frequency'], series['columns'], series['slices']) 
              for series in cursor]
    return series


def add_series(name, frequency, columns=[], db=None, config=None):
    if db is None:
        db = get_mongo_db(config)
    series = db.series
    new_series = {"name": name, "frequency": frequency, "columns": columns, "slices": []}
    result = series.insert_one(new_series)
    return Series(series, result.inserted_id, name, frequency)