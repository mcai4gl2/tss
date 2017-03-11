tss
===
[![CircleCI](https://circleci.com/gh/mcai4gl2/tss.svg?style=svg)](https://circleci.com/gh/mcai4gl2/tss)

tss is a simple time series storage on top of Mongodb. It allows user to store pandas DataFrames directly into mongodb under a simple schema. Data stored in Mongodb are in native format. This is to allow other languages to directly interacting the storage to read or modify data. 

tss uses two collections to store the data in Mongodb:
* series - which stores the time series meta data and chunks' meta data
* data - which stores the actual data

Examples:
* Creating a new time series from pandas DataFrame:
```Python
from StringIO import StringIO

import pandas as pd
import numpy as np

from tss.utils import get_mongo_db

db = get_mongo_db()
input_data=StringIO("""col1,col2,col3
1,2,3
4,5,6
7,8,9
""")
    df = pd.read_csv(input_data, sep=",")
    df['time'] = pd.Series([np.datetime64(datetime(2017, 3, 8)),
                            np.datetime64(datetime(2017, 3, 9)),
                            np.datetime64(datetime(2017, 3, 10))])
    df.set_index(['time'], inplace=True)
    result = utils.create_with_sparse_slices_from_df(df, 'test1', '1d', 1, db)
```
By default, tss connects to mongo at localhost:27017 with db name tss. This can be customized by environment variables: MONGO_SERVER, MONGO_PORT, and MONGO_DB_NAME.