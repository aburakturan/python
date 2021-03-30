from binance.client import Client
import pandas as pd
import numpy as np
import sys
import time



from sys import maxsize
from numpy import set_printoptions


from pymongo import MongoClient, DESCENDING, ASCENDING

client = MongoClient('localhost',27017)  # 27017 is the default port number for mongodb

db = client.pmax
col = db.data


set_printoptions(threshold=maxsize)


def setInterval(func,time):
    e = threading.Event()
    while not e.wait(time):
        func()


client = Client('jjIP0g5xq7S1HjBSHLH1Eizw1qpPO0HxUm1P3CqlGUFKKmb7T4vLj7B6AYbqtEgu', '6W9hO9vrVWjMkThl2stbv0OR80Sl83GpkWzwYsIrOrAvPEVTQStLfKbc3bUasttg')

def getCandles(asset):
    df = pd.DataFrame(columns= ['date', 'open', 'high', 'low', 'close', 'volume'])
    candles = client.get_klines(symbol=asset, interval=Client.KLINE_INTERVAL_4HOUR)
    opentime, lopen, lhigh, llow, lclose, lvol, closetime = [], [], [], [], [], [], []


    for candle in candles:
        opentime.append(candle[0])
        lopen.append(candle[1])
        lhigh.append(candle[2])
        llow.append(candle[3])
        lclose.append(candle[4])
        lvol.append(candle[5])
        closetime.append(candle[6])

    df['date'] = opentime
    df['open'] = np.array(lopen).astype(np.float64)
    df['high'] = np.array(lhigh).astype(np.float64)
    df['low'] = np.array(llow).astype(np.float64)
    df['close'] = np.array(lclose).astype(np.float64)
    df['volume'] = np.array(lvol).astype(np.float64)
    return df

def PMAX(dataframe, period=2, multiplier=1.4, length=2, MAtype=7, src=1):
    import talib.abstract as ta
    df = dataframe.copy()
    mavalue = 'MA_' + str(MAtype) + '_' + str(length)
    atr = 'ATR_' + str(period)
    df[atr] = ta.ATR(df, timeperiod=period)
    pm = 'pm_' + str(period) + '_' + str(multiplier) + '_' + str(length) + '_' + str(MAtype)
    pmx = 'pmX_' + str(period) + '_' + str(multiplier) + '_' + str(length) + '_' + str(MAtype)

    if src == 1:
        masrc = df["close"]
    elif src == 2:
        masrc = (df["high"] + df["low"]) / 2
    elif src == 3:
        masrc = (df["high"] + df["low"] + df["close"] + df["open"]) / 4
    if MAtype == 1:
        df[mavalue] = ta.EMA(masrc, timeperiod=length)
    elif MAtype == 2:
        df[mavalue] = ta.DEMA(masrc, timeperiod=length)
    elif MAtype == 3:
        df[mavalue] = ta.T3(masrc, timeperiod=length)
    elif MAtype == 4:
        df[mavalue] = ta.SMA(masrc, timeperiod=length)
    elif MAtype == 5:
        df[mavalue] = VIDYA(df, length=length)
    elif MAtype == 6:
        df[mavalue] = ta.TEMA(masrc, timeperiod=length)
    elif MAtype == 7:
        df[mavalue] = ta.WMA(df, timeperiod=length)
    elif MAtype == 8:
        df[mavalue] = vwma(df, length)
    elif MAtype == 9:
        df[mavalue] = zema(df, period=length)
    # Compute basic upper and lower bands
    df['basic_ub'] = df[mavalue] + (multiplier * df[atr])
    df['basic_lb'] = df[mavalue] - (multiplier * df[atr])
    # Compute final upper and lower bands
    df['final_ub'] = 0.00
    df['final_lb'] = 0.00
    for i in range(period, len(df)):
        df['final_ub'].iat[i] = df['basic_ub'].iat[i] if (
            df['basic_ub'].iat[i] < df['final_ub'].iat[i - 1]
            or df[mavalue].iat[i - 1] > df['final_ub'].iat[i - 1]) else df['final_ub'].iat[i - 1]
        df['final_lb'].iat[i] = df['basic_lb'].iat[i] if (
            df['basic_lb'].iat[i] > df['final_lb'].iat[i - 1]
            or df[mavalue].iat[i - 1] < df['final_lb'].iat[i - 1]) else df['final_lb'].iat[i - 1]

    df[pm] = 0.00
    for i in range(period, len(df)):
        df[pm].iat[i] = (
            df['final_ub'].iat[i] if (df[pm].iat[i - 1] == df['final_ub'].iat[i - 1]
                                      and df[mavalue].iat[i] <= df['final_ub'].iat[i])
            else df['final_lb'].iat[i] if (
                df[pm].iat[i - 1] == df['final_ub'].iat[i - 1]
                and df[mavalue].iat[i] > df['final_ub'].iat[i]) else df['final_lb'].iat[i]
            if (df[pm].iat[i - 1] == df['final_lb'].iat[i - 1]
                and df[mavalue].iat[i] >= df['final_lb'].iat[i]) else df['final_ub'].iat[i]
            if (df[pm].iat[i - 1] == df['final_lb'].iat[i - 1]
                and df[mavalue].iat[i] < df['final_lb'].iat[i]) else 0.00)

    # Mark the trend direction up/down
    df[pmx] = np.where((df[pm] > 0.00), np.where((df[mavalue] < df[pm]), 'down',  'up'), np.NaN)
    # Remove basic and final bands from the columns
    df.drop(['basic_ub', 'basic_lb', 'final_ub', 'final_lb'], inplace=True, axis=1)

    df.fillna(0, inplace=True)

    return df

