from StringIO import StringIO
from datetime import datetime

import pytest
import pandas as pd
import numpy as np

import tss.utils_aws as utils
from tss.models_aws import Series, SpareSlice


def test_add_series(series):
    result = utils.add_series('test', '1d', ['col1'])
    assert result.collection == series
    assert result.name == 'test'
    assert result.frequency == '1d'
    assert result.columns == ['col1']
    assert result.slices == {}


