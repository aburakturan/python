from binance.client import Client
import pandas as pd
import os

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

def notify(title, text):
    os.system("""
              osascript -e 'display notification "{}" with title "{}"'
              """.format(text, title))


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
    # Table = PrettyTable(['ID','Asset', 'Total Buy Price', 'Total Current Price', 'Percentage'])
    Table = PrettyTable(['ID','Asset', 'Percentage', 'Total Buy Price', 'Total Current Price', 'Profit'])

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

        percentage = ((total_current_price-total_buy_price)/total_current_price)*100
        total_percantage = total_percantage + percentage

        if (total_buy_price >= 10):
            if percentage > 5:
                # print("{} - {}".format(balance['asset'], percentage))
                control(balance['asset'])
                
        
    if args.sort:
        Table.sortby = args.sort
    if args.reverse:
        if args.reverse in ("True"):
            Table.reversesort = True
        if args.reverse in ("False"):
            Table.reversesort = False



def control(asset):
    symbol = "{}USDT".format(asset)
    Prices = client.get_all_tickers()
    for price in Prices:
        if (price['symbol'] == symbol):
            current_price = float(price['price'])

    binanceWallet = wallet.find_one({'asset': asset})
    # try:
    if (binanceWallet['updated_price'] != 0):
        updated_price_new_array = []
        wallet_updated_price = binanceWallet['updated_price']
        total_wallet_updated_price = 0

        
        for u_price in wallet_updated_price:
            updated_price_new_array.append(float(u_price))
            total_wallet_updated_price += float(u_price)
            
        
        updated_price_new_array.append(current_price)
        total_wallet_updated_price += current_price

        average_of_updated_prices = total_wallet_updated_price / len(updated_price_new_array)
        last_updated_price = updated_price_new_array[len(updated_price_new_array)-1]
        



        if len(updated_price_new_array) >= 5:
            if (average_of_updated_prices < last_updated_price): 
            # if (average_of_updated_prices - ((average_of_updated_prices/100)*20) > last_updated_price): 
                print("<b><blue>Binance Wallet Sat Sinyali</blue> </b>")
                print("<b><green>Ortalama düştü</green>")
                print("<b>{} <red>⬇</red></b>".format(asset))
                notify_ending("{} Satış Sinyali".format(asset))
            else:
                print("<b>{} <blue>⬆</blue></b>".format(asset))
                condition = { "asset": asset }
                update_data = { "$set": { "updated_price": updated_price_new_array } }
                wallet.update_one(condition, update_data)

                
        else:
            print("<b>{} <blue>⬆</blue></b>".format(asset))
            condition = { "asset": asset }
            update_data = { "$set": { "updated_price": updated_price_new_array } }
            wallet.update_one(condition, update_data)
                

    else:
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



i = 0
while i >= 0:
    i+=1
    binanceWalletList()
    print('---------------')
    time.sleep(2)

        