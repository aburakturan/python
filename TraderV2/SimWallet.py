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
from termcolor import colored
from ansimarkup import ansiprint as print
from pyfiglet import Figlet

f = Figlet(font='slant')

parser = argparse.ArgumentParser()
parser.add_argument("--sort", "-o", help="neye göre sıralanacak?")
args = parser.parse_args()

dbclient = MongoClient('localhost',27017) 

set_printoptions(threshold=maxsize)

client = Client('jjIP0g5xq7S1HjBSHLH1Eizw1qpPO0HxUm1P3CqlGUFKKmb7T4vLj7B6AYbqtEgu', '6W9hO9vrVWjMkThl2stbv0OR80Sl83GpkWzwYsIrOrAvPEVTQStLfKbc3bUasttg')

candles = client.get_all_tickers()

Table = PrettyTable(['Sim #', 'Tether', 'Profit $', 'Profit %', 'Limit', 'Wallet', 'Watch', 'Sold', 'Total $'])

Table.align["Sim #"] = "l"
Table.align["Tether"] = "l"
Table.align["Profit $"] = "l"
Table.align["Profit %"] = "l"

title = ''

def do(i):

    if i == 1:
        title = i
        db = dbclient.simulationV1
        wallet_limit = 5
        per = int(500/wallet_limit)
    elif i == 2:
        title = i
        db = dbclient.simulationV2
        wallet_limit = 10
        per = int(500/wallet_limit)
    elif i == 3:
        title = i
        db = dbclient.simulationV3
        wallet_limit = 20
        per = int(500/wallet_limit)
    elif i == 4:
        title = i
        db = dbclient.simulationV4
        wallet_limit = 30
        per = int(500/wallet_limit)
    elif i == 5:
        title = i  
        db = dbclient.simulationV5
        wallet_limit = 45
        per = int(500/wallet_limit)
    elif i == 6:
        title = 'Z-Sim-1'  
        db = dbclient.sim_macd_v1
        wallet_limit = 30
        per = int(500/wallet_limit)
    elif i == 7:
        title = 'Z-Sim-2'  
        db = dbclient.sim_macd_v2
        wallet_limit = 30
        per = int(500/wallet_limit)
    elif i == 8:
        title = 'Z-Sim-3'  
        db = dbclient.sim_macd_v3
        wallet_limit = 30
        per = int(500/wallet_limit)
    elif i == 9:
        title = 'Z-Sim-4'  
        db = dbclient.sim_macd_v3
        wallet_limit = 30
        per = int(500/wallet_limit)


    walletdb = db.wallet
    solddb = db.sold
    watchdb = db.track
    hotwalletdb = db.hotwallet

    wallet = walletdb.find({})
    sold = solddb.find({})
    watch = watchdb.find({})
    hotwallet = hotwalletdb.find({})

    tether = 0
    assetUSDT = 0
    totalUSDT = 0
    profit = 0
    
    for item in hotwallet:
        if (item['asset']) == 'USDT':
            tether = item['qty']
        if (item['asset']) != 'USDT':
            for candle in candles:
                if (candle['symbol'] == item['asset']):
                    current_price = float(candle['price'])
            assetUSDT += item['qty'] * current_price
            totalUSDT = assetUSDT + tether

            profit = tether - (wallet_limit - walletdb.count_documents({})) * per


    Table.add_row([title, '{}'.format(round(tether,2)), '{} $'.format(round(profit,2)), '% {}'.format(round(round(round(profit,5)/500,5)*100,2)), wallet_limit, walletdb.count_documents({}), watchdb.count_documents({}), solddb.count_documents({}), '{} $'.format(round(totalUSDT,2))])

i = 1
while i <= 9:
    do(i)
    i += 1
    
print(Table)







