import pytest
import mongomock
from datetime import datetime

import tss.utils as utils


@pytest.fixture
def db():
    return mongomock.MongoClient().db

@pytest.fixture
def series(db):
    return db.series


@pytest.fixture
def data(db):
    return db.data


@pytest.fixture
def a_series(db):
    return utils.add_series('test', '1d', ['col1', 'col2'], db)


@pytest.fixture
def a_slice(a_series):
    start = datetime(2017, 3, 4)
    return a_series.add_slice(start) 