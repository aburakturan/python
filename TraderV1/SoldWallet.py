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

db = client.pmaxV1
sold = db.sold

set_printoptions(threshold=maxsize)

client = Client('jjIP0g5xq7S1HjBSHLH1Eizw1qpPO0HxUm1P3CqlGUFKKmb7T4vLj7B6AYbqtEgu', '6W9hO9vrVWjMkThl2stbv0OR80Sl83GpkWzwYsIrOrAvPEVTQStLfKbc3bUasttg')



def do():
    wallet = sold.find({})

    Table = PrettyTable(['ID','Asset', 'Buy', 'Sell', 'Percentage'])
    total_percantage = 0
    count = 0

    for item in wallet:
        count = count +1
        asset = item['asset']
        buy_price = float(item['buy_data']['buy_price'])
        sell_price = float(item['sold_price'])
        percentage = ((sell_price-buy_price)/sell_price)*100
        Table.add_row([count, asset, buy_price, sell_price, percentage ])
        
    total_percantage = total_percantage + percentage
    
    print(Table)
    print(total_percantage / count)

    
do()
        


