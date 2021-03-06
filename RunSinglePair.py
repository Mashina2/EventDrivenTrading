import math

from BinanceAPI import *
from GlobalFunctions import *
from Strategies import *
from BackEngine import *
import time as tt
from RetrieveData import sdate, edate, pair, interval


import warnings
warnings.filterwarnings("ignore")


if __name__ == "__main__":

    ### Fetch data first from binance "2020-08-04"##
    strategy = 'TSMA'
    sdate = sdate
    edate = "2020-01-17"
    # edate = "2022-05-12"
    pair = 'ETHUSDT' #ETHBTC BTCUSDT
    interval = interval
    desiredInterval = '24h'
    desiredHour = '06'
    switchInterval = True
    Direction = "Long" # Long, Short, LS
    commission = 10 ### bps
    fundrate = 0 ### bps
    plot = True
    monthlyStats = False
    fullReport = True
    N = 365

    # 8HR
    dictParams = {'short_ma': [2],  ## {'short_ma': range(10, 1000, 10),
                  'medium_ma': [9],  ## 'long_ma': range(100, 10000, 100),
                  'long_ma': [34],
                  'threshold': [0]}  ## 'long_ma': range(100, 10000, 100)

    # dictParams = {'short_ma': range(1, 5, 1),  ## {'short_ma': range(10, 1000, 10),
    #               'medium_ma': range(9, 18, 2),  ## 'long_ma': range(100, 10000, 100),
    #               'long_ma': range(21, 41, 3),
    #               'threshold': [0]}  ## 'long_ma': range(100, 10000, 100),

    finaldata = readpkl(pair)

    if (switchInterval):
        finaldata = modifyOHLCtime(OHLC = finaldata,currentInterval = interval,desiredInterval = desiredInterval,
                                   desiredHour = desiredHour)
        finaldata = finaldata.set_index('Close time')
        # finaldata.index = pd.to_datetime(finaldata.index)
        # type(finaldata.index)

    AllParams = expand_grid(dictParams)
    params = AllParams[(AllParams['long_ma'] - AllParams['short_ma']) >= 1]
    params.index = range(1, len(params) + 1)
    params['Direction'] = Direction

    start = tt.time()

    allPerform = pd.DataFrame()
    for index, row in params.iterrows():

        print('\n', '---------------Now doing combination ' f"{index}/{len(params)}---------------", '\n')
        row['index'] = index
        strResult = BacktestEngine(data = finaldata, strategy = strategy, plot = plot, comms=commission, fundrate = fundrate,
                                   monthlyStats = monthlyStats, params = row, benchmark = pair, sdate = sdate, edate = edate)

        allrets = strResult['strategyReturns']
        strName = allrets.columns[0]

        if monthlyStats:
            N = 12
            allrets = MonthlyRets(allrets)

        getStats = statistics(allrets, N=N)
        getStats['short_ma'] = row['short_ma']
        getStats['medium_ma'] = row['medium_ma']
        getStats['long_ma'] = row['long_ma']

        corrMtx = allrets.corr()
        #getStats['threshold'] = row['threshold']

        # rr = allrets.reset_index(drop=True)
        # rr.corr()
        # correlation = allrets.iloc[:, 0].corr(allrets.iloc[:, 1])

        allPerform = allPerform.append(getStats.iloc[[0]])

        clndRets = trades = math.nan
        if fullReport:

            if not monthlyStats:
                allrets = MonthlyRets(allrets)

            strclndRets = CalendarRets(allrets[[strName]])
            bnchclndRets = CalendarRets(allrets[[pair]])
            trades = strResult['Trades']

        print(getStats,'\n')
        print(corrMtx, '\n')
        print(f"{strName} Monthly Return", '\n', strclndRets, '\n')
        print(f"{pair} Monthly Return", '\n', bnchclndRets, '\n')
        print(trades,'\n')

    latency = tt.time() - start

    print(f"Iterating {len(params)} {strName} combinations took {latency:.3f} seconds", '\n')

    allPerform = allPerform.sort_values(by='Calmar', ascending=False)
    print(allPerform)

# aa = strResult['LongTradesAls']
# len(aa[aa['Return']<0]['Return']) / len(aa)
#
# aa.tail()

# strResult['Trades']
# strResult['tradeAction']
# print(strResult['allData'].head(5))
# strResult['OriginalReturns']
# savepkl('BTCETH1hPerform', allPerform)
# strResult.keys()
# strResult['OriginalReturns'].tail(20)
# strResult['allData'].head(3)
# strResult['tradeAction']
# aa = strResult['allData']
# aa.loc[(aa.index >= '2018-01-20') & (aa.index <= '2018-03-30')]
# bb = aa.loc[aa.index <= '2018-02-12']
# cc = bb.tail(21)
# cc.tail(1)
# cc.Close.mean()

# dd = cc.Close
# dd.head(21).mean()

# aa.loc[(aa.index >= '2021-08-30')]

# finaldata = finaldata.drop(['Open time', 'symbol'], axis = 1)
# finaldata = finaldata[['Close time'] + list(finaldata.columns[:4]) + ['Number of trades']]
# finaldata.to_csv('ETHBTC5MIN.txt', sep=';', index=False)
# finaldata.to_csv('ETHBTC5MIN.txt', sep='\t', index=False)
# finaldata = data.DataReader('SPY', 'yahoo',start='1/1/2000') - yahoo

# perform1h = readpkl('BTCETH1hPerform')
# perform1h.sort_values(by='Calmar Ratio', ascending=False)

