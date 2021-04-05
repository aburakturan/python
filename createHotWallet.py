from pymongo import MongoClient, DESCENDING, ASCENDING
client = MongoClient('localhost',27017)  

db = client.sim_macd_v1
hotwallet = db.hotwallet

tether = 500





hotwallet.insert_one({
    'asset': 'USDT',
    'qty':tether
    }) 