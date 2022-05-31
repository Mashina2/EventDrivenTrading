from binance.client import Client
import pandas as pd
from binance.enums import *
from GlobalFunctions import *

# binance.fetch_balance({'recvWindow': 10000000})

# import sys
# sys.path.insert(1, 'C:/SpacEngine/trunk')
# from trunk import NAV


# set pandas size
pd.set_option('display.width', 300)
pd.set_option('display.max_columns', 30)
pd.set_option('display.max_rows', 150)
# pd.set_option('precision', 5)
pd.set_option('mode.chained_assignment', None) ## turning off SettingWithCopyWarning

api_key = 'DVxVn8JHKAfI2By0CqmdFySHmQA5Oiv9RhcANj0KsF7s7EYl9hDc4p0dW3l7daPY'
api_secret = 'C6eQzWYP3RcjQ8zcVWeTf8kZ0KHnMtGqsSnDQVPu5ZiDk2AnRHONgtziZsMFIxbi'

client = Client(api_key, api_secret)

def binanceOHLC(klines):

    dfklines = pd.DataFrame(klines)
    dfklines.rename(
        columns={0: 'Open time', 1: 'Open', 2: 'High', 3: 'Low', 4: 'Close', 5: 'Volume', 6: 'Close time', 7: 'Quote asset volume',
                 8: 'Number of trades', 9: 'Taker buy base asset volume', 10: 'Taker buy quote asset volume', 11: 'ignore'},
        inplace=True)

    ohlc = dfklines[['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Number of trades']]

    startTime = ohlc['Open time']
    endTime = ohlc['Close time']
    sdate = IntegertoDatatime(startTime)
    edate = IntegertoDatatime(endTime)

    ohlc['Open time'] = sdate
    ohlc['Close time'] = edate
    ohlc = ohlc.drop(['Open time'], axis=1)
    ohlc = ohlc.set_index('Close time')
    ohlc['Close'] = pd.to_numeric(ohlc['Close'])
    colsTonum = list(ohlc.columns)[0:6]
    ohlc[colsTonum] = ohlc[colsTonum].apply(pd.to_numeric, errors='coerce', axis=1)

    return ohlc

def SMA(ohlc, params):

    short_ma = int(params['short_ma'])
    long_ma = int(params['long_ma'])

    ohlc['short_ma'] = ohlc['Close'].rolling(window=short_ma).mean()
    ohlc['long_ma'] = ohlc['Close'].rolling(window=long_ma).mean()
    ohlc['FACTOR'] = ohlc['short_ma'] / ohlc['long_ma'] - 1

    return ohlc


def LimitOrder(symbol='ETHBTC', action='BUY', quantity='1.04', price=0.01):

    if action == 'BUY':

        result = client.create_margin_order(
            symbol=symbol,
            side=SIDE_BUY,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC,
            sideEffectType="MARGIN_BUY",
            quantity=quantity,
            price=price)

    elif action == 'SELL':

        result = client.create_margin_order(
            symbol=symbol,
            side=SIDE_SELL,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC,
            sideEffectType="MARGIN_BUY",
            quantity=quantity,
            price=price)

    else:
        print(f"Action is {action}, however it can be BUY or SELL only")

    return result


def marginAccountDetails(symbol):

    info = client.get_margin_account()
    btcValue = float(info['totalAssetOfBtc'])

    priceIndex = client.get_margin_price_index(symbol=symbol)
    priceIndex = float(priceIndex['price'])

    depth = client.get_order_book(symbol=symbol)
    depth = pd.DataFrame(depth)

    result = {}
    result['btcValue'] = btcValue
    result['priceIndex'] = priceIndex
    result['MarketDepth'] = depth

    return result

def priceQtybyAccount(symbol, bid=True, epsilon=0):

    accountInfo = marginAccountDetails(symbol)

    btcValue = accountInfo['btcValue'] * 2 - 0.0001
    depth = accountInfo['MarketDepth']

    if bid == True:
        price = float(depth['bids'][0][0])
    else:
        price = float(depth['asks'][0][0])

    price = price * (1 + epsilon)
    price = truncate(price, decimals=6)

    Amount = btcValue / price
    qty = truncate(Amount, decimals=3)

    result = {}
    result['quantity'] = qty
    result['price'] = price

    return result
####
# depth = client.get_order_book(symbol='BNBPAX')
# depth.keys()
# depth['bids']
# depth['asks']
#
# trades = client.get_historical_trades(symbol='BNBBTC')
# trades = client.get_aggregate_trades(symbol='BNBBTC')
#
# candles = client.get_klines(symbol='BNBBTC', interval=Client.KLINE_INTERVAL_30MINUTE)
# len(candles)
#
# # fetch 1 minute klines for the last day up until now
# klines = client.get_historical_klines("BNBBTC", Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")
#
# # fetch 30 minute klines for the last month of 2017
# klines = client.get_historical_klines("ETHBTC", Client.KLINE_INTERVAL_5MINUTE, "1 Dec, 2016", "1 Jul, 2020")
# klines = client.get_historical_klines("ETHBTC", Client.KLINE_INTERVAL_1DAY, "1 Dec, 2013", "1 Jul, 2020")
#
#
# # fetch weekly klines since it listed
# klines = client.get_historical_klines("NEOBTC", Client.KLINE_INTERVAL_1WEEK, "1 Jan, 2017")
# prices = client.get_all_tickers()
#
#


# info = client.get_margin_asset(asset='BNB')
# info1 = client.get_margin_symbol(symbol=symbol)
# amt_str = "{:0.0{}f}".format(ethValue, precision)
# orders = client.get_all_margin_orders(symbol=symbol)
# orders = pd.DataFrame(orders)
# orderID = orders[orders['status'] == 'NEW']['orderId'].iloc[0]