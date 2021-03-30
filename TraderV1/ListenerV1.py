from binance.client import Client
import pandas as pd
import numpy as np
import sys
import time
from datetime import datetime
import json
from sys import maxsize
from numpy import set_printoptions
from pymongo import MongoClient, DESCENDING, ASCENDING
import Notify
from ansimarkup import ansiprint as print
from pyfiglet import Figlet

f = Figlet(font='slant')


client = MongoClient('localhost',27017)  

db = client.pmaxV1
bought = db.bought
sold = db.sold

set_printoptions(threshold=maxsize)

def setInterval(func,time):
    e = threading.Event()
    while not e.wait(time):
        func()
 
client = Client('jjIP0g5xq7S1HjBSHLH1Eizw1qpPO0HxUm1P3CqlGUFKKmb7T4vLj7B6AYbqtEgu', '6W9hO9vrVWjMkThl2stbv0OR80Sl83GpkWzwYsIrOrAvPEVTQStLfKbc3bUasttg')

def getCandles(asset):
    df = pd.DataFrame(columns= ['date', 'open', 'high', 'low', 'close', 'volume'])
    
    try:
        candles = client.get_klines(symbol=asset, interval=Client.KLINE_INTERVAL_4HOUR)
    except:
        print("<b><yellow>Bağlantı Koptu</yellow> </b>")
        print("<b><green>Yeniden Başlatılmayı Bekliyor</green> </b>")
        time.sleep(30)
        print("<b><blue>Yeniden Başlatıldı</blue> </b>")
        candles = client.get_klines(symbol=asset, interval=Client.KLINE_INTERVAL_4HOUR)
        pass
        
        
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

def PMAX(dataframe, period=4, multiplier=0.1, length=4, MAtype=7, src=1):
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

    # up/down belirteçi / main logic
    df[pmx] = np.where((df[pm] > 0.00), np.where((df[mavalue] < df[pm]), 'down',  'up'), np.NaN)
    
    df.drop(['basic_ub', 'basic_lb', 'final_ub', 'final_lb'], inplace=True, axis=1)

    df.fillna(0, inplace=True)

    return df

# TUSDUSDT, PAXUSDT, BUSDUSDT // Trash
# ONGUSDT //Çok kırılım var
# TRUUSDT, CKBUSDT, TWTUSDT, LITUSDT, DODOUSDT, BADGERUSDT, FISUSDT, LINAUSDT, PERPUSDT

