import ccxt
import control
import alarm
import print_and_log
import errors
import pprint
import time
from decimal import Decimal


class Judger:
    def __init__(self, a, b, c, symbol, main_position, leverage):
        self.a = a
        self.b = b
        self.c = c
        self.a_1 = None 
        self.b_1 = None
        self.program_on = True
        self.symbol = symbol
        self.main_position = main_position
        self.leverage = leverage
        self.step = -1
        self.mode = 0  # if 0 surf-way judging, if 1 step-way judging
        #-------------------------------
        self.strong_position = main_position
        if self.main_position == 'LONG':
            self.weak_position = 'SHORT'
        else:
            self.weak_position = 'LONG'
        self.strong_amount = 0
        self.weak_amount = None
        self.l = None
        self.s = None
        self.p = None
        self.q = None
        self.last_closed_id = None
        self.minus_stack = 0
        self.plus_stack = 0
        self.recent_counter = 0
        #-------------------------------
        self.income_24 = 0
        self.cycles_24 = 0
        self.bad_cycles_24 = 0
        self.good_cycles_24  = 0
        self.income_1 = 0
        self.cycles_1 = 0
        self.bad_cycles_1 = 0
        self.good_cycles_1 = 0
        self.alarm_bot = alarm.alarm_bot()
        #-------------------------------
        with open("./requirement_test.txt") as f:
            lines = f.readlines()
            api_key = lines[0].strip()
            api_secret = lines[1].strip()

        self.binance = ccxt.binanceusdm(config={
            'apiKey' : api_key,
            'secret' : api_secret,
            'enableRateLimit' : True
        })
        self.binance.set_sandbox_mode(True)
        self.initiate_balance()
    
    def initiate_balance(self):
        leverage = int(self.binance.fapiPrivate_post_leverage({"symbol" : self.symbol, "leverage" : self.leverage})['leverage'])
        if leverage == self.leverage:
            print('leverage :', leverage, 'yes right!')
        else:
            raise errors.LeverageError
        balance = self.binance.fetch_balance(params = {"type" : "future"})['used']['USDT']
        if balance == 0.0:
            print('Position is clean now!\n\n\n')
        else:
            raise errors.BalanceError


    def get_24(self):
        self.alarm_bot.day_situation(self.income_24, self.cycles_24, self.bad_cycles_24, self.good_cycles_24)
        self.income_24 = 0
        self.cycles_24 = 0
        self.bad_cycles_24 = 0
        self.good_cycles_24 = 0

    def get_1(self):
        self.alarm_bot.hour_situation(self.income_1, self.cycles_1, self.bad_cycles_1, self.good_cycles_1)
        self.alarm_bot.day_situation(self.income_24, self.cycles_24, self.bad_cycles_24, self.good_cycles_24)
        self.income_1 = 0
        self.cycles_1 = 0
        self.bad_cycles_1 = 0
        self.good_cycles_1 = 0

    def change_judging_way(self, number):
        if number == 0:
            self.mode = 0
        else:
            self.mode = 1

    def judge(self, program_on):
        self.program_on = program_on
        if self.mode == 0:   # surf-way judging
            position = self.binance.fetchPositions(symbols=[self.symbol])
            mark_price = float(position[1]['info']['markPrice'])
            if self.strong_position == 'LONG':
                strong_amount = float(position[1]['info']['positionAmt'])
            else:
                strong_amount = float(position[2]['info']['positionAmt'])

            now_step = self.check_step(strong_amount)

            if now_step != self.step:  # step variated!
                answer = self.cancel_all_open_orders()
                position = self.binance.fetchPositions(symbols=[self.symbol])
                if self.strong_position == 'LONG':
                    strong_amount = float(position[1]['info']['positionAmt'])
                else:
                    strong_amount = float(position[2]['info']['positionAmt'])
                if self.strong_position == 'LONG':
                    self.l = float(position[1]['info']['entryPrice'])
                else:
                    self.s = float(position[1]['info']['entryPrice'])
                now_step = self.check_step(strong_amount)
                
                if now_step == 0:     # when step is 0
                    if self.step == -1:
                        pass
                    else:
                        self.done()     # initialize all variables
                    info = self.market_open(self.strong_position, self.c)
                    if self.strong_position == 'LONG':
                        self.l = float(info['avgPrice'])
                    else:
                        self.s = float(info['avgPrice'])
                    self.strong_amount = self.c

                    history = self.binance.fetch_my_trades(
                        symbol=self.symbol, params={'limit':1}
                    )[0]['info']
                    self.last_closed_id = history['id']
                    self.minus_stack = float(history['commission'])
                    self.plus_stack = float(history['realizedPnl'])

                    count = 0
                    while self.plus_stack != 0:
                        count += 1
                        time.sleep(0.001)
                        history = self.binance.fetch_my_trades(
                            symbol=self.symbol, params={'limit': 1})[0]['info']

                        self.last_closed_id = history['id']
                        self.minus_stack = float(history['commission'])
                        self.plus_stack = float(history['realizedPnl'])
                        if count == 1:
                            print(count, 'th refetch my trades...\n\n')
                        #print('minus_stack :', self.minus_stack)
                        #print('plus_stack :', self.plus_stack,'\n\n')
                    #print('minus_stack :',self.minus_stack)
                    #print('plus_stack :',self.plus_stack,'\n\n')
                    
                    if self.strong_position == 'LONG':
                        self.step = 1
                        self.p = round(self.l*1.0008, 1)+0.1
                        self.q = round(self.l*0.9988, 1)
                        self.limit_close(self.strong_position, self.decimal_multiply(self.c,self.a**(self.step)), self.p)
                        self.limit_open(self.strong_position, self.decimal_minus(self.decimal_multiply(self.c,(self.a**self.step)),self.strong_amount), self.q)
                        text = print_and_log.print_surf_status(self.strong_position, self.l, self.s, self.p, self.q, self.strong_amount, self.step)
                    else:                                # when strong position is short
                        pass

                elif now_step == self.b:   # when step is b
                    # 손해 방지 코드 control을 통해 추가해야 함.++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    self.strong_amount = strong_amount
                    self.p = round(self.l*1.0008, 1)+0.1
                    self.q = round(self.l*0.9994, 1)
                    self.limit_close(self.strong_position, self.decimal_multiply(self.c,self.a**(self.step-1)), self.p)
                    self.stop_limit_close(self.strong_position, self.decimal_multiply(self.c,self.a**(self.step-1)), self.q-self.l*0.0004, self.q)
                    self.step = now_step
                    text = print_and_log.print_surf_status(self.strong_position, self.l, self.s, self.p, self.q, self.strong_amount, self.step)

                else:                  # when 1 < step < b
                    if self.strong_position == 'LONG':
                        self.strong_amount = strong_amount
                        self.p = round(self.l*1.0008, 1)+0.1
                        self.q = round(self.l*0.9988, 1)
                        self.limit_close(self.strong_position, self.decimal_multiply(self.c,self.a**(self.step)), self.p)
                        self.limit_open(self.strong_position, self.decimal_minus(self.decimal_multiply(self.c,(self.a**now_step)),self.strong_amount), self.q)
                        self.step = now_step
                        text = print_and_log.print_surf_status(self.strong_position, self.l, self.s, self.p, self.q, self.strong_amount, self.step)
                    
            else:                      # no step variation 
                if self.step == self.b:
                    if self.strong_position == 'LONG':
                        if mark_price < self.q-self.l*0.0004:
                            info = self.binance.create_order(symbol=self.symbol, type='MARKET',side='sell', amount=self.decimal_multiply(self.c,self.a**(self.step-1)), params={
                            'positionSide': 'LONG'
                            })['info']


        else:                # step-way judging
            pass     

