from trunk.BinanceAPI import *
from Strategies import *
import pandas as pd
from time import sleep
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from binance.enums import *

strategy = 'TSMA'
# edate = "2022-05-12"
pair = 'ETHUSDT' #ETHBTC BTCUSDT
interval = '1m'
Direction = "Long" # Long, Short, LS


dictParams = {'short_ma': 2,  ## {'short_ma': range(10, 1000, 10),
              'medium_ma': 9,  ## 'long_ma': range(100, 10000, 100),
              'long_ma': 34,
              'threshold': 0,
              'Direction': 'Long'}  ## 'long_ma': range(100, 10000, 100)

longSMA = dictParams['long_ma']
threshold = dictParams['threshold']
eps = 2
bar = int(interval[:-1])
start_str = f"{(longSMA + eps)*bar} minute ago UTC"

x = dt.datetime.utcnow()
startTime = x.replace(day=x.day, hour=9, minute=43, second=0, microsecond=0)

allActions = ['NOTHING']
while True:

    NOWutc = dt.datetime.utcnow()

    if NOWutc > startTime:

        print(f"Running Factor for time {(NOWutc)}")

        currentData = client.get_historical_klines(symbol=pair, interval=interval,start_str=start_str)
        df = binanceOHLC(currentData)
        strResult = globals()[strategy](df, dictParams)
        LastObs = strResult.iloc[[len(strResult)-1]]
        Factor = float(LastObs['Stance'])

        ### Check whether to buy or sell
        if Factor > threshold:
            msg = 'BUY or HOLD'
        else:
            msg = 'SELL or Stay Out'

    else:
        sleep(1)
        print(dt.datetime.utcnow())



