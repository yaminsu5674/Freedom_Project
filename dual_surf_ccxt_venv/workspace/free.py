import ccxt
from ccxt.base import errors as binance_errors
import pprint
import time
from datetime import datetime


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
a = binance.fetch_balance(params = {"type" : "future"})
pprint.pprint(a)
info = 0
try:
    info = binance.create_order(symbol=symbol, type='LIMIT',side='buy', price = 24000,amount=20, params={
                'positionSide': 'LONG'
            })['info']['orderId']

except binance_errors.InsufficientFunds as e:
    print("시드 부족 에러 캐치 성공")
except binance_errors.InvalidOrder as e:
    print("레버리지 에러 캐치 성공 ")
except Exception as e:
    print(type(e))
    print(e)

info = int(info)
pprint.pprint(info)

'''try:
    result = binance.cancelOrder(id = info, symbol = symbol, params={'orderId' : info })
    print(result)
except:
    print('erorr 처리 완료')'''
