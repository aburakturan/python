from binance.client import Client  # python3 -m pip install python-binance
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
# client = MongoClient('mongodb+srv://ahmetburak:og1LCXX4VCw7RYV7@cluster0.ygftz.mongodb.net/')  

db = client.pmaxV2
track = db.track
wallet = db.wallet
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

# BCHSVUSDT,LENDUSDT, XZCUSDT, USDSBUSDT, ERDUSDT Grafik Yok
# TUSDUSDT, PAXUSDT, BUSDUSDT, USDCUSDT,USDTBIDR,USDTBRL // Trash
# ONGUSDT //Çok kırılım var
# YENI COINLER TRUUSDT, CKBUSDT, TWTUSDT, LITUSDT, DODOUSDT, BADGERUSDT, FISUSDT, LINAUSDT, PERPUSDT, SUPERUSDT, VENUSDT, BULLUSDT, ETHBULLUSDT, ETHBEARUSDT, EOSBULLUSDT, BKRWUSDT, DAIUSDT, CELOUSDT, RIFUSDT, BTCSTUSDT, FIROUSDT, SFPUSDT, CAKEUSDT, ACMUSDT, OMUSDT, PONDUSDT, DEGOUSDT, ALICEUSDT, RAMPUSDT, USDTUAH
assets = ["DCRUSDT", "STORJUSDT", "USDTBKRW", "MANAUSDT", "AUDUSDT", "YFIUSDT", "BALUSDT", "BLZUSDT", "IRISUSDT", "KMDUSDT", "USDTDAI", "JSTUSDT", "SRMUSDT", "ANTUSDT", "CRVUSDT", "SANDUSDT", "OCEANUSDT", "NMRUSDT", "DOTUSDT", "LUNAUSDT", "RSRUSDT", "PAXGUSDT", "WNXMUSDT", "TRBUSDT", "BZRXUSDT", "SUSHIUSDT", "YFIIUSDT", "KSMUSDT", "EGLDUSDT", "DIAUSDT", "RUNEUSDT", "FIOUSDT", "UMAUSDT", "USDTNGN", "BELUSDT", "WINGUSDT", "UNIUSDT", "NBSUSDT", "OXTUSDT", "SUNUSDT", "AVAXUSDT", "HNTUSDT", "FLMUSDT", "ORNUSDT", "UTKUSDT", "XVSUSDT", "ALPHAUSDT", "AAVEUSDT", "NEARUSDT", "FILUSDT", "INJUSDT", "AUDIOUSDT", "CTKUSDT", "AKROUSDT", "AXSUSDT", "HARDUSDT", "DNTUSDT", "STRAXUSDT", "UNFIUSDT", "ROSEUSDT", "AVAUSDT", "XEMUSDT", "SKLUSDT", "SUSDUSDT", "GRTUSDT", "JUVUSDT", "PSGUSDT", "USDTBVND", "1INCHUSDT", "REEFUSDT", "OGUSDT", "ATMUSDT", "ASRUSDT", "SCUSDT", "ZENUSDT", "SNXUSDT", "VTHOUSDT", "DGBUSDT", "GBPUSDT", "SXPUSDT", "MKRUSDT", "TCTUSDT", "WRXUSDT", "BTSUSDT", "LSKUSDT", "BNTUSDT", "LTOUSDT", "STRATUSDT", "AIONUSDT", "MBLUSDT", "COTIUSDT", "STPTUSDT", "USDTZAR", "WTCUSDT", "DATAUSDT", "SOLUSDT", "USDTIDRT", "CTSIUSDT", "HIVEUSDT", "CHRUSDT", "GXSUSDT", "ARDRUSDT", "MDTUSDT", "STMXUSDT", "KNCUSDT", "REPUSDT", "LRCUSDT", "PNTUSDT", "COMPUSDT", "BTCUSDT", "ETHUSDT", "BNBUSDT", "BCCUSDT", "NEOUSDT", "LTCUSDT", "QTUMUSDT", "ADAUSDT", "XRPUSDT", "EOSUSDT", "IOTAUSDT", "XLMUSDT", "ONTUSDT", "TRXUSDT", "ETCUSDT", "ICXUSDT", "NULSUSDT", "VETUSDT", "BCHABCUSDT", "LINKUSDT", "WAVESUSDT", "BTTUSDT", "USDSUSDT", "HOTUSDT", "ZILUSDT", "ZRXUSDT", "FETUSDT", "BATUSDT", "XMRUSDT", "ZECUSDT", "IOSTUSDT", "CELRUSDT", "DASHUSDT", "NANOUSDT", "OMGUSDT", "THETAUSDT", "ENJUSDT", "MITHUSDT", "MATICUSDT", "ATOMUSDT", "TFUELUSDT", "ONEUSDT", "FTMUSDT", "ALGOUSDT", "GTOUSDT", "DOGEUSDT", "DUSKUSDT", "ANKRUSDT", "WINUSDT", "COSUSDT", "NPXSUSDT", "COCOSUSDT", "MTLUSDT", "TOMOUSDT", "PERLUSDT", "DENTUSDT", "MFTUSDT", "KEYUSDT", "STORMUSDT", "DOCKUSDT", "WANUSDT", "FUNUSDT", "CVCUSDT", "CHZUSDT", "BANDUSDT", "BEAMUSDT", "XTZUSDT", "RENUSDT", "RVNUSDT", "HCUSDT", "HBARUSDT", "NKNUSDT", "STXUSDT", "KAVAUSDT", "ARPAUSDT", "IOTXUSDT", "RLCUSDT", "MCOUSDT", "CTXCUSDT", "BCHUSDT", "TROYUSDT", "VITEUSDT", "FTTUSDT", "BUSDTRY", "USDTTRY", "USDTRUB", "OGNUSDT", "DREPUSDT"]

