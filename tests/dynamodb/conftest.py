import pytest

import tss.utils_aws as utils
from tss.models_aws import SERIES_SCHEMA, DATA_SCHEMA


@pytest.fixture(scope="session", autouse=True)
def db():
    return utils.get_dynamodb()


@pytest.fixture
def series(db):
    return db.Table(SERIES_SCHEMA['TableName'])


@pytest.fixture
def data(db):
    return db.Table(DATA_SCHEMA['TableName'])


@pytest.fixture(scope="session", autouse=True)
def create_table(db):
    utils.create_table(db)
