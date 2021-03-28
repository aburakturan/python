from binance.client import Client
import pandas as pd
import numpy as np
import sys, getopt
import time
from datetime import datetime
import json
from sys import maxsize
from numpy import set_printoptions
from pymongo import MongoClient, DESCENDING, ASCENDING
from prettytable import PrettyTable
import operator
import argparse

client = MongoClient('localhost',27017)  

db = client.pmaxnew
bought = db.bought


set_printoptions(threshold=maxsize)

client = Client('jjIP0g5xq7S1HjBSHLH1Eizw1qpPO0HxUm1P3CqlGUFKKmb7T4vLj7B6AYbqtEgu', '6W9hO9vrVWjMkThl2stbv0OR80Sl83GpkWzwYsIrOrAvPEVTQStLfKbc3bUasttg')

parser = argparse.ArgumentParser()

parser.add_argument("--sort", "-s", help="neye göre sıralanacak?")
parser.add_argument("--reverse", "-r", help="reverse sorting?")
parser.add_argument("--watch", "-w", help="custom takip listesi")

args = parser.parse_args()

if args.watch:
    custom_watch_list = args.watch.split(',')

def do():


    wallet = bought.find({})
    candles = client.get_all_tickers()

    Table = PrettyTable(['ID','Asset', 'Buy', 'Current', 'Percentage'])

    total_percantage = 0
    count = 0
    for item in wallet:
        count = count +1
        buy_price = float(item['buy_price'])
        for candle in candles:
            if (candle['symbol'] == item['asset']):
                current_price = float(candle['price'])
                
                if args.watch:
                    if item['asset'] in custom_watch_list:
                        percentage = ((current_price-buy_price)/current_price)*100
                        total_percantage = total_percantage + percentage
                else:
                    percentage = ((current_price-buy_price)/current_price)*100
                    total_percantage = total_percantage + percentage
        
        if args.watch:
            if item['asset'] in custom_watch_list:
                Table.add_row([count, item['asset'], buy_price, current_price, percentage ])
        else:
            Table.add_row([count, item['asset'], buy_price, current_price, percentage ])

    
    if args.sort:
        Table.sortby = args.sort
    if args.reverse:
        if args.reverse in ("True"):
            Table.reversesort = True
        if args.reverse in ("False"):
            Table.reversesort = False
    

    print(Table)
    print(total_percantage/count)
    print(total_percantage)






do()
        


