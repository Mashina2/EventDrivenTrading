from BinanceAPI import *
from GlobalFunctions import *
from Strategies import *
from BackEngine import *
import time as tt

import warnings
warnings.filterwarnings("ignore")


if __name__ == "__main__":

    ### Fetch data first from binance "2020-08-04"##
    strategy = 'TPRICE'
    sdate = "2018-01-01"
    edate = dt.datetime.today()
    edate = edate.strftime("%Y-%m-%d")
    # edate = "2022-05-12"
    pair = 'ETHBTC' #ETHBTC BTCUSDT
    interval = '8h'
    Direction = "Long" # Long, Short, LS
    commission = 10 ### bps
    fundrate = 0 ### bps
    plot = True
    monthlyStats = False
    fullReport = True
    N = 365

    # 8HR
    dictParams = {'short_ma': [1],  ## {'short_ma': range(10, 1000, 10),
                  'medium_ma': [21],  ## 'long_ma': range(100, 10000, 100),
                  'long_ma': [45],
                  'threshold': [0]}  ## 'long_ma': range(100, 10000, 100)

    # dictParams = {'short_ma': range(1, 5, 1),  ## {'short_ma': range(10, 1000, 10),
    #               'medium_ma': range(9, 18, 2),  ## 'long_ma': range(100, 10000, 100),
    #               'long_ma': range(21, 41, 3),
    #               'threshold': [0]}  ## 'long_ma': range(100, 10000, 100),

    idate = dt.datetime.strptime(sdate, "%Y-%m-%d")
    idate = idate + dt.timedelta(days=-40)
    idate = idate.strftime("%Y-%m-%d")

    klines = client.get_historical_klines(symbol=pair, interval=interval, start_str=idate, end_str=edate)
    finaldata = binanceOHLC(klines)
    finaldata.index = pd.to_datetime(finaldata.index)


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
                                   monthlyStats = monthlyStats, params = row, benchmark = pair, sdate = sdate)

        allrets = strResult['strategyReturns']
        strName = allrets.columns[0]

        if monthlyStats:
            N = 12
            allrets = MonthlyRets(allrets)

        getStats = statistics(allrets, N=N)
        getStats['short_ma'] = row['short_ma']
        getStats['long_ma'] = row['long_ma']
        getStats['threshold'] = row['threshold']

        allPerform = allPerform.append(getStats.iloc[[0]])

        clndRets = trades = math.nan
        if fullReport:

            if not monthlyStats:
                allrets = MonthlyRets(allrets)

            strclndRets = CalendarRets(allrets[[strName]])
            bnchclndRets = CalendarRets(allrets[[pair]])
            trades = strResult['Trades']

        print(getStats,'\n')
        print(f"{strName} Monthly Return", '\n', strclndRets, '\n')
        print(f"{pair} Monthly Return", '\n', bnchclndRets, '\n')
        print(trades,'\n')

    latency = tt.time() - start

    print(f"Iterating {len(params)} {strName} combinations took {latency:.3f} seconds", '\n')

    allPerform = allPerform.sort_values(by='Calmar Ratio', ascending=False)
    print(allPerform)

# strResult['Trades']
# strResult['tradeAction']
strResult['allData']
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

