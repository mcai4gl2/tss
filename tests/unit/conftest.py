import pytest
import mongomock

@pytest.fixture
def db():
    return mongomock.MongoClient().db

@pytest.fixture
def series(db):
    return db.series


@pytest.fixture
def data(db):
    return db.data