# assets = ["XLMUSDT","WINGUSDT","QTUMUSDT", "XRPUSDT", "EOSUSDT", "VETUSDT", "LINKUSDT", "BTTUSDT", "HOTUSDT", "ZILUSDT", "ZECUSDT", "IOSTUSDT", "CELRUSDT", "DASHUSDT", "NANOUSDT", "OMGUSDT", "THETAUSDT", "TFUELUSDT", "ONEUSDT", "FTMUSDT", "GTOUSDT", "DOGEUSDT", "DUSKUSDT", "ANKRUSDT", "WINUSDT", "COSUSDT", "NPXSUSDT", "MTLUSDT", "TOMOUSDT", "PERLUSDT", "DENTUSDT", "MFTUSDT", "KEYUSDT", "CVCUSDT", "CHZUSDT", "BEAMUSDT", "STXUSDT", "IOTXUSDT", "TROYUSDT", "DREPUSDT", "WRXUSDT", "BTSUSDT", "LSKUSDT", "LTOUSDT", "MBLUSDT", "COTIUSDT", "STPTUSDT", "HIVEUSDT", "CHRUSDT", "GXSUSDT", "ARDRUSDT", "STMXUSDT", "REPUSDT", "COMPUSDT", "SCUSDT", "ZENUSDT", "SXPUSDT", "STORJUSDT", "YFIUSDT", "BALUSDT", "JSTUSDT", "SRMUSDT", "ANTUSDT", "CRVUSDT", "DOTUSDT", "LUNAUSDT", "RSRUSDT", "TRBUSDT", "YFIIUSDT", "KSMUSDT", "UMAUSDT", "NBSUSDT", "OXTUSDT", "SUNUSDT", "AVAXUSDT", "HNTUSDT", "FLMUSDT", "ORNUSDT", "INJUSDT", "CTKUSDT", "AKROUSDT", "DNTUSDT", "STRAXUSDT", "AVAUSDT", "XEMUSDT", "SUSDUSDT", "1INCHUSDT", "REEFUSDT"]
# assets = ["ZILUSDT"]
assets = ["DCRUSDT", "STORJUSDT", "USDTBKRW", "MANAUSDT", "AUDUSDT", "YFIUSDT", "BALUSDT", "BLZUSDT", "IRISUSDT", "KMDUSDT", "USDTDAI", "JSTUSDT", "SRMUSDT", "ANTUSDT", "CRVUSDT", "SANDUSDT", "OCEANUSDT", "NMRUSDT", "DOTUSDT", "LUNAUSDT", "RSRUSDT", "PAXGUSDT", "WNXMUSDT", "TRBUSDT", "BZRXUSDT", "SUSHIUSDT", "YFIIUSDT", "KSMUSDT", "EGLDUSDT", "DIAUSDT", "RUNEUSDT", "FIOUSDT", "UMAUSDT", "USDTNGN", "BELUSDT", "WINGUSDT", "UNIUSDT", "NBSUSDT", "OXTUSDT", "SUNUSDT", "AVAXUSDT", "HNTUSDT", "FLMUSDT", "ORNUSDT", "UTKUSDT", "XVSUSDT", "ALPHAUSDT", "AAVEUSDT", "NEARUSDT", "FILUSDT", "INJUSDT", "AUDIOUSDT", "CTKUSDT", "AKROUSDT", "AXSUSDT", "HARDUSDT", "DNTUSDT", "STRAXUSDT", "UNFIUSDT", "ROSEUSDT", "AVAUSDT", "XEMUSDT", "SKLUSDT", "SUSDUSDT", "GRTUSDT", "JUVUSDT", "PSGUSDT", "USDTBVND", "1INCHUSDT", "REEFUSDT", "OGUSDT", "ATMUSDT", "ASRUSDT", "SCUSDT", "ZENUSDT", "SNXUSDT", "VTHOUSDT", "DGBUSDT", "GBPUSDT", "SXPUSDT", "MKRUSDT", "TCTUSDT", "WRXUSDT", "BTSUSDT", "LSKUSDT", "BNTUSDT", "LTOUSDT", "STRATUSDT", "AIONUSDT", "MBLUSDT", "COTIUSDT", "STPTUSDT", "USDTZAR", "WTCUSDT", "DATAUSDT", "SOLUSDT", "USDTIDRT", "CTSIUSDT", "HIVEUSDT", "CHRUSDT", "GXSUSDT", "ARDRUSDT", "MDTUSDT", "STMXUSDT", "KNCUSDT", "REPUSDT", "LRCUSDT", "PNTUSDT", "COMPUSDT", "BTCUSDT", "ETHUSDT", "BNBUSDT", "BCCUSDT", "NEOUSDT", "LTCUSDT", "QTUMUSDT", "ADAUSDT", "XRPUSDT", "EOSUSDT", "IOTAUSDT", "XLMUSDT", "ONTUSDT", "TRXUSDT", "ETCUSDT", "ICXUSDT", "NULSUSDT", "VETUSDT", "BCHABCUSDT", "LINKUSDT", "WAVESUSDT", "BTTUSDT", "USDSUSDT", "HOTUSDT", "ZILUSDT", "ZRXUSDT", "FETUSDT", "BATUSDT", "XMRUSDT", "ZECUSDT", "IOSTUSDT", "CELRUSDT", "DASHUSDT", "NANOUSDT", "OMGUSDT", "THETAUSDT", "ENJUSDT", "MITHUSDT", "MATICUSDT", "ATOMUSDT", "TFUELUSDT", "ONEUSDT", "FTMUSDT", "ALGOUSDT", "GTOUSDT", "DOGEUSDT", "DUSKUSDT", "ANKRUSDT", "WINUSDT", "COSUSDT", "NPXSUSDT", "COCOSUSDT", "MTLUSDT", "TOMOUSDT", "PERLUSDT", "DENTUSDT", "MFTUSDT", "KEYUSDT", "STORMUSDT", "DOCKUSDT", "WANUSDT", "FUNUSDT", "CVCUSDT", "CHZUSDT", "BANDUSDT", "BEAMUSDT", "XTZUSDT", "RENUSDT", "RVNUSDT", "HCUSDT", "HBARUSDT", "NKNUSDT", "STXUSDT", "KAVAUSDT", "ARPAUSDT", "IOTXUSDT", "RLCUSDT", "MCOUSDT", "CTXCUSDT", "BCHUSDT", "TROYUSDT", "VITEUSDT", "FTTUSDT", "BUSDTRY", "USDTTRY", "USDTRUB", "OGNUSDT", "DREPUSDT"]

def do(asset):
    result = PMAX(getCandles(asset))

    isInWallet = bought.find_one({'asset': asset},sort=[( '_id', DESCENDING )])
            
    current_pmax = result['pmX_4_0.1_4_7'][499]
    last_pmax = result['pmX_4_0.1_4_7'][498]
                
    if (last_pmax != current_pmax):
        if(current_pmax == "down"):
            if (isInWallet != None):
                print("<b><blue>SATILDI</blue> </b>")
                print("<b>{}</b>".format(asset))
                print("<b><fg 0,95,0><white>{}</white></fg 0,95,0></b>".format(result) )
                sold.insert_one({
                        'asset': asset,
                        'pmax': result['pmX_4_0.1_4_7'][499],
                        'sold_price': result['close'][499],
                        'buy_data': isInWallet,
                        'sold_time': datetime.now()
                        }) 
                bought.delete_one({'asset': asset})
        else:
            if (isInWallet == None):
                Notify.notify(asset, 'Alım Sinyali', 'Trader V1', sound=True)
                print("<b><blue>SATIN ALINDI</blue> </b>")
                print("<b>{}</b>".format(asset))
                print("<b><fg 0,95,0><white>{}</white></fg 0,95,0></b>".format(result) )
                bought.insert_one({
                        'asset': asset,
                        'pmax': result['pmX_4_0.1_4_7'][499],
                        'buy_price': result['close'][499],
                        'buy_time': datetime.now()
                        }) 
            else:
                print("<b><green>Pmax Up Uyarısı</green> <red>Tekrar</red>")
                print("<b>{}</b>".format(asset))
        
i = 0
while i < len(assets):
    if (i == 0):
        print ("<b><yellow>{}</yellow> </b>".format(f.renderText('Trader V1')))
    do(assets[i])
    i += 1
    time.sleep(5)
    if (i == len(assets)):
        print("<b><green>*** Listenin Sonu ***</green> </b>")
        print("<b><yellow>*** Yeniden Başlıyor ***</yellow> </b>")
        i = 0




