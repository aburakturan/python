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
parser.add_argument("--reverse", "-r", help="reverse sorting?")
parser.add_argument("--watch", "-w", help="custom takip listesi")
parser.add_argument("--source", "-s", help="kaynak hangi cüzdan?")
args = parser.parse_args()


client = MongoClient('localhost',27017)  
db = client.pmaxV2

if args.source == "watch":
    type_of_wallet = "Watch List"
    source = db.track
elif args.source == "wallet":
    type_of_wallet = "Wallet"
    source = db.wallet
elif args.source == "sold":
    type_of_wallet = "Sold Wallet"
    source = db.sold

if args.watch:
    custom_watch_list = args.watch.split(',')

set_printoptions(threshold=maxsize)

client = Client('jjIP0g5xq7S1HjBSHLH1Eizw1qpPO0HxUm1P3CqlGUFKKmb7T4vLj7B6AYbqtEgu', '6W9hO9vrVWjMkThl2stbv0OR80Sl83GpkWzwYsIrOrAvPEVTQStLfKbc3bUasttg')


def do():


    wallet = source.find({})
    candles = client.get_all_tickers()

    if args.source == "sold":
        Table = PrettyTable(['ID','Asset', 'Buy $', 'Sell $', '%', 'Reason', 'Current $', 'Current %', 'Buy Time', 'Sell Time'])
    else:
        Table = PrettyTable(['ID','Asset', 'Buy', 'Current', 'Percentage', 'Date'])

    total_percantage = 0
    current_percentage_if_dont_sold = 0
    count = 0
    previous_date = ""
    for item in wallet:
        
        
        if args.source == "sold":
            buy_price = float(item['buy_data']['buy_price'])
        else:
            buy_price = float(item['buy_price'])

    
  
        for candle in candles:
            if (candle['symbol'] == item['asset']):
                current_price = float(candle['price'])
                current_price_if_dont_sold = float(candle['price'])
                if args.watch:
                    if item['asset'] in custom_watch_list:
                        if args.source == "sold":
                            current_price = float(item['sold_price'])
                            current_percentage_if_dont_sold = ((current_price_if_dont_sold-buy_price)/current_price_if_dont_sold)*100
                        percentage = ((current_price-buy_price)/current_price)*100
                        total_percantage = total_percantage + percentage
                        if args.source == "sold":
                            _current_percentage_if_dont_sold = current_percentage_if_dont_sold - percentage
                else:
                    if args.source == "sold":
                            current_price = float(item['sold_price'])
                            current_percentage_if_dont_sold = ((current_price_if_dont_sold-buy_price)/current_price_if_dont_sold)*100
                    percentage = ((current_price-buy_price)/current_price)*100
                    total_percantage = total_percantage + percentage
                    if args.source == "sold":
                            _current_percentage_if_dont_sold =  current_percentage_if_dont_sold  - percentage

        
        
        if args.source == "sold":
            current_date = item['sold_time'].strftime("%d/%m")
        else:
            current_date = item['buy_time'].strftime("%d/%m")

        if previous_date != current_date:
            if args.source == "sold":
                Table.add_row(["---", "---", "---", "---", "---", "---", "---", "---" , "---", "---"])
            else:
                Table.add_row(["---", "---", "---", "---", "---", "---"])
        
        previous_date = current_date

        if args.watch:
            
            if item['asset'] in custom_watch_list:
                if args.source == "sold":
                    count = count +1
                    Table.add_row([count, item['asset'], buy_price, current_price, colored("%.2f" % round(percentage, 2), 'green', attrs=['bold']), item['reason'].split('alama')[0], current_price_if_dont_sold, colored("%.2f" % round(_current_percentage_if_dont_sold, 2), 'red', attrs=['bold']) , item['buy_data']['buy_time'].strftime("%d/%m %H:%M"), item['sold_time'].strftime("%d/%m %H:%M")])
                else:
                    count = count +1
                    if percentage < 0: 
                        Table.add_row([colored(count,'white'), colored(item['asset'],'white'), colored(buy_price,'white'), colored(current_price,'white'), colored("%.2f" % round(percentage, 2), 'red', attrs=['bold']), colored(item['buy_time'].strftime("%d/%m %H:%M"),'white')   ])
                    else:
                        Table.add_row([colored(count,'white'), colored(item['asset'],'white'), colored(buy_price,'white'), colored(current_price,'white'), colored("%.2f" % round(percentage, 2), 'green', attrs=['bold']), colored(item['buy_time'].strftime("%d/%m %H:%M"),'white')   ])

        else:
            if args.source == "sold":
                count = count +1
                Table.add_row([count, item['asset'], buy_price, current_price, colored("%.2f" % round(percentage, 2), 'green', attrs=['bold'])  , item['reason'].split('alama')[0], current_price_if_dont_sold, colored("%.2f" % round(_current_percentage_if_dont_sold, 2), 'red', attrs=['bold']), item['buy_data']['buy_time'].strftime("%d/%m %H:%M"), item['sold_time'].strftime("%d/%m %H:%M")])
            else:
                count = count +1
                if percentage < 0: 
                    Table.add_row([colored(count,'white'), colored(item['asset'],'white'), colored(buy_price,'white'), colored(current_price,'white'), colored("%.2f" % round(percentage, 2), 'red', attrs=['bold']), colored(item['buy_time'].strftime("%d/%m %H:%M"),'white')   ])
                else:
                    Table.add_row([colored(count,'white'), colored(item['asset'],'white'), colored(buy_price,'white'), colored(current_price,'white'), colored("%.2f" % round(percentage, 2), 'green', attrs=['bold']), colored(item['buy_time'].strftime("%d/%m %H:%M"),'white')   ])

    
    if args.sort:
        Table.sortby = args.sort
    if args.reverse:
        if args.reverse in ("True"):
            Table.reversesort = True
        if args.reverse in ("False"):
            Table.reversesort = False
    
    

    # print ("<b><red>{}</red> </b>".format(f.renderText('Trader V2')))
    print("<b><yellow>*** CÜZDAN ({}) ***</yellow> </b>".format(type_of_wallet))
    print("<b><fg 0,95,0><white>{}</white></fg 0,95,0></b>".format(Table) )



    print("<b><blue>Ortalama Fark</blue> </b><b><yellow>{}</yellow></b>".format(total_percantage/count) )
    print("<b><blue>Farkların Toplamı</blue> </b><b><yellow>{}</yellow></b>".format(total_percantage) )
    print("<b><red>*** Diğer Cüzdanlar ***</red> </b>")
    print("<b><green>İzleme Listesi</green> </b><b><yellow>{}</yellow></b>".format(db.track.count_documents({})) )
    print("<b><green>Alış</green> </b><b><yellow>{}</yellow></b>".format(db.wallet.count_documents({})) )
    print("<b><green>Satış</green> </b><b><yellow>{}</yellow></b>".format(db.sold.count_documents({})) )

    





do()
        