#-------------------------------------------------------------------------------------------
    def check_step(self, strong_amount):
        step = 0
        if strong_amount == 0:
            return step
        if self.mode == 0:
            for i in range(2, self.b+2):
                if self.decimal_multiply(self.c,self.a**(i-2))<= strong_amount < self.decimal_multiply(self.c,self.a**(i-1)):
                    step = i-1
                    break
                else:
                    pass
            return step
        else:
            pass

    def done(self):
        self.update_stack()
        won = print_and_log.print_final_profit(self.plus_stack, self.minus_stack)
        self.alarm_bot.cycle_situation(self.step, won)
        self.income_1 += won
        self.income_24 += won
        self.cycles_1 += 1
        self.cycles_24 += 1
        
        if self.step == 1:
            self.recent_counter +=1
        else:
            self.recent_counter = 0
        if self.recent_counter == self.b:
            self.recent_counter = 0
            self.good_cycles_24 += 1
            self.good_cycles_1 += 1
        if won < 0:
            self.bad_cycles_1 += 1
            self.bad_cycles_24 += 1

        self.strong_amount = 0
        self.weak_amount = None
        self.l = None
        self.s = None
        self.p = None
        self.q = None
        self.last_closed_id = None
        self.minus_stack = 0
        self.plus_stack = 0
        if self.program_on == False:
            raise errors.ProgramEndError

    
        
    def update_stack(self):
        trade = self.binance.fetch_my_trades(symbol = self.symbol, params={
            'fromId' : self.last_closed_id
        })
        is_certain = self.is_certain_profit(trade[1:], self.strong_amount)
        count = 0
        while is_certain == False:
            count += 1
            if count == 1:
                print('update stack re-entering...\n\n')
            trade = self.binance.fetch_my_trades(symbol=self.symbol, params ={
                'fromId':self.last_closed_id
            })
            is_certain = self.is_certain_profit(trade[1:], self.strong_amount)
        for t in trade[1:]:
            commission, pnl = float(t['info']['commission']), float(
                t['info']['realizedPnl'])
            self.minus_stack += commission
            self.plus_stack += pnl
        self.last_closed_id = trade[-1]['info']['id']
        #print('\n\n')

    def decimal_multiply(self, a, b):
        a = str(a)
        b = str(b)
        return float(Decimal(a)*Decimal(b))
    
    def decimal_minus(self, a, b):
        a = str(a)
        b = str(b)
        return float(Decimal(a)-Decimal(b))



    def is_certain_profit(self, trade, strong_amount):
        stack_qty = 0
        for t in trade:
            if float(t['info']['realizedPnl']) != 0:
                stack_qty += float(t['info']['qty'])
        #print('stack_qty :',stack_qty)
        #print('strong_amount :',strong_amount)
        if stack_qty >= strong_amount:
            return True
        else:
            return False


