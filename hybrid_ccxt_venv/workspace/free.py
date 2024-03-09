import ccxt
import pprint
import requests
import time
from datetime import datetime
import plotly.express as px
import pandas as pd

global symbol
global last_closed_id
global plus_stack
global minus_stack
symbol = "BTCUSDT"
last_closed_id = None
plus_stack = 0
minus_stack = 0


with open("./requirement_test.txt") as f:
            lines = f.readlines()
            api_key = lines[0].strip()
            api_secret = lines[1].strip()

binance = ccxt.binanceusdm(config={
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
        })
binance.set_sandbox_mode(True)  # 테스트넷 모드

print(']]]\n\n\n')


info = binance.create_order(symbol=symbol, type='MARKET',side='buy', amount=0.003, params={
                'positionSide': 'LONG'
            })['info']['orderId']
info = int(info)
print(info)
try:
    result = binance.cancelOrder(id = info, symbol = symbol, params={'orderId' : info })
    print(result)
except:
    print('erorr 처리 완료')
'''info = binance.create_order(symbol=symbol, type='MARKET',side='buy', amount=0.001, params={
                'positionSide': 'LONG'
            })['info']
history = binance.fetch_my_trades(
                        symbol=symbol, params={'limit':1}
                    )[0]['info']
last_closed_id = history['id']
minus_stack = float(history['commission'])
plus_stack = float(history['realizedPnl'])
count = 0
while plus_stack != 0:
        count += 1
        time.sleep(0.001)
        history = binance.fetch_my_trades(
                            symbol=symbol, params={'limit': 1})[0]['info']

        last_closed_id = history['id']
        minus_stack = float(history['commission'])
        plus_stack = float(history['realizedPnl'])
        print(count, 'th refetch my trades...')
        print('minus_stack :', minus_stack)
        print('plus_stack :', plus_stack,'\n\n')
    
print('minus_stack :',minus_stack)
print('plus_stack :',plus_stack)

sell = binance.create_order(symbol=symbol, type='MARKET',side='sell', amount=0.1, params={
                'positionSide': 'LONG'
            })['info']
time.sleep(10)
trade = binance.fetch_my_trades(symbol = symbol, params={
            'fromId' : last_closed_id
        })
pprint.pprint(trade)
print('\n\n\n')
binance.create_order(symbol=symbol, type='LIMIT', side='buy', price=22222,
            amount = 0.001, params={
                'positionSide' : 'LONG'
            })
cancel_info = binance.cancelAllOrders(symbol=symbol)
pprint.pprint(cancel_info)
cancel_info = binance.cancelAllOrders(symbol=symbol)
pprint.pprint(cancel_info)
if cancel_info['code'] == '200':
    print('okauy')'''


















































'''def fetchTicker():
    # time.sleep(0.01)
    result = requests.get(
        "https://fapi.binance.com/fapi/v1/ticker/price", params={"symbol": symbol}
    )

    price_ = float(result.json()["price"])
    return price_'''


