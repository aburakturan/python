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
    wallet = bought.find({})
    
    candles = client.get_all_tickers()

    Table = PrettyTable(['ID','Asset', 'Buy', 'Sell', 'Percentage'])
    total_percantage = 0
    total_percantage_minus = 0
    count = 0
    c = 0
    for item in wallet:
        count = count +1
        buy_price = float(item['buy_price'])
        for candle in candles:
            if (candle['symbol'] == item['asset']):
                current_price = float(candle['price'])
                
                percentage = ((current_price-buy_price)/current_price)*100

                

                total_percantage = total_percantage + percentage
        if (percentage < 0):
                total_percantage_minus = total_percantage_minus + percentage

        if (percentage > 3):
            c += 1
            Table.add_row([count, item['asset'], buy_price, current_price, percentage ])


    print(Table)
    print(total_percantage/c, '/', total_percantage)
    print('***')
    print (total_percantage_minus)
       
            
                

do()
        


