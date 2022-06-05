import math

from BinanceAPI import *
from GlobalFunctions import *
from Strategies import *
from BackEngine import *
import time as tt

import warnings
warnings.filterwarnings("ignore")

### Fetch data first from binance "2020-08-04"##
sdate = "2018-01-01"
edate = dt.datetime.today()
edate = edate.strftime("%Y-%m-%d")
# edate = "2022-05-12"
pair = 'ETHUSDT'  # ETHBTC BTCUSDT
interval = '1h'

if __name__ == "__main__":

    idate = dt.datetime.strptime(sdate, "%Y-%m-%d")
    idate = idate + dt.timedelta(days=-100)
    idate = idate.strftime("%Y-%m-%d")

    klines = client.get_historical_klines(symbol=pair, interval=interval, start_str=idate, end_str=edate)
    finaldata = binanceOHLC(klines)
    finaldata.index = pd.to_datetime(finaldata.index)

    savepkl(filename = pair, data = finaldata)