# TRXUSDT


assets = ["QTUMUSDT", "XRPUSDT", "EOSUSDT",  "TUSDUSDT", "VETUSDT", "PAXUSDT", "LINKUSDT", "BTTUSDT", "ONGUSDT", "HOTUSDT", "ZILUSDT", "ZECUSDT", "IOSTUSDT", "CELRUSDT", "DASHUSDT", "NANOUSDT", "OMGUSDT", "THETAUSDT", "TFUELUSDT", "ONEUSDT", "FTMUSDT", "GTOUSDT", "DOGEUSDT", "DUSKUSDT", "ANKRUSDT", "WINUSDT", "COSUSDT", "NPXSUSDT", "MTLUSDT", "TOMOUSDT", "PERLUSDT", "DENTUSDT", "MFTUSDT", "KEYUSDT", "CVCUSDT", "CHZUSDT", "BUSDUSDT", "BEAMUSDT", "STXUSDT", "IOTXUSDT", "TROYUSDT", "DREPUSDT", "WRXUSDT", "BTSUSDT", "LSKUSDT", "LTOUSDT", "MBLUSDT", "COTIUSDT", "STPTUSDT", "HIVEUSDT", "CHRUSDT", "GXSUSDT", "ARDRUSDT", "STMXUSDT", "REPUSDT", "COMPUSDT", "SCUSDT", "ZENUSDT", "SXPUSDT", "STORJUSDT", "YFIUSDT", "BALUSDT", "JSTUSDT", "SRMUSDT", "ANTUSDT", "CRVUSDT", "DOTUSDT", "LUNAUSDT", "RSRUSDT", "TRBUSDT", "YFIIUSDT", "KSMUSDT", "UMAUSDT", "NBSUSDT", "OXTUSDT", "SUNUSDT", "AVAXUSDT", "HNTUSDT", "FLMUSDT", "ORNUSDT", "INJUSDT", "CTKUSDT", "AKROUSDT", "DNTUSDT", "STRAXUSDT", "AVAUSDT", "XEMUSDT", "SUSDUSDT", "1INCHUSDT", "REEFUSDT", "TRUUSDT", "CKBUSDT", "TWTUSDT", "LITUSDT", "DODOUSDT", "BADGERUSDT", "FISUSDT", "LINAUSDT", "PERPUSDT"]
# assets = ["TRXUSDT","QTUMUSDT"]

# for val in assets:
#     print(val)
#     time.sleep(5)


def do(asset):
    result = PMAX(getCandles(asset))
    
    _last_pmax = col.find_one(
        {'asset': asset},
        sort=[( '_id', DESCENDING )]
    )
    
    if (result['pmX_2_1.4_2_7'][499] != None):
        current_pmax = result['pmX_2_1.4_2_7'][499]

        if (_last_pmax != None):
            last_pmax = _last_pmax['pmax']

            if (last_pmax != current_pmax):
                if(current_pmax == "down"):
                    print('düşüş başladı')
                else:
                    print('Yükseliş başladı')

            print(asset)
            print(asset)
            print('new data')
            print(current_pmax)
            print(result)
            print('old data')
            print(last_pmax)
            print(_last_pmax)
            print('------')

        col.insert_one(
            {
                'asset': asset,
                'pmax': result['pmX_2_1.4_2_7'][499] ,
                'price': result['close'][499] ,
            }
        )




i = 0
while i < len(assets):
  do(assets[i])
  i += 1
  time.sleep(1)
  if (i == len(assets)):
    i = 0



# result = PMAX(getCandles())

# for val in result['pmX_2_1.4_2_7']:
#     print(val)

# print(result)


# print(result['pmX_2_1.4_2_7'][497])
# print(result['pmX_2_1.4_2_7'][498])
# print(result['pmX_2_1.4_2_7'][499])
    
# col.insert_one(
#    {
#       'name': "HOTUSDT",
#       'salary': result['pmX_2_1.4_2_7'][499] ,
#    }
# )