def do(asset):

    # print(asset)
    
    result = PMAX(getCandles(asset))
    
    WatchList = track.find_one({'asset': asset},sort=[( '_id', DESCENDING )])
    WalletList = wallet.find_one({'asset': asset},sort=[( '_id', DESCENDING )])
    
    current_pmax = result['pmX_4_0.1_4_7'][499]
    last_pmax = result['pmX_4_0.1_4_7'][498]

    index = 0
    numpy_data = []
    while index <= 5:
        numpy_data.append({
            'open': result['open'][index+494],
            'high': result['high'][index+494],
            'low': result['low'][index+494],
            'close': result['close'][index+494],
            'volume': result['volume'][index+494],
            'ATR_4': result['ATR_4'][index+494],
            'MA_7_4': result['MA_7_4'][index+494],
            'pm_4_0_1_4_7': result['pm_4_0.1_4_7'][index+494],
            'pmX_4_0_1_4_7': result['pmX_4_0.1_4_7'][index+494],
        })
        index += 1  
           

    # Eğer Watchlist elemanı negatif değere düştüyse listeden çıkar
    if (WatchList != None):  # İzleme Listesindeyse
        time.sleep(1)
        

        try:
            candles = client.get_all_tickers()
        except:
            time.sleep(30)
            candles = client.get_all_tickers()
            pass


        buy_price = float(WatchList['buy_price'])
        for candle in candles:
            if (candle['symbol'] == asset):
                current_price = float(candle['price'])
                if (current_price < buy_price):
                    track.delete_one({'asset': asset})
                    print("<b><blue>Fiyat düştüğü için izleme listesinden çıkarıldı</blue> </b>")
                    print("<b>{}</b>".format(asset))
                         
                

    # Satış kontrolü,  fiyat ortalaması son fiyatın altına düşerse sat
    if (WalletList != None):  # Cüzdandaysa
        time.sleep(1)
        Prices = client.get_all_tickers()
        for price in Prices:
            if (price['symbol'] == asset):
                current_price = float(price['price'])

                # updated_price_new_array=[]
                # updated_price_new_array.append(current_price)

                # condition = { "asset": asset }
                # update_data = { "$set": { "updated_price": updated_price_new_array } }
                # wallet.update_one(condition, update_data)
                

                
                # %3 kâr olmadığı sürece elde tut 
                _buy_price = float(WalletList['buy_price'])
                _percentage = ((current_price-_buy_price)/current_price)*100

                if(_percentage > 3):
                    try:
                        if (WalletList['updated_price'] != 0):
                            updated_price_new_array = []
                            wallet_updated_price = WalletList['updated_price']
                            total_wallet_updated_price = 0
                            for u_price in wallet_updated_price:
                                updated_price_new_array.append(float(u_price))
                                total_wallet_updated_price += float(u_price)
                            
                            updated_price_new_array.append(current_price)
                            total_wallet_updated_price += current_price


                            average_of_updated_prices = total_wallet_updated_price / len(updated_price_new_array)
                            last_updated_price = updated_price_new_array[len(updated_price_new_array)-1]
                            
                            print("<b><red>average_of_updated_prices</red> </b><b><yellow>{}</yellow></b>".format(average_of_updated_prices) )
                            print("<b><red>last_updated_price</red> </b><b><yellow>{}</yellow></b>".format(last_updated_price) )

                            
                            if (average_of_updated_prices > last_updated_price): 
                                condition = { "asset": asset }
                                update_data = { "$set": { "updated_price": updated_price_new_array } }
                                wallet.update_one(condition, update_data)
                            else:
                                Notify.notify(asset, 'Satış Alarmı - Ortalama', 'Trader V2', sound=True)
                                print("<b><blue>SATILDI</blue> </b>")
                                print("<b><green>Ortalama düştü</green>")
                                print("<b>{}</b>".format(asset))
                                

                                # Silinecek

                                WatchList = track.find_one({'asset': asset},sort=[( '_id', DESCENDING )])
                                WalletList = wallet.find_one({'asset': asset},sort=[( '_id', DESCENDING )])

                                print('WalletList', WalletList)
                                print('Watchlist', WatchList)

                                Notify.notify(asset, 'SATIŞ', 'Trader V2', sound=True)

                                # Silinecek

                                sold.insert_one({
                                    'asset': asset,
                                    'pmax': result['pmX_4_0.1_4_7'][499],
                                    'sold_price': result['close'][499],
                                    'buy_data': WalletList,
                                    'sold_time': datetime.now(),
                                    'candle_data': numpy_data,
                                    'reason': 'Ortalama',
                                    }) 
                                wallet.delete_one({'asset': asset})
                    except:
                        updated_price_init = []
                        
                        try:
                            updated_price_init.append(current_price)
                        except:
                            updated_price_init.append(0)
                            pass
                        condition = { "asset": asset }
                        update_data = { "$set": { "updated_price": updated_price_init } }
                        wallet.update_one(condition, update_data)
                        pass


                
    if (last_pmax != current_pmax):
        # Satış mantığı, fiyat Pmax'e göre düşüşteyse sat. Bu kısım zarara girmeden satış yapamadı
        if(current_pmax == "down"):
            if (WalletList != None):  # Cüzdanda ise
                
                time.sleep(1)
                Prices = client.get_all_tickers()
                for price in Prices:
                    if (price['symbol'] == asset):
                        current_price = float(price['price'])
                
                _buy_price = float(WalletList['buy_price'])
                _percentage = ((current_price-_buy_price)/current_price)*100

                # %3 kâr olmadığı sürece elde tut 
                if(_percentage > 3):
                    Notify.notify(asset, 'Satış Alarmı - Pmax', 'Trader V2', sound=True)
                    print("<b><blue>SATILDI</blue> </b>")
                    print("<b><green>Pmax Sinyali</green>")
                    print("<b>{}</b>".format(asset))

                    # Silinecek
                    WatchList = track.find_one({'asset': asset},sort=[( '_id', DESCENDING )])
                    WalletList = wallet.find_one({'asset': asset},sort=[( '_id', DESCENDING )])

                    print('WalletList', WalletList)
                    print('Watchlist', WatchList)

                    Notify.notify(asset, 'SATIŞ', 'Trader V2', sound=True)
                    # Silinecek
                                
                    sold.insert_one({
                        'asset': asset,
                        'pmax': result['pmX_4_0.1_4_7'][499],
                        'sold_price': result['close'][499],
                        'buy_data': WalletList,
                        'sold_time': datetime.now(),
                        'candle_data': numpy_data,
                        'reason': 'Pmax',
                        }) 
                    wallet.delete_one({'asset': asset})  
        else:
            #  UP ise
            if (WatchList == None):   # Takip listesinde değilse
                if (WalletList == None): # Cüzdanda değilse
                    Notify.notify(asset, 'WatchList Aktif', 'Trader V2', sound=True)

                    print("<b><green>Takip Listesine Alındı</green> </b>")
                    print("<b>{}</b>".format(asset))
                    print("<b><fg 0,95,0><white>{}</white></fg 0,95,0></b>".format(result) )

                    track.insert_one({
                        'asset': asset,
                        'pmax': result['pmX_4_0.1_4_7'][499],
                        'buy_price': result['close'][499],
                        'buy_time': datetime.now(),
                        'candle_data': numpy_data,
                        }) 
            else:  # Takip listesindeyse 
                if (WalletList == None): # Cüzdanda değilse
                    time.sleep(1)
                    try:
                        candles = client.get_all_tickers()
                    except:
                        time.sleep(30)
                        candles = client.get_all_tickers()
                        pass

                    for candle in candles:
                            if (candle['symbol'] == asset):
                                current_price = float(candle['price'])
                    buy_price = WatchList['buy_price']
                    percentage = ((current_price-buy_price)/current_price)*100
                    if (percentage >= 2):
                        Notify.notify(asset, 'Alım Sinyali %2', 'Trader V2', sound=True)
                        print("<b><blue>SATIN ALINDI</blue> </b>")
                        print("<b>{}</b>".format(asset))
                        print("<b><fg 0,95,0><white>{}</white></fg 0,95,0></b>".format(result) )
                        wallet.insert_one({
                            'asset': asset,
                            'buy_price': current_price,
                            'buy_time': datetime.now(),
                            'track_data' :WatchList,
                            'candle_data': numpy_data,
                            })
                        track.delete_one({'asset': asset})

        
i = 0
while i < len(assets):
    if (i == 0):
        print ("<b><yellow>{}</yellow> </b>".format(f.renderText('Trader V2')))
    do(assets[i])
    i += 1
    time.sleep(5)
    if (i == len(assets)):
        print("<b><green>*** Listenin Sonu ***</green> </b>")
        print("<b><yellow>*** Yeniden Başlıyor ***</yellow> </b>")
        i = 0





