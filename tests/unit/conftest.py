import pytest
import mongomock

@pytest.fixture
def db():
    return mongomock.MongoClient().db

@pytest.fixture
def series(db):
    return db.series