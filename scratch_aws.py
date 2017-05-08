import tss.utils_aws as utils

import pandas as pd
df = pd.read_csv('CURRFX-GBPUSD.csv')
df[0:10]
from datetime import datetime
df.Date = df.Date.map(lambda d: datetime.strptime(d, '%Y-%m-%d'))
df = df.set_index('Date')
df

df.Rate = df.Rate.astype(str)
df['High (est)'] = df['High (est)'].astype(str)
df['Low (est)'] = df['Low (est)'].astype(str)
df.dtypes
utils.create_with_sparse_slices_from_df(df, '/fx/raw', 'GBP/USD', '1d', 100)

import numpy as np
series = utils.get_series('/fx/raw', 'GBP/USD')
df = series.get(data_from=np.datetime64('2017-01-01 00:00:00'), data_to=np.datetime64('2017-03-01 00:00:00'))
