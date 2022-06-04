import pickle
import csv
import os
import sys
import time
import math
import pandas as pd
import numpy as np
import datetime as dt
from itertools import product
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt


# set pandas size
pd.set_option('display.width', 300)
pd.set_option('display.max_columns', 30)
pd.set_option('display.max_rows', 150)
# pd.set_option('precision', 5)
pd.set_option('mode.chained_assignment', None) ## turning off SettingWithCopyWarning


storePath = 'C:/StoredFiles/'

def savepkl(filename, data):
    filename = storePath + filename + '.pkl'
    outfile = open(filename, "wb")
    pickle.dump(data, outfile)
    outfile.close()

def readpkl(filename):
    filename = storePath + filename + '.pkl'
    infile = open(filename, 'rb')
    result = pickle.load(infile)
    infile.close()
    return result


def printPlot(data, title='DrawDown', xlabel='Date', ylabel='%'):
    data.plot(grid=True, figsize=(8, 5))
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()


def IntegertoDatatime(Timestamp):

    result = [dt.datetime.fromtimestamp(int(x) / 1000) for x in Timestamp]
    result = [x.strftime('%Y-%m-%d %H:%M:%S') for x in result]

    return result



def expand_grid(dictionary):
   return pd.DataFrame([row for row in product(*dictionary.values())],
                       columns=dictionary.keys())


def annualised_sharpe_mean(returns, N=252):
    return np.sqrt(N) * (returns.mean() / returns.std())


def annualised_sharpe(returns, N=252):

    annRet = (1 + returns).prod() ** np.sqrt(N / len(returns)) - 1
    annVol = returns.std() * np.sqrt(N)
    sharpe = annRet / annVol

    return sharpe

def maxDD(rets):

    nav = (1 + rets).cumprod()
    previous_peaks = nav.cummax()
    drawdown = (nav - previous_peaks) / previous_peaks
    return drawdown


def date_range(start_date, end_date, increment, period):
    result = []
    nxt = start_date
    delta = relativedelta(**{period: increment})
    while nxt <= end_date:
        result.append(nxt)
        nxt += delta
    return result

def date_sequence(start_date="2017-01-24", end_date="2017-05-12", increment=1, period='months'):

    sdate = dt.datetime.strptime(start_date, '%Y-%m-%d')
    edate = dt.datetime.strptime(end_date, '%Y-%m-%d')

    drange = date_range(sdate, edate, increment, period)
    drangeStr = [i.strftime('%Y-%m-%d') for i in drange]
    drangeStr = drangeStr + [edate.strftime('%Y-%m-%d')]
    finalRange = sorted(set(drangeStr))

    return finalRange


def weightEval(returns):

    # Add zero row and remove last return observation
    dates = returns.index
    zero = pd.DataFrame([[0] * returns.shape[1]], columns=returns.columns)
    finalRets = zero.append(returns, ignore_index=True)
    finalRets = finalRets.iloc[:(len(finalRets) - 1)]
    finalRets.index = dates

    # calculate cumulative returns
    crets = (finalRets + 1).cumprod()
    # find number of columns
    length = crets.shape[1]
    # calculate initial weight for each asset
    eqweight = 1 / length
    # create a weights matrix
    weights = np.tile(eqweight, length)
    # multiply weights array with crets to find cumulaitve wealth
    wealthmat = crets.multiply(weights, axis=1)
    # find sum of rows
    tsum = wealthmat.sum(axis=1)
    # get weight matrix
    weigthmat = wealthmat.multiply(1 / tsum, axis=0)

    return weigthmat

def portfolioByRets(returns, positions = [1.2, -0.8]):

    nav = (1+returns).cumprod()
    # create a weights matrix

    # multiply weights array with crets to find cumulaitve wealth
    wealthmat = nav.multiply(positions, axis=1)
    firstObs = pd.DataFrame([positions], columns=returns.columns)
    # calc nav, diff and sum it
    finalNav = firstObs.append(wealthmat, ignore_index=False)
    diffNAV = finalNav.diff(periods=1, axis=0)
    sumNAV = diffNAV.sum(axis = 1)
    cumNav = 1+ sumNAV.cumsum()

    ## calc portfolio return
    portReturn = cumNav / cumNav.shift(1) - 1
    portReturn = portReturn.drop(portReturn.index[[0]])
    portReturn = portReturn.to_frame()
    portReturn.rename(columns={0: 'Portfolio'}, inplace=True)

    return portReturn

