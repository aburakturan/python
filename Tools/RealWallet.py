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
realWallet = db.realWallet
realSoldWallet = db.realSoldWallet
from ansimarkup import ansiprint as print
from pyfiglet import Figlet

f = Figlet(font='slant')


set_printoptions(threshold=maxsize)

client = Client('jjIP0g5xq7S1HjBSHLH1Eizw1qpPO0HxUm1P3CqlGUFKKmb7T4vLj7B6AYbqtEgu', '6W9hO9vrVWjMkThl2stbv0OR80Sl83GpkWzwYsIrOrAvPEVTQStLfKbc3bUasttg')

parser = argparse.ArgumentParser()

parser.add_argument("--realWalletList", "-wl", help="liste gösterilsin")
parser.add_argument("--realSoldWalletList", "-sl", help="liste gösterilsin")

parser.add_argument("--sort", "-o", help="neye göre sıralanacak?")
parser.add_argument("--reverse", "-r", help="reverse sorting?")
parser.add_argument("--watch", "-w", help="custom takip listesi")

parser.add_argument("--buy", "-b", help="gerçek alım eklenir")
parser.add_argument("--sell", "-s", help="gerçek satış eklenir")
# parser.add_argument('--foo', type=float, choices=[Range(0.0, 1.0)])

parser.add_argument("--price", "-p", help="gerçek alım/satım fiyatı fiyatı")



args = parser.parse_args()

if args.watch:
    custom_watch_list = args.watch.split(',')

def realWalletList():

    wallet = realWallet.find({})
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
    


    print ("<b><red>{}</red> </b>".format(f.renderText('Trader V1')))
    print("<b><yellow>*** CÜZDAN (Alış) ***</yellow> </b>")
    print("<b><fg 0,95,0><white>{}</white></fg 0,95,0></b>".format(Table) )

    print("<b><blue>Ortalama Fark</blue> </b><b><yellow>{}</yellow></b>".format(total_percantage/count) )
    print("<b><blue>Farkların Toplamı</blue> </b><b><yellow>{}</yellow></b>".format(total_percantage) )
  

    

def realSoldWalletList():

    wallet = realSoldWallet.find({})

    Table = PrettyTable(['ID','Asset', 'Buy Price', 'Sell Price', 'Percentage'])

    total_percantage = 0
    count = 0
    for item in wallet:
        count = count +1
        buy_price = float(item['buy_price'])
        sell_price = float(item['sell_price'])
        if args.watch:
            if item['asset'] in custom_watch_list:
                percentage = ((sell_price-buy_price)/sell_price)*100
                total_percantage = total_percantage + percentage
        else:
            percentage = ((sell_price-buy_price)/sell_price)*100
            total_percantage = total_percantage + percentage
        
        if args.watch:
            if item['asset'] in custom_watch_list:
                Table.add_row([count, item['asset'], buy_price, sell_price, percentage ])
        else:
            Table.add_row([count, item['asset'], buy_price, sell_price, percentage ])

    
    if args.sort:
        Table.sortby = args.sort
    if args.reverse:
        if args.reverse in ("True"):
            Table.reversesort = True
        if args.reverse in ("False"):
            Table.reversesort = False
    

    print ("<b><red>{}</red> </b>".format(f.renderText('Trader V1')))
    print("<b><yellow>*** CÜZDAN (Satış) ***</yellow> </b>")
    print("<b><fg 0,95,0><white>{}</white></fg 0,95,0></b>".format(Table) )

    print("<b><blue>Ortalama Fark</blue> </b><b><yellow>{}</yellow></b>".format(total_percantage/count) )
    print("<b><blue>Farkların Toplamı</blue> </b><b><yellow>{}</yellow></b>".format(total_percantage) )
  


def buy():
    print(args.buy)

    isInWallet = realWallet.find_one({'asset': args.buy})
        
    if (isInWallet == None):
        print("<b><yellow>Gerçek alım eklendi</yellow> </b>")
        print("<b><white>{}</white> </b>".format(args.buy))
        realWallet.insert_one({
            'asset': args.buy,
            'buy_price': float(args.price),
            'buy_time': datetime.now()
            }) 

    else:
        print("<b><red>Asset zaten cüzdana eklenmiş</red> </b>")
        
def sell():
    print(args.sell)

    isInWallet = realWallet.find_one({'asset': args.sell})
        
    if (isInWallet != None):

        print("<b><yellow>Gerçek satış eklendi</yellow> </b>")
        print("<b><white>{}</white> </b>".format(args.buy))

        realSoldWallet.insert_one({
            'asset': args.sell,
            'buy_price': isInWallet['buy_price'],
            'sell_price': float(args.price),
            'buy_time': datetime.now()
            }) 
        realWallet.delete_one({'asset': args.sell})

    else:
        print("<b><red>Asset cüzdanda yok</red> </b>")


if args.realWalletList:
    realWalletList()
elif args.realSoldWalletList:
    realSoldWalletList()
elif args.buy:
    buy()
elif args.sell:
    sell()
        

