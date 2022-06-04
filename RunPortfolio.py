from BinanceAPI import *
from GlobalFunctions import *
from Strategies import *
from BackEngine import *
import time as tt

import warnings
warnings.filterwarnings("ignore")

if __name__ == "__main__":

    ### Fetch data first from binance "2020-08-04"##
    sdate = "2018-01-01"
    edate = dt.datetime.today()
    edate = edate.strftime("%Y-%m-%d")
    # edate = "2022-05-12"
    commission = 10 ### bps
    fundrate = 0 ### bps
    plot = True
    monthlyStats = False
    fullReport = True
    N = 365

    # 8HR
    dictParams = {'PORT1': {'str':'TSMA', 'pair': 'ETHUSDT', 'interval': '8h', 'Direction':'Long',
                            'short_ma': 1, 'medium_ma': 7, 'long_ma': 10, 'threshold': 0},
                  'PORT2': {'str':'TSMA', 'pair': 'BTCUSDT', 'interval': '4h', 'Direction':'Long',
                            'short_ma': 1, 'medium_ma': 10, 'long_ma': 12, 'threshold': 0},
                  'PORT3': {'str':'TPRICE', 'pair': 'BNBUSDT', 'interval': '1d', 'Direction':'Long',
                            'short_ma': 1, 'medium_ma': 15, 'long_ma': 40, 'threshold': 0}
                  }

    params = pd.DataFrame(dictParams)
    params = params.T
    start = tt.time()

    allPerform = pd.DataFrame()
    mulrets = pd.DataFrame()
    cols = []

    for index, row in params.iterrows():

        print('\n', '---------------Now doing combination ' f"{index}/{len(params)}---------------", '\n')

        row['index'] = index
        pair = row['pair']
        interval = row['interval']

        idate = dt.datetime.strptime(sdate, "%Y-%m-%d")
        idate = idate + dt.timedelta(days=-40)
        idate = idate.strftime("%Y-%m-%d")

        klines = client.get_historical_klines(symbol=pair, interval=interval, start_str=idate, end_str=edate)
        finaldata = binanceOHLC(klines)
        finaldata.index = pd.to_datetime(finaldata.index)

        strategy = row['str']
        strResult = BacktestEngine(data = finaldata, strategy = strategy, plot = plot, comms=commission, fundrate = fundrate,
                                   monthlyStats = monthlyStats, params = row, benchmark = pair, sdate = sdate)

        allrets = strResult['strategyReturns']
        strName = allrets.columns[0]
        cols.append(strName)
        mulrets = mulrets.append(allrets[strName], ignore_index=True)

        if monthlyStats:
            N = 12
            allrets = MonthlyRets(allrets)

        getStats = statistics(allrets, N=N)
        getStats['short_ma'] = row['short_ma']
        getStats['medium_ma'] = row['medium_ma']
        getStats['long_ma'] = row['long_ma']
        # getStats['threshold'] = row['threshold']

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

    print(f"Iterating {len(dictParams)} {strName} combinations took {latency:.3f} seconds", '\n')

    print('\n', "---------------Rank portfolios by Sharpe Ratio---------------", '\n')

    allPerform = allPerform.sort_values(by='Sharpe Ratio', ascending=False)
    print(allPerform)

    print('\n', "---------------Now doing Portfolio calculation---------------", '\n')

    #### Portfolio performance
    mulrets = mulrets.T
    # pairs = dictParams['pair']
    mulrets.columns = cols

    str(mulrets.index[[0]])

    # Convert DatetimeIndex to String.
    strDates = mulrets.index.strftime('%Y-%m-%d')
    sdate = strDates[0]
    edate = strDates[-1]
    weight = [1/len(cols)] * len(cols)

    port = portfolioConstruct(returns = mulrets, sdate=sdate, edate=edate,
                              positions=weight, increment=1,period='weeks')

    portStats = statistics(port, N=N)
    if not monthlyStats:
        port = MonthlyRets(port)

    corrMtx = port.corr()
    strclndPort = CalendarRets(port[['Portfolio']])

    print('\n', portStats, '\n')
    print(corrMtx, '\n')

    print(f"Portfolio Monthly Return", '\n', strclndPort, '\n')

    cumRets = (1 + port).cumprod() - 1
    cumRets = cumRets * 100

    runPlot(cumRets, title=strategy + ' Cumulative Return', xlabel='Date', ylabel='%')

# df = pd.DataFrame.from_dict(mulrets, orient='columns')


# strResult['Trades']
# strResult['tradeAction']
# strResult['allData']
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

