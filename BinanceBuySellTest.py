from binance.client import Client  # python3 -m pip install python-binance
from binance.enums import *

client = Client('4LdqnhvqK0rg5f4KKIPpfhAdD9PG7fKF4ssNHqWazHL0GepGjTPXKhmUFz2Db8oG', 'ua55ROqNp0CbohbcrL5McfZg7ALr6wlxRS9Kc43feGfKWn3Bv6M6XggONjhlqXYG')


# BUY
# order = client.order_market_buy(
#     symbol='TRXUSDT',
#     quantity=110)

# SELL
# order = client.order_market_sell(
#     symbol='TRXUSDT',
#     quantity=110)


# print(order)


# BUY
# {'symbol': 'TRXUSDT', 'orderId': 752318006, 'orderListId': -1, 'clientOrderId': 'YaHwtJqw1YpQ9uD18LRVqB', 'transactTime': 1617486607404, 'price': '0.00000000', 'origQty': '110.00000000', 'executedQty': '110.00000000', 'cummulativeQuoteQty': '11.02420000', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'MARKET', 'side': 'BUY', 'fills': [{'price': '0.10022000', 'qty': '110.00000000', 'commission': '0.00002504', 'commissionAsset': 'BNB', 'tradeId': 69926928}]}

# SELL
# {'symbol': 'TRXUSDT', 'orderId': 752322622, 'orderListId': -1, 'clientOrderId': 'x7UKsehx8GpQUWZrGjJcyj', 'transactTime': 1617486661497, 'price': '0.00000000', 'origQty': '110.00000000', 'executedQty': '110.00000000', 'cummulativeQuoteQty': '11.01760000', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'MARKET', 'side': 'SELL', 'fills': [{'price': '0.10016000', 'qty': '110.00000000', 'commission': '0.00002534', 'commissionAsset': 'BNB', 'tradeId': 69927885}]}