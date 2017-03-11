tss
===
[![CircleCI](https://circleci.com/gh/mcai4gl2/tss.svg?style=svg)](https://circleci.com/gh/mcai4gl2/tss)

tss is a simple time series storage on top of Mongodb. It allows user to store pandas DataFrames directly into mongodb under a simple schema. Data stored in Mongodb are in native format. This is to allow other languages to directly interacting the storage to read or modify data. 

tss uses two collections to store the data in Mongodb:
* series - which stores the time series meta data and chunks' meta data. The document is defined as follows:

| Attribute | Data Type | Notes |
| --- | --- | --- |
| _id | ObjectId | id for the time series |
| frequency | String | the frequency of the data: 1d, 1m and 1s |
| name | String | the name of the time series |
| columns | String[] | the name of the columns |
| slices | array of slice | slices meta data |

Where sub document slice is defined as:

| Attribute | Data Type | Notes |
| --- | --- | --- |
| id | ObjectId | slice's data's object id in data document |
| start | DateTime | start time of the slice |
| num_of_samples | int | the number of data stored in this slice |
| is_sparse | boolean | indicates whether the slice's data is stored in sparse way or not |

* data - which stores the actual data. data can be stored in either sparse way or not (currently, only sparse way is supported).

| Attribute | Data Type | Notes |
| --- | --- | --- |
| _id | ObjectId | id for slice |
| data | array | the actual data |

For sparse slice, the actual data is stored as subdocument as follows:

| Attribute | Data Type | Notes |
| --- | --- | --- |
| timestamp | DatTime | the timestamp of the data point |
| data | array | the data array representing a row of data |

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
    result = utils.create_with_sparse_slices_from_df(df, 'test1', '1d', 3, db)
```
By default, tss connects to mongo at localhost:27017 with db name tss. This can be customized by environment variables: MONGO_SERVER, MONGO_PORT, and MONGO_DB_NAME.

In mongo, the data is stored as:
```
> db.series.findOne()
{ 
	"_id" : ObjectId("58c45d4af4a6b0054cecdad6"), 
	"frequency" : "1d", "name" : 
	"test1", 
	"columns" : [ "col1", "col2", "col3" ], 
	"slices" : [ 
		{ 
			"start" : ISODate("2017-03-08T00:00:00Z"), 
			"num_of_samples" : 1, 
			"id" : ObjectId("58c45d4af4a6b0054cecdad7"), 
			"is_sparse" : true 
		}, 
		{ 
			"start" : ISODate("2017-03-09T00:00:00Z"), 
			"num_of_samples" : 1, 
			"id" : ObjectId("58c45d4af4a6b0054cecdad8"), 
			"is_sparse" : true 
		}, 
		{ 
			"start" : ISODate("2017-03-10T00:00:00Z"), 
			"num_of_samples" : 1, 
			"id" : ObjectId("58c45d4af4a6b0054cecdad9"), 
			"is_sparse" : true 
		} 
	] 
}
> db.data.find({})
{
	{ "_id" : ObjectId("58c45d4af4a6b0054cecdad7"), "data" : [ { "timestamp" : ISODate("2017-03-08T00:00:00Z"), "data" : [ 1, 2, 3 ] } ] }
	{ "_id" : ObjectId("58c45d4af4a6b0054cecdad8"), "data" : [ { "timestamp" : ISODate("2017-03-09T00:00:00Z"), "data" : [ 4, 5, 6 ] } ] }
	{ "_id" : ObjectId("58c45d4af4a6b0054cecdad9"), "data" : [ { "timestamp" : ISODate("2017-03-10T00:00:00Z"), "data" : [ 7, 8, 9 ] } ] }
}
```