#-------------------------------------------------------------------------------------------
    def cancel_all_open_orders(self):
        self.binance.cancelAllOrders(symbol=self.symbol)

    def market_open(self, position, amount):
        if position == 'LONG':
            info = self.binance.create_order(symbol=self.symbol, type='MARKET',side='buy', amount=amount, params={
                'positionSide': 'LONG'
            })['info']
            return info
        else:
            info = self.binance.create_order(
                symbol= self.symbol, type='MARKET', side='sell', amount=amount, params={
                    'positionSide': 'SHORT'})['info']
            return info

    def limit_open(self, position, amount, price):
        if position == 'LONG':
            order = self.binance.create_order(symbol=self.symbol, type='LIMIT', side='buy', price=price,
            amount = amount, params={
                'positionSide' : 'LONG'
            })
        else:
            order = self.binance.create_order(symbol=self.symbol, type='LIMIT', side='sell', price=price,
            amount = amount, params={
                'positionSide' : 'SHORT'
            })

    def limit_close(self, position, amount, price):
        if position == 'LONG':
            order = self.binance.create_order(symbol=self.symbol, type='LIMIT', side='sell', price=price,
            amount = amount, params={
                'positionSide' : 'LONG'
            })
        else:
            order = self.binance.create_order(symbol=self.symbol, type='LIMIT', side='buy', price=price,
            amount = amount, params={
                'positionSide' : 'SHORT'
            })
    
    def stop_limit_close(self, position, amount, price, stopPrice):
        if position == 'LONG':
            try:
                order = self.binance.create_order(
                    symbol= self.symbol, type='STOP', side='sell', price=price, amount=amount, params={
                        'positionSide': 'LONG', 'stopPrice': stopPrice})
            except:
                order = self.binance.create_order(
                    symbol= self.symbol, type='LIMIT', side='sell', price=price, amount=amount, params={
                        'positionSide': 'LONG', })
        else:
            try:
                order = self.binance.create_order(
                    symbol= self.symbol, type='STOP', side='buy', price=price, amount=amount, params={
                        'positionSide': 'SHORT', 'stopPrice': stopPrice})
            except:
                order = self.binance.create_order(
                    symbol= self.symbol, type='LIMIT', side='buy', price=price, amount=amount, params={
                        'positionSide': 'SHORT', })


