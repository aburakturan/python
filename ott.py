from binance.client import Client
import pandas as pd
import numpy as np

client = Client('jjIP0g5xq7S1HjBSHLH1Eizw1qpPO0HxUm1P3CqlGUFKKmb7T4vLj7B6AYbqtEgu', '6W9hO9vrVWjMkThl2stbv0OR80Sl83GpkWzwYsIrOrAvPEVTQStLfKbc3bUasttg')

def getCandles():
    df = pd.DataFrame(columns= ['date', 'open', 'high', 'low', 'close', 'volume'])
    candles = client.get_klines(symbol='HOTUSDT', interval=Client.KLINE_INTERVAL_4HOUR)
    opentime, lopen, lhigh, llow, lclose, lvol, closetime = [], [], [], [], [], [], []

    # print(candles)

    for candle in candles:
        opentime.append(candle[0])
        lopen.append(candle[1])
        lhigh.append(candle[2])
        llow.append(candle[3])
        lclose.append(candle[4])
        lvol.append(candle[5])
        closetime.append(candle[6])

    df['date'] = opentime
    df['open'] = np.array(lopen).astype(np.float)
    df['high'] = np.array(lhigh).astype(np.float)
    df['low'] = np.array(llow).astype(np.float)
    df['close'] = np.array(lclose).astype(np.float)
    df['volume'] = np.array(lvol).astype(np.float)
    return df
    # print(df)
    
def OTT(dataframe, *, pds = 2, percent = 1.4):
    """
    Source: https://www.tradingview.com/script/zVhoDQME/
    Author: Anıl Özekşi
    
    Pinescript Developer: KivancOzbilgic
    
    Idea: 
        Buy when Signal line crosses above OTT
        Sell when signal crosses below OTT
        
    usage:
      dataframe['OTT'], dataframe['OTTSignal'] = OTT(dataframe)
    """
    df = dataframe.copy()
    alpha = 2 / (pds + 1)
    
    df['ud1'] = np.where(df['close'] > df['close'].shift(1), df['close'] - df['close'].shift() , 0)
    df['dd1'] = np.where(df['close'] < df['close'].shift(1), df['close'].shift() - df['close'] , 0)
    
    df['UD'] = df['ud1'].rolling(9).sum()
    df['DD'] = df['dd1'].rolling(9).sum()
    df['CMO'] = ((df['UD'] - df['DD']) / (df['UD'] + df['DD'])).fillna(0).abs()
    
    df['Var'] = 0.0
    for i in range(pds, len(df)):
        df['Var'].iat[i] = (alpha * df['CMO'].iat[i] * df['close'].iat[i]) + (1 - alpha * df['CMO'].iat[i]) * df['Var'].iat[i-1]
    df['fark'] = df['Var'] * percent * 0.01
    df['longStop'] = df['Var'] - df['fark']
    df['longStopPrev'] = df['longStop'].shift(1).ffill(limit=1)
    
    df['longStop'] = np.where(df['Var'] > df['longStopPrev'], df[['longStop', 'longStopPrev']].max(axis=1), df['longStop'])
    
    df['shortStop'] = df['Var'] + df['fark']
    df['shortStopPrev'] = df['shortStop'].shift(1).ffill(limit=1)
    df['shortStop'] = np.where(df['Var'] < df['shortStopPrev'], df[['shortStop', 'shortStopPrev']].max(axis=1), df['shortStop'])

    df['dir'] = 1
    # dir = 1
    # dir := nz(dir[1], dir)
    # dir := dir == -1 and Var > shortStopPrev ? 1 : dir == 1 and Var < longStopPrev ? -1 : dir
    df['dir'] = np.where(df['Var'] > df['shortStopPrev'], 1, np.where(df['Var'] < df['longStopPrev'], -1, df['dir']))
    df['MT'] = np.where(df['dir'] == 1, df['longStop'], df['shortStop'])
    df['OTT'] = np.where(df['Var'] > df['MT'], df['MT'] * (200 + percent) / 200, df['MT'] * (200 - percent) / 200)
    
    
    # return df['OTT'], df['Var']
    print(df['OTT'], df['Var'])
    
    




dataframe = getCandles()
# print(dataframe)
OTT(dataframe)