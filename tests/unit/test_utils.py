from datetime import datetime
import pytest

import tss.utils as utils


def test_add_series(db, series):
    result = utils.add_series('test', '1d', ['col1'], db)
    assert result.id is not None
    assert result.collection == series
    assert result.name == 'test'
    assert result.frequency == '1d'
    assert result.columns == ['col1']
    assert result.slices == {}
    
    
def test_add_series_errors_when_frequency_is_not_valid(db, series):
    with pytest.raises(ValueError) as error:
        utils.add_series('test', 'XX', [], db)
    assert error.value.message == 'frequency is not valid'
    

def test_get_series_when_empty(db):
    results = utils.get_series(db)
    assert len(results) == 0
    

def test_get_series_by_id(db, series):
    s1 = utils.add_series('test', '1d', [], db)
    results = utils.get_series(db, id=s1.id)
    assert len(results) == 1
    result = results[0]
    assert s1.name == result.name
    assert s1.id == result.id
    assert s1.frequency == result.frequency
    assert s1.columns == result.columns
    assert s1.slices == result.slices
    
    
def test_get_series_by_invalid_id(db, series):
    results = utils.get_series(db, id='123456')
    assert results == []
    

def test_get_series_by_non_existing_id(db, series):
    results = utils.get_series(db, id='58b0b8b9f4a6b002cbb14ba9')
    assert results == []


def test_get_slices(db):
    slices = []
    assert utils._get_slices(db=db, slices=slices) == []
    assert utils._get_slices(db=db) == []   
    t = datetime.now()
    slices = [{'start': t, 'num_of_samples':100}, 
              {'start': t, 'num_of_samples':1, 'id': 123}]
    results = utils._get_slices(db=db, slices=slices)
    assert len(results) == 2
    result = results[0]
    assert result.db == db
    assert result.start == t
    assert result.num_of_samples == 100
    assert result.id is None
    result = results[1]
    assert result.db == db
    assert result.start == t
    assert result.num_of_samples == 1
    assert result.id == 123


def test_clear_all_when_empty(db, series, data):
    results = utils._clear_all(db)
    assert len(results) == 2
    assert 'series' in results
    assert 'data' in results
    assert results['series'] == 0
    assert results['data'] == 0
    

def test_clear_all_when_there_are_some_data(db, series, data):
    for _ in range(3):
        series.insert({})
    for _ in range(4):
        data.insert({})
    results = utils._clear_all(db)
    assert len(results) == 2
    assert 'series' in results
    assert 'data' in results
    assert results['series'] == 3
    assert results['data'] == 4