def portfolioConstruct(returns, sdate = '2002-03-01', edate = '2009-09-12', positions = [1.2, -0.8], increment=1, period='months'):

    cleanRets = returns[sdate:edate]
    mrange = date_sequence(start_date=sdate, end_date=edate, increment=increment, period=period)
    mrange = [dt.datetime.strptime(i, '%Y-%m-%d') for i in mrange]

    Portfolio = pd.DataFrame()
    for i in range(0, len(mrange) - 1):

        evalStart = mrange[i] + dt.timedelta(days=1)
        if (i == 0):
            evalStart = mrange[i]

        evalStart = evalStart.strftime('%Y-%m-%d')
        evalEnd = mrange[i + 1]
        evalEnd = evalEnd.strftime('%Y-%m-%d')

        crets = cleanRets.loc[evalStart:evalEnd]
        getPort =  portfolioByRets(crets, positions=positions)
        Portfolio = Portfolio.append(getPort)

    cleanRets['Portfolio'] = Portfolio

    return cleanRets

def runPlot(data, title = 'Cumulative Return', xlabel = 'Date', ylabel = '%'):
    data.plot(grid=True, figsize=(8, 5))
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()


def statistics(rets, N=252):

    stats = pd.DataFrame()
    stats['Cum. Return'] = (1 + rets).prod() - 1
    stats['Ann. Return'] = (1 + rets).prod() ** np.sqrt(N / len(rets)) - 1
    stats['Ann. Vol'] = rets.std() * np.sqrt(N)
    stats['Max DD'] = maxDD(rets).min()
    stats['Sharpe Ratio'] = stats['Ann. Return'] / stats['Ann. Vol']
    stats['Calmar Ratio'] = stats['Ann. Return'] / abs(stats['Max DD'])

    if len(rets.columns) == 2:
        resetRets = rets.reset_index(drop=True)
        correlation = resetRets.iloc[:,0].corr(resetRets.iloc[:,1])
        stats['Correlation'] = [correlation, 1]

    stats = round(stats, 2) * 100
    stats[['Sharpe Ratio', 'Calmar Ratio']] = stats[['Sharpe Ratio', 'Calmar Ratio']] / 100

    return stats



def MonthlyRets(dailyRets):

    dates = pd.to_datetime(dailyRets.index)
    dates = [i.strftime("%Y-%m-%d") for i in dates]
    dailyRets.index = pd.to_datetime(dates)
    monRets = dailyRets.resample('M').agg(lambda x: (x + 1).prod() - 1)
    # rets.resample('W-FRI').agg(lambda x: (x + 1).prod() - 1)
    return monRets

def CalendarRets(monRets):

    adjRets = round(monRets, 4)
    adjRets['years'] = list(adjRets.index.year)
    adjRets['months'] =  list(adjRets.index.month)


    years = list(monRets.index.year.unique())
    years = years[::-1]
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    calendar = pd.DataFrame(index=years, columns=months)
    for i in range(0, len(calendar)):

        cyear = calendar.index[i]

        for j in range(0, 12):
            cmonth = j + 1

            try:
                valDate = adjRets[(adjRets['years'] == cyear) & (adjRets['months'] == cmonth)]
                varRet = valDate.iloc[0, 0]
            except:
                # varRet = ''
                continue

            calendar.iloc[i,j] = varRet

    calendar['YTD'] = calendar.apply(lambda x: (x + 1).prod() - 1, axis=1)
    calendar['YTD'] = round(calendar['YTD'], 4)
    calendar = calendar * 100
    calendar = calendar.fillna('')

    return calendar


def splitDeribitInstrument(instruments):

    symbol = []
    expiration = []
    strike = []
    right = []

    for x in instruments:
        spinstr = x.split("-")
        symbol.append(spinstr[0])
        expiration.append(spinstr[1])
        strike.append(spinstr[2])
        right.append(spinstr[3])

    strike = [float(i) for i in strike]
    expiration = pd.to_datetime(expiration, format='%d%b%y')

    result = {'symbol': symbol, 'expiration': expiration, 'strike': strike, 'right': right}
    return result

