from datetime import datetime

import pandas as pd
from pandas.util.testing import assert_frame_equal


def test_delete_series_without_slices(a_series, series, data):
    assert series.find({'_id': a_series.id}, {'_id': 1}).limit(1).count() == 1
    assert data.find({}, {'_id': 1}).count() == 0
    assert a_series.id is not None
    a_series.delete()
    assert series.find({'_id': a_series.id}, {'_id': 1}).limit(1).count() == 0
    assert data.find({}, {'_id': 1}).count() == 0
    assert a_series.id is None
    

def test_add_slice(a_series, series, data):
    start = datetime(2017, 3, 4)
    slice = a_series.add_slice(start)
    assert slice.start == start
    assert data.find({}, {'_id': 1}).count() == 1
    id = data.find({}, {'_id': 1})[0]['_id']
    assert slice.id == id
    assert slice.collection == data
    assert slice.series == a_series
    assert slice.num_of_samples == 0
    assert len(a_series.slices) == 1
    assert slice.series == a_series


def test_delete_slice(a_series, a_slice, data):
    a_slice.delete()
    assert a_slice.id is None
    assert data.find({}, {'_id': 1}).count() == 0
    assert len(a_series.slices) == 0
    
    
def test_delete_series_with_slices(a_series, a_slice, data):
    a_series.delete()
    assert len(a_series.slices) == 0
    assert a_series.id is None
    assert a_slice.id is None
    assert data.find({}, {'_id': 1}).count() == 0
    
    
def test_add_one_data_point_to_slice(a_slice, data):
    input = [['abc', 1, 2, 3]]
    a_slice.add(input)
    assert a_slice.num_of_samples == 1
    stored_data = data.find({})
    assert stored_data.count() == 1
    stored_data = stored_data[0] 
    assert stored_data['data'] == input
    

def test_add_two_data_points_to_slice(a_slice, data):
    input = [['abc', 1, 2, 3], ['bcd', 2, 3, 4]]
    a_slice.add(input)
    assert a_slice.num_of_samples == 2
    stored_data = data.find({})
    assert stored_data.count() == 1
    stored_data = stored_data[0] 
    assert stored_data['data'] == input
    
    
def test_add_data_into_slices_which_already_has_data(a_slice, data):
    input = [['abc', 1, 2, 3]]
    a_slice.add(input)
    a_slice.add(input)
    assert a_slice.num_of_samples == 2
    stored_data = data.find({})
    assert stored_data.count() == 1
    stored_data = stored_data[0] 
    assert stored_data['data'] == [input[0], input[0]]
    
    
def test_get_data_from_slice(a_slice, data):
    output = a_slice.get()
    assert output == []
    input = [['abc', 1, 2, 3]]
    a_slice.add(input)
    output = a_slice.get()
    assert input == output
    

def test_slice_end_property(a_series, a_slice):
    a_series.frequency = '1d'
    a_slice.start = datetime(2017, 3, 4)
    assert a_slice.start == a_slice.end
    a_slice.add([1])
    assert a_slice.end == datetime(2017, 3, 5)
    assert type(a_slice.end) == datetime
    

def test_get_data_from_series(a_series, a_slice):
    a_series.frequency = '1d'
    a_slice.start = datetime(2017, 3, 4)
    a_slice.add([[1, 2], [3, 4]])
    results = a_series.get()
    expected = pd.DataFrame({'col1': [1., 3.], 'col2': [2., 4.], 'time': [datetime(2017, 3, 4), datetime(2017, 3, 5)]})
    expected.set_index('time', inplace=True)
    assert_frame_equal(expected, results)
    

def test_get_data_from_slice_with_filters(a_series, a_slice, data):
    a_series.frequency = '1d'
    a_slice.start = datetime(2017, 3, 4)
    a_slice.add([[1], [2], [3], [4], [5]])
    output = a_slice.get()
    assert output == [[1], [2], [3], [4], [5]]
    output = a_slice.get(data_from=datetime(2017, 3, 4), data_to=datetime(2017, 3, 4))
    assert output == [[1]]
    output = a_slice.get(data_from=datetime(2017, 3, 3), data_to=datetime(2017, 3, 3))
    assert output == []
    output = a_slice.get(data_from=datetime(2017, 3, 5))
    assert output == [[2], [3], [4], [5]]
    output = a_slice.get(data_from=datetime(2017, 3, 11))
    assert output == []