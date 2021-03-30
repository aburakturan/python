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
from ansimarkup import ansiprint as print
from pyfiglet import Figlet
import operator
import argparse
import json
import telegram


def notify_ending(message):
    
    token = "1664179275:AAHSNRalCCJmfHrnpm0GnijgUbbH38u41vw"
    chat_id = "-514290409"

    bot = telegram.Bot(token=token)
    bot.sendMessage(chat_id=chat_id, text=message)


client = MongoClient('localhost',27017)  

db = client.Binance
wallet = db.wallet



f = Figlet(font='slant')


set_printoptions(threshold=maxsize)

client = Client('4LdqnhvqK0rg5f4KKIPpfhAdD9PG7fKF4ssNHqWazHL0GepGjTPXKhmUFz2Db8oG', 'ua55ROqNp0CbohbcrL5McfZg7ALr6wlxRS9Kc43feGfKWn3Bv6M6XggONjhlqXYG')
# client = Client('0o8vTST2w4uH5cOfwoGhBqFySy04jFHGQ9yHZHdESFFpyCWQDCnH9aaJSekVfDGq', 'PTdpxSlAFsbnY5Qn3djGvKWO2MPJF7wNpnSTdE7XWhQ0JIxODp5c18BC1MYfCZOn')

parser = argparse.ArgumentParser()

parser.add_argument("--update", "-u", help="Binance wallet update")
parser.add_argument("--wallet", "-l", help="Binance wallet watch")

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

def binanceWalletList():
    prices = client.get_all_tickers()
    Table = PrettyTable(['ID','Asset', 'Total Buy Price', 'Total Current Price', 'Percentage'])

    acc = client.get_account()
    # balances = acc['balances']
    balances = wallet.find({})

    count = 0
    total_percantage = 0
    for balance in balances:
        
                count = count +1
                symbol = "{}USDT".format(balance['asset'])
                trades = client.get_my_trades(symbol=symbol)

                buy_price = float(balance['buy_price'])
                qty = float(balance['qty'])

                
                for trade in trades:
                    buy_price = float(trade['price'])
                    total_buy_price = qty * buy_price
                
                for price in prices:
                    if (price['symbol'] == symbol):
                        current_price = float(price['price'])
                        total_current_price = qty * current_price

                
                if (total_buy_price <= 10):
                    count -= 1
                else:
                    percentage = ((total_current_price-total_buy_price)/total_current_price)*100
                    total_percantage = total_percantage + percentage
                    Table.add_row([count, balance['asset'], total_buy_price, total_current_price, percentage ])
                    if percentage > 5:
                        notify_ending("{} Binance Wallet %3'ügeçti".format(balance['asset']))

        
    if args.sort:
        Table.sortby = args.sort
    if args.reverse:
        if args.reverse in ("True"):
            Table.reversesort = True
        if args.reverse in ("False"):
            Table.reversesort = False


    print ("<b><red>{}</red> </b>".format(f.renderText('Trader Tools')))
    print("<b><yellow>*** CÜZDAN (Binance) ***</yellow> </b>")
    print("<b><fg 0,95,0><white>{}</white></fg 0,95,0></b>".format(Table) )

    print("<b><blue>Ortalama Fark</blue> </b><b><yellow>{}</yellow></b>".format(total_percantage/count) )
    print("<b><blue>Farkların Toplamı</blue> </b><b><yellow>{}</yellow></b>".format(total_percantage) )
  

def binanceWalletRecord():
    wallet.remove({})
    print("<b><blue>Cüzdan silindi</blue> </b>" )

    prices = client.get_all_tickers()
    
    acc = client.get_account()
    balances = acc['balances']

    count = 0
    total_percantage = 0
    for balance in balances:
        if float(balance['free']) > 0 or float(balance['locked']) > 0:
            if balance['asset'] != 'BNB' and balance['asset'] != 'USDT' and balance['asset'] != 'LDDOGE':
                count = count +1
                symbol = "{}USDT".format(balance['asset'])
                trades = client.get_my_trades(symbol=symbol)

                if float(balance['free']) > 0:
                    qty = float(balance['free'])
                elif float(balance['locked']) > 0:
                    qty = float(balance['locked'])

                for trade in trades:
                    buy_price = float(trade['price'])
                    total_buy_price = qty * buy_price
                
                for price in prices:
                    if (price['symbol'] == symbol):
                        current_price = float(price['price'])
                        total_current_price = qty * current_price

                
                if (total_buy_price <= 10):
                    count -= 1
                else:
                    percentage = ((total_current_price-total_buy_price)/total_current_price)*100
                    total_percantage = total_percantage + percentage
                    wallet.insert_one({
                        'asset': balance['asset'],
                        'qty':qty,
                        'total_buy_price': total_buy_price,
                        'buy_price': buy_price,
                        'total_current_price': total_current_price,
                        'percentage': percentage
                        }) 
                    print("<b><blue>Cüzdan güncelleniyor:</blue> </b><b><yellow> {} </yellow></b>".format(balance['asset']) )

                    



# i = 0
# while i >= 0:
#     i+=1
#     binanceWalletList()
#     time.sleep(300)



if args.update:
    binanceWalletRecord()
elif args.wallet:
    i = 0
    while i >= 0:
        i+=1
        binanceWalletList()
        time.sleep(300)

        