def PortfolioTable(portfolio):

    tuples = []

    for Contracts in portfolio:

        Account = Contracts.account
        position = Contracts.position
        avgCost = Contracts.averageCost
        marketPrice = Contracts.marketPrice
        marketValue = Contracts.marketValue
        realizedPNL = Contracts.realizedPNL
        unrealizedPNL = Contracts.unrealizedPNL

        symbol = Contracts.contract.symbol
        localSymbol = Contracts.contract.localSymbol
        currency = Contracts.contract.currency
        primaryExchange = Contracts.contract.primaryExchange

        try:
            lastTrade = Contracts.contract.lastTradeDateOrContractMonth
            multiplier = Contracts.contract.multiplier
            strike = Contracts.contract.strike
            secType = Contracts.contract.secType
            right = Contracts.contract.right

        except:
            lastTrade = math.nan
            multiplier = 1
            strike = math.nan
            secType = math.nan
            right = math.nan

        tup = (
            Account,
            symbol,
            localSymbol,
            position,
            avgCost,
            marketPrice,
            marketValue,
            realizedPNL,
            unrealizedPNL,
            currency,
            primaryExchange,
            lastTrade,
            multiplier,
            strike,
            secType,
            right
        )
        tuples.append(tup)
    df = pd.DataFrame.from_records(tuples,
                                   columns=["Account", "symbol", "localSymbol", "position", 'avgCost', "marketPrice",
                                            "marketValue","realizedPNL","unrealizedPNL","currency","primaryExchange",
                                            "lastTrade", "multiplier","strike", 'secType', "right"])
    # df = df.set_index(["symbol"], drop=True)
    return df


def IBpositionsTable(port, tickers_list, MarginReq):

    result = []

    for x, y, z in zip(port, tickers_list, MarginReq):

        ### Check symbols are matched
        symbol1 = x.contract.symbol
        symbol2 = y.contract.symbol
        symbol3 = z['symbol']


        if (not(symbol1 == symbol2 == symbol3)):
            raise Exception("symbol " + symbol1 + " Don't match to symbol " + symbol2 + " or symbol3 " + symbol3)

        cleanData = {}
        cleanData['Account'] = x.account
        cleanData['position'] = x.position
        cleanData['avgCost'] = x.averageCost
        cleanData['marketPrice'] = x.marketPrice
        cleanData['marketValue'] = x.marketValue
        cleanData['realizedPNL'] = x.realizedPNL
        cleanData['unrealizedPNL'] = x.unrealizedPNL
        cleanData['symbol'] = x.contract.symbol
        cleanData['localSymbol'] = x.contract.localSymbol
        cleanData['secType'] = x.contract.secType
        cleanData['currency'] = x.contract.currency
        cleanData['primaryExchange'] = x.contract.primaryExchange
        cleanData['MarginReq'] = z['InitMarginChange']

        try:
            cleanData['lastTrade'] = x.contract.lastTradeDateOrContractMonth
        except:
            cleanData['lastTrade'] = math.nan

        try:
            cleanData['multiplier'] = x.contract.multiplier
        except:
            cleanData['multiplier'] = 1

        try:
            cleanData['strike'] = x.contract.strike
        except:
            cleanData['strike'] = math.nan

        try:
            cleanData['right'] = x.contract.right
        except:
            cleanData['right'] = math.nan

        try:
            cleanData['undPrice'] = y.lastGreeks.undPrice  ### Should be modelGreeks once I'm fully subscribed (it has more data)
            cleanData['delta'] = y.modelGreeks.delta  ### Should be modelGreeks once I'm fully subscribed (it has more data)

            if cleanData['secType'] == 'STK':
                cleanData['undPrice'] = y.last
        except:
            cleanData['undPrice'] = math.nan
            cleanData['delta']  = math.nan

        cleanData['bid'] = y.bid
        cleanData['ask'] = y.ask

        result.append(cleanData)

    return result

def ClusterReport(finalOpt, cluster='symbol'):

    keys = finalOpt[cluster].unique()
    col1 = 'CumPRM'
    col2 = 'LeftPRM'
    col3 = 'LeftdeltaPRM'
    col4 = 'CumLeftdeltaPRM'

    classReport = {}
    for i in range(0, len(keys)):
        crep = finalOpt[finalOpt[cluster] == keys[i]]
        crep[col1] = round(crep[col2].cumsum(), 3)
        crep[col4] = round(crep[col3].cumsum(), 3)
        classReport[keys[i]] = crep

    smry = {cluster: [], 'CALL': [], 'PUT': [], 'MarginReq': [], col2: [], col3: []}
    for x in keys:
        smry[cluster].append(x)
        smry['CALL'].append(classReport[x].loc[classReport[x]['right'] == 'C', 'position'].sum())
        smry['PUT'].append(classReport[x].loc[classReport[x]['right'] == 'P', 'position'].sum())
        smry['MarginReq'].append(classReport[x]['MarginReq'].sum())
        smry[col2].append(classReport[x][col2].sum())
        smry[col3].append(classReport[x][col3].sum())

    smry = pd.DataFrame(smry)
    # smry[col1] = round(smry[col2].cumsum(), 3)
    # smry[col4] = round(smry[col3].cumsum(), 3)
    smry[col1] = smry[col2].cumsum()
    smry[col4] = smry[col3].cumsum()

    result = {'classReport': classReport, 'summary': smry}

    return result




