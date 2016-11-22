from pymongo import MongoClient

from config import Config as cfg
from models import Series, Slice

def get_mongo_db(config=None):
    if config is None:
        config = cfg
    client = MongoClient(cfg.MONGO_SERVER, cfg.MONGO_PORT)
    db = client[cfg.MONGO_DB_NAME]
    return db

def get_series(db=None, config=None):
    if db is None:
        db = get_mongo_db(config)

def add_series(name, frequency, columns=[], db=None, config=None):
    if db is None:
        db = get_mongo_db(config)
    series = db.series
    new_series = {"name": name, "frequency": frequency, "columns": columns, "slices": []}
    result = series.insert_one(new_series)
    return Series(series, result.inserted_id, name, frequency)