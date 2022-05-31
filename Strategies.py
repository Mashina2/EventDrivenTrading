from GlobalFunctions import *


def SMA(ohlc, params):

    short_ma = int(params['short_ma'])
    long_ma = int(params['long_ma'])

    ohlc['short_ma'] = ohlc['Close'].rolling(window=short_ma).mean()
    ohlc['long_ma'] = ohlc['Close'].rolling(window=long_ma).mean()
    ohlc['FACTOR'] = ohlc['short_ma'] / ohlc['long_ma'] - 1

    threshold = params['threshold']
    direction = params['Direction']

    if direction == "Long":
        ohlc['Stance'] = np.where(ohlc['FACTOR'] > threshold, 1, 0)
        ohlc['Stance'] = np.where(ohlc['FACTOR'] < -threshold, 0, ohlc['Stance'])
    elif direction == "Short":
        ohlc['Stance'] = np.where(ohlc['FACTOR'] > threshold, 0, 0)
        ohlc['Stance'] = np.where(ohlc['FACTOR'] < -threshold, -1, ohlc['Stance'])
    elif direction == "LS":
        ohlc['Stance'] = np.where(ohlc['FACTOR'] > threshold, 1, 0)
        ohlc['Stance'] = np.where(ohlc['FACTOR'] < -threshold, -1, ohlc['Stance'])
    else:
        raise Exception("direction should be 'Long', 'Short', 'LS'")

    return ohlc

def TSMA(ohlc, params):

    short_ma = int(params['short_ma'])
    medium_ma = int(params['medium_ma'])
    long_ma = int(params['long_ma'])

    ohlc['short_ma'] = ohlc['Close'].rolling(window=short_ma).mean()
    ohlc['medium_ma'] = ohlc['Close'].rolling(window=medium_ma).mean()
    ohlc['long_ma'] = ohlc['Close'].rolling(window=long_ma).mean()

    ohlc['FACTOR1'] = ohlc['short_ma'] / ohlc['medium_ma'] - 1
    ohlc['FACTOR2'] = ohlc['short_ma'] / ohlc['long_ma'] - 1

    threshold = params['threshold']
    direction = params['Direction']

    if direction == "Long":
        ohlc['Stance'] = np.where((ohlc['FACTOR1'] > threshold) & (ohlc['FACTOR2'] > threshold), 1, 0)
        ohlc['Stance'] = np.where(ohlc['FACTOR1'] < -threshold, 0, ohlc['Stance'])
    elif direction == "Short":
        ohlc['Stance'] = np.where((ohlc['FACTOR1'] < threshold) & (ohlc['FACTOR2'] < threshold), -1, 0)
        ohlc['Stance'] = np.where(ohlc['FACTOR1'] > threshold, 0, ohlc['Stance'])
    elif direction == "LS":
        ohlc['Stance'] = np.where((ohlc['FACTOR1'] > threshold) & (ohlc['FACTOR2'] > threshold), 1, 0)
        ohlc['Stance'] = np.where((ohlc['FACTOR1'] < threshold) & (ohlc['FACTOR2'] < threshold), -1, ohlc['Stance'])
    else:
        raise Exception("direction should be 'Long', 'Short', 'LS'")

    # newRes = Stance(ohlc = result, threshold = 0)

    return ohlc

def TPRICE(ohlc, params):

    short_ma = int(params['short_ma'])
    medium_ma = int(params['medium_ma'])
    long_ma = int(params['long_ma'])

    ohlc['short_ma'] = ohlc['Close'].shift(short_ma-1)
    ohlc['medium_ma'] = ohlc['Close'].shift(medium_ma-1)
    ohlc['long_ma'] = ohlc['Close'].shift(long_ma-1)

    ohlc['FACTOR1'] = ohlc['short_ma'] / ohlc['medium_ma'] - 1
    ohlc['FACTOR2'] = ohlc['short_ma'] / ohlc['long_ma'] - 1

    threshold = params['threshold']
    direction = params['Direction']

    if direction == "Long":
        ohlc['Stance'] = np.where((ohlc['FACTOR1'] > threshold) & (ohlc['FACTOR2'] > threshold), 1, 0)
        ohlc['Stance'] = np.where(ohlc['FACTOR1'] < -threshold, 0, ohlc['Stance'])
    elif direction == "Short":
        ohlc['Stance'] = np.where((ohlc['FACTOR1'] < threshold) & (ohlc['FACTOR2'] < threshold), -1, 0)
        ohlc['Stance'] = np.where(ohlc['FACTOR1'] > threshold, 0, ohlc['Stance'])
    elif direction == "LS":
        ohlc['Stance'] = np.where((ohlc['FACTOR1'] > threshold) & (ohlc['FACTOR2'] > threshold), 1, 0)
        ohlc['Stance'] = np.where((ohlc['FACTOR1'] < threshold) & (ohlc['FACTOR2'] < threshold), -1, ohlc['Stance'])
    else:
        raise Exception("direction should be 'Long', 'Short', 'LS'")

    # newRes = Stance(ohlc = result, threshold = 0)

    return ohlc
