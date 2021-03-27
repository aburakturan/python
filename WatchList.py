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
from prettytable import PrettyTable

client = MongoClient('localhost',27017)  


if sys.argv[1:] == ['new']:
    db = client.TraderPmax
    track = db.track
    
else:
    db = client.pmax


if sys.argv[1:] == ['15']:
    bought = db.bought15
    sold = db.sold15
else:
    bought = db.bought
    sold = db.sold





set_printoptions(threshold=maxsize)

client = Client('jjIP0g5xq7S1HjBSHLH1Eizw1qpPO0HxUm1P3CqlGUFKKmb7T4vLj7B6AYbqtEgu', '6W9hO9vrVWjMkThl2stbv0OR80Sl83GpkWzwYsIrOrAvPEVTQStLfKbc3bUasttg')



def do():
    if sys.argv[1:] == ['new']:
        wallet = track.find({})
    else:
        wallet = bought.find({})

    
    candles = client.get_all_tickers()

    # for candle in candles:
    #     symbol = str(candle['symbol'])
    #     if "USDT" in symbol:
    #         if not "UP" in symbol:
    #             if not "DOWN" in symbol:
    #                 print(symbol)


    if sys.argv[1:] == ['new']: 
        Table = PrettyTable(['ID','Asset', 'Tracked', 'Current', 'Percentage'])
    else:
        Table = PrettyTable(['ID','Asset', 'Buy', 'Sell', 'Percentage'])

    total_percantage = 0
    count = 0
    for item in wallet:
        count = count +1
        buy_price = float(item['buy_price'])
        for candle in candles:
            if (candle['symbol'] == item['asset']):
                current_price = float(candle['price'])
                
                percentage = ((current_price-buy_price)/current_price)*100

                total_percantage = total_percantage + percentage
        
        Table.add_row([count, item['asset'], buy_price, current_price, percentage ])

    

    print(Table)
    print(total_percantage/count)
    print(total_percantage)

       
            
                

do()
        


