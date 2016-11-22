import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    BASE_DIR = BASE_DIR
    MONGO_SERVER = os.getenv('MONGO_SERVER', 'localhost')
    MONGO_PORT = os.getenv('MONGO_PORT', 27017)
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'tss')