### Find where python is installed in my computer
# os.path.dirname(sys.executable)


# filename = storePath + 'TradesDA' + '.csv'
# with open(filename, newline='') as csvfile:
#     # spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
#     spamreader = csv.reader(csvfile)
#     for row in spamreader:
#         print(', '.join(row))


# csv = pd.read_csv(filename)


def round_price_from_rules(price, exchange, details, rules):
    # the exchange is the exchange selected for the order, normally SMART
    # details are the details for the instrument
    # rules is the dictionary of rules
    # First find the rule ID to use for the target exchange
    selected_id = None
    rule_ids = [int(x) for x in details.marketRuleIds.split(",")]
    exchanges = details.validExchanges.split(",")
    for rule_exchange, rule_id in zip(exchanges, rule_ids):
        if rule_exchange == exchange:
            selected_id = rule_id
    if selected_id not in rules:
        print("No valid rule found")
        raise AttributeError
    min_tick = None
    # note that we use the absolute value or price
    for low_edge, tick in rules[selected_id]:
        if low_edge <= abs(price):
            min_tick = tick
    return round_price(price, min_tick)

def round_price(price, min_tick, fmt="%.4f"):
    # this code needs to use string processing to avoid floating point issues
    # the initial code fails because e.g. 188 * 0.01 = 1.8800000000000001
    # deep down, the IB API python code uses simply str(val), no formatting
    # so we transform back and forth from string to float
    rounded = round(price/min_tick) * min_tick
    # ideally the size should depend on min_tick, but 4 should be enough for most instruments
    truncated = float(fmt % rounded)
    return truncated

def active_order(ib, symbol, directions=["SELL"]):
    # confusingly, ib_insync calls trades what is generally called an order
    # note that this code will *not* work across session
    api_trades = list(ib.openTrades())
    for trade in api_trades:
        if trade.contract.localSymbol != symbol: continue
        if trade.order.action not in directions: continue
        return True
    return False

def matching_trades(trades, symbol="", ref_pattern="", action=""):
    matching = []
    for trade in trades:
        if symbol and trade.contract.localSymbol != symbol:
            continue
        if ref_pattern and ref_pattern not in trade.order.orderRef:
            continue
        if action and action != trade.order.action:
            continue
        matching.append(trade)
    return matching


def matching_fills(fills, symbol="", ref_pattern="", action=""):
    matching = []
    for fill in fills:
        if symbol and symbol != fill.contract.localSymbol:
            continue
        # note that the orderRef is inside execution, there is no order inside a fill
        if ref_pattern and ref_pattern not in fill.execution.orderRef:
            continue
        # action is BOT or SOLD for an execution
        if action == "BUY":
            action = "BOT"
        if action == "SELL":
            action = "SOLD"
        if action and action != fill.execution.side:
            continue
        matching.append(fill)
    return matching

def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier


def modifyOHLCtime(OHLC,currentInterval = '1h',desiredInterval = '24h', desiredHour = '18'):

    firstDate = OHLC.index[0]
    desireDate = firstDate.replace(hour=int(desiredHour))

    OHLC = OHLC[OHLC.index > desireDate]

    # daily = finaldata.head(10)

    currentInterval = int(currentInterval[:-1])
    desireInterval = int(desiredInterval[:-1])
    obs = desireInterval / currentInterval
    loop = math.floor(len(OHLC)/obs)

    result = math.inf * OHLC.copy()
    result = result.iloc[0:loop]
    result = result.reset_index()

    highFreqData = OHLC.reset_index()

    for i in range(loop):
        result['Close time'].iloc[i] = highFreqData['Close time'].iloc[int(obs*(i+1)-1)]
        result['Open'].iloc[i] = highFreqData['Open'].iloc[int(obs*(i + 1)-obs)]
        result['Close'].iloc[i] = highFreqData['Close'].iloc[int(obs * (i + 1)-1)]
        result['High'].iloc[i] = max(highFreqData['High'].iloc[range(int(obs*(i + 1)-obs),int(obs * (i + 1)))])
        result['Low'].iloc[i] = min(highFreqData['Low'].iloc[range(int(obs * (i + 1) - obs), int(obs * (i + 1)))])
        result['Volume'].iloc[i] = highFreqData['Volume'].iloc[range(int(obs * (i + 1) - obs), int(obs * (i + 1)))].sum()
        result['Number of trades'].iloc[i] = highFreqData['Number of trades'].iloc[range(int(obs * (i + 1) - obs), int(obs * (i + 1)))].sum()

    return result
