import tss.utils as utils

def test_get_series_when_empty(db):
    results = utils.get_series(db)
    assert len(results) == 0
    

def test_add_series(db, series):
    result = utils.add_series('test', 100, [], db)
    assert result.id is not None
    assert result.collection == series
    assert result.name == 'test'
    assert result.frequency == 100
    assert result.columns == []
    assert result.slices == []