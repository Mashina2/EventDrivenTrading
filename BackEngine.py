from GlobalFunctions import *
from Strategies import *


def BacktestEngine(data,strategy = "SMA", comms = 10, fundrate = 1, plot = True, monthlyStats = False, params = {},
                   benchmark = 'ETHBTC', sdate = '2018-01-01', edate = "2020-01-01"):

    data[benchmark] = data['Close'] / data['Close'].shift(1) - 1

    data = globals()[strategy](data, params)
    data = data[(data.index > sdate) & (data.index <= edate)]
    #
    # data = Stance(ohlc = data, threshold = params['threshold'])
    data = data.dropna(axis=0)
    data['Stance'].value_counts()

    ##### Stance auxiliaries
    stance = data[['Stance']]
    stance['Sub'] = stance.diff(1)
    stance['Plus'] = stance['Stance'].rolling(window=2).sum()
    stance['Sub'][0] = stance['Plus'][0] = stance['Stance'][0]
    stance['Sum'] = stance['Sub'] + stance['Plus']

    ##### Create open buy/close buy/open sell/close sell signals
    pair = data['Close']

    BuyOpen = math.inf * pair.copy()
    BuyClose = math.inf * pair.copy()
    SellOpen = math.inf * pair.copy()
    SellClose = -math.inf * pair.copy()

    BuyOpenRule = (stance['Sub'] > 0) & (stance['Sum'] == 2)
    BuyCloseRule = (stance['Sub'] == 1) & (stance['Sum'] == 0)
    SellOpenRule = (stance['Sub'] < 0) & (stance['Sum'] == -2)
    SellCloseRule = (stance['Sub'] == -1) & (stance['Sum'] == 0)

    BuyOpen.loc[BuyOpenRule] = pair.loc[BuyOpenRule]
    BuyClose.loc[BuyCloseRule] = pair.loc[BuyCloseRule]
    SellOpen.loc[SellOpenRule] = pair.loc[SellOpenRule]
    SellClose.loc[SellCloseRule] = pair.loc[SellCloseRule]

    ### LONG TRADES ANALYSIS
    buyOpenDates = BuyOpen.loc[BuyOpenRule]
    buyOpenDates = buyOpenDates.reset_index()
    sellCloseDates = SellClose.loc[SellCloseRule]
    sellCloseDates = sellCloseDates.reset_index()

    LongTradesAls = {'trade': range(1,len(buyOpenDates) + 1), 'enterTime': buyOpenDates['Close time'],
                      'exitTime': sellCloseDates['Close time'], 'enterPrice': buyOpenDates['Close'],
                      'exitPrice': sellCloseDates['Close']}
    LongTradesAls = pd.DataFrame(data=LongTradesAls)
    LongTradesAls['Return'] = LongTradesAls['exitPrice'] / LongTradesAls['enterPrice'] - 1

    ### SHORT TRADES ANALYSIS
    # sellOpenDates = SellOpen.loc[SellOpenRule]
    # sellOpenDates = sellOpenDates.reset_index()
    # buyCloseDates = BuyClose.loc[BuyCloseRule]
    # buyCloseDates = buyCloseDates.reset_index()
    #
    # ShortTradesAls = {'trade': range(1, len(sellOpenDates) + 1), 'enterTime': sellOpenDates['Close time'],
    #                  'exitTime': buyCloseDates['Close time'], 'enterPrice': sellOpenDates['Close'],
    #                  'exitPrice': buyCloseDates['Close']}
    # ShortTradesAls = pd.DataFrame(data=ShortTradesAls)
    # ShortTradesAls['Return'] = ShortTradesAls['exitPrice'] / ShortTradesAls['enterPrice'] - 1

    ### LONG SHORT TRADES ANALYSIS
    # buyOpenDates = BuyOpen.loc[BuyOpenRule]
    # buyOpenDates = buyOpenDates.reset_index()
    # sellCloseDates = SellClose.loc[SellCloseRule]
    # sellCloseDates = sellCloseDates.reset_index()
    #
    # LongTradesAls = {'trade': range(1, len(buyOpenDates) + 1), 'enterTime': buyOpenDates['Close time'],
    #                  'exitTime': sellCloseDates['Close time'], 'enterPrice': buyOpenDates['Close'],
    #                  'exitPrice': sellCloseDates['Close']}
    # LongTradesAls = pd.DataFrame(data=LongTradesAls)
    # LongTradesAls['Return'] = LongTradesAls['exitPrice'] / LongTradesAls['enterPrice'] - 1
    #



    ### Mark trades
    tradeAction = pd.concat([BuyOpenRule, BuyCloseRule, SellOpenRule, SellCloseRule], axis=1)
    tradeAction.columns = ['Buy Open', 'Buy Close', 'Sell Open', 'Sell Close']

    ### Count them
    Trades = tradeAction.sum(axis = 0)

    ### Make trades readble
    Trades = Trades.to_frame()
    Trades.rename(columns={0: 'Trades'}, inplace=True)
    Trades = Trades.T

    #create strategy daily returns
    # strategy = strategy+" "+params['Direction']
    strategy = f"{strategy} {params['Direction']} #{params['index']}"
    data[strategy] = data[benchmark] * data['Stance'].shift(1)

    # Get trades location
    allTradesLoc = list(np.where(BuyOpenRule)[0]) + list(np.where(BuyCloseRule)[0]) + list(np.where(SellOpenRule)[0]) + \
                   list(np.where(SellCloseRule)[0])
    # [i for i, x in enumerate(SellCloseRule) if x]

    ### Reduce strategy returns by trading commission
    data[strategy][allTradesLoc] = data[strategy][allTradesLoc] - comms / 10**4

    OriginReturn = data[[strategy, benchmark]]
    strategyReturns = OriginReturn.resample('D').sum()
    strategyReturns[strategy] = strategyReturns[strategy] - fundrate / 10 ** 4
    # FinalReturns.groupby(pd.Grouper(freq='D')).sum()
    CumReturns = (1 + strategyReturns).cumprod() - 1

    N = 252
    if monthlyStats:
        strategyReturns = MonthlyRets(strategyReturns)
        CumReturns = (1 + strategyReturns).cumprod() - 1
        N = 12

    if (plot):

        ### Cumulative return plot
        CumReturnsPch = CumReturns * 100
        printPlot(data=CumReturnsPch, title='Cumulative Return', xlabel='Date', ylabel='%')


    result = {}
    result['OriginalReturns'] = OriginReturn
    result['strategyReturns'] = strategyReturns
    result['allData'] = data
    result['Trades'] = Trades
    result['tradeAction'] = tradeAction
    result['LongTradesAls'] = LongTradesAls
    # result['ShortTradesAls'] = ShortTradesAls

    return result
