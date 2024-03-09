import ccxt
import alarm
import print_and_log
import errors
import control
import pprint
import time
from decimal import Decimal
from ccxt.base import errors as binance_errors

class Judger:
    def __init__(self, a_0, a_1, b_0, b_1, c, d_0, d_1, symbol, leverage, net):
        self.a_0 = a_0
        self.a_1 = a_1
        self.b_0 = b_0
        self.b_1 = b_1
        self.c = c
        self.middle_0 = self.decimal_multiply(self.c,self.a_0**(self.b_0-1))
        self.middle_1 = self.decimal_multiply(self.middle_0,self.a_1)
        self.original_d_0 = d_0
        self.d_0 = d_0
        self.d_1 = d_1
        self.program_on = True
        self.symbol = symbol
        self.leverage = leverage
        self.step_l = -1
        self.max_step_l = -1
        self.step_s = -1
        self.max_step_s = -1
        self.weight = 0
        self.orders_num = 0
        #-------------------------------
        self.amount_l = 0
        self.amount_s = 0
        self.l = None
        self.p_l = None
        self.p_l_id = None
        self.q_l = None
        self.q_l_id = None
        self.s = None
        self.p_s = None
        self.p_s_id = None
        self.q_s = None
        self.q_s_id = None
        self.last_closed_l = None
        self.last_closed_s = None
        self.minus_stack_l = 0
        self.plus_stack_l = 0
        self.minus_stack_s = 0
        self.plus_stack_s = 0
        #-------------------------------
        self.balance = 0
        self.income_24 = 0
        self.cycles_24 = 0
        self.bad_cycles_24 = 0
        self.good_cycles_24  = 0
        self.income_1 = 0
        self.cycles_1 = 0
        self.bad_cycles_1 = 0
        self.good_cycles_1 = 0
        self.program_off_counter = 0
        self.program_on_l = True
        self.program_on_s = True
        self.alarm_bot = alarm.alarm_bot()
        self.net = net
        if self.net == 1:
            self.url = "./requirement_test.txt"
        else:
            self.url = "./requirement.txt"
        with open(self.url) as f:
            lines = f.readlines()
            api_key = lines[0].strip()
            api_secret = lines[1].strip()

        self.binance = ccxt.binanceusdm(config={
            'apiKey' : api_key,
            'secret' : api_secret,
            'enableRateLimit' : True
        })
        if self.net == 1:
            self.binance.set_sandbox_mode(True)
        else:
            pass
        self.initiate_balance()


    def initiate_balance(self):
        leverage = int(self.binance.fapiPrivate_post_leverage({"symbol" : self.symbol, "leverage" : self.leverage})['leverage'])
        self.weight_plus(5)#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        #&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        if leverage == self.leverage:
            print('leverage :', leverage, 'yes right!')
        else:
            raise errors.LeverageError
        balance_1 = self.binance.fetch_balance(params = {"type" : "future"})['used']
        self.weight_plus(5)#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        #&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        pprint.pprint(balance_1)
        balance = balance_1['USDT']
        if balance == 0.0:
            print('Position is clean now!\n\n\n')
        else:
            print(balance)
            raise errors.BalanceError

    def change_mode(self):
        if self.d_0 == self.d_1:
            self.d_0 = self.original_d_0
        else:
            self.d_0 = self.d_1

    
    def weight_plus(self, w):
        self.weight+=w

    def orders_num_plus(self):
        self.orders_num+=1

    def weight_show(self):
        temp = self.weight
        '''print('weight per minute :',self.weight)
        print('\n\n')'''
        self.weight = 0
        return temp

    def orders_num_show(self):
        temp = self.orders_num
        '''print('orders number per 10seconds :',self.orders_num)
        print('\n\n')'''
        self.orders_num = 0
        return temp

    def check_balance(self):
        self.balance = self.binance.fetch_balance(params = {"type" : "future"})['total']['USDT']
        self.weight_plus(5)#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        #&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
 




    def get_24(self):
        self.alarm_bot.day_situation(self.income_24, self.cycles_24, self.bad_cycles_24, self.good_cycles_24)
        self.income_24 = 0
        self.cycles_24 = 0
        self.bad_cycles_24 = 0
        self.good_cycles_24 = 0

    def get_1(self):
        self.alarm_bot.hour_situation(self.income_1, self.cycles_1, self.bad_cycles_1, self.good_cycles_1, self.balance)
        self.alarm_bot.day_situation(self.income_24, self.cycles_24, self.bad_cycles_24, self.good_cycles_24)
        self.income_1 = 0
        self.cycles_1 = 0
        self.bad_cycles_1 = 0
        self.good_cycles_1 = 0


    def judge(self, program_on):
        self.program_on = program_on

        position = self.binance.fetchPositions(symbols = [self.symbol])
        self.weight_plus(5)#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        #&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        amount_l = float(position[1]['info']['positionAmt'])
        amount_s = float(position[2]['info']['positionAmt'])
        if amount_s != 0.0:
            amount_s = -amount_s
        mark_price = float(position[1]['info']['markPrice'])

        now_step_l = self.check_step(amount_l)
        now_step_s = self.check_step(amount_s)

        if now_step_l != self.step_l:   # step_long variated!
            if self.step_l == -1:
                pass
            else:
                self.cancel_all_open_orders(0)
            
            position = self.binance.fetchPositions(symbols=[self.symbol])
            self.weight_plus(5)#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        #&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
            amount_l = float(position[1]['info']['positionAmt'])
            self.l = float(position[1]['info']['entryPrice'])
            now_step_l = self.check_step(amount_l)

            if now_step_l == 0:
                if self.step_l == -1:
                    pass
                else:
                    self.done(0)
                if self.program_on_l == True:
                    info = self.market_open('LONG', self.c)
                    self.l = float(info['avgPrice'])
                    self.amount_l = self.c
                    self.last_closed_l = info['updateTime']

                    self.step_l = 1
                    self.p_l = control.get_p(0, self.l, self.a_0, self.d_0)
                    self.q_l = control.get_q(0, self.l, self.a_0, self.d_0)
                    self.p_l_id = int(self.limit_close('LONG', self.decimal_multiply(self.c,self.a_0**(self.step_l)), self.p_l)['orderId'])
                    self.q_l_id = int(self.limit_open('LONG', self.decimal_minus(self.decimal_multiply(self.c,(self.a_0**self.step_l)),self.amount_l), self.q_l)['orderId'])
                    print_and_log.print_surf_status(self.l, self.s, self.p_l, self.p_s, self.q_l, self.q_s, self.amount_l, self.amount_s, self.step_l, self.step_s)
                else:
                    self.step_l = -1
               

            elif now_step_l < self.b_0:
                self.amount_l = amount_l
                self.p_l = control.get_p(0, self.l, self.a_0, self.d_0)
                self.q_l = control.get_q(0, self.l, self.a_0, self.d_0)
                self.p_l_id = int(self.limit_close('LONG', self.decimal_multiply(self.c,self.a_0**now_step_l), self.p_l)['orderId'])
                self.q_l_id = int(self.limit_open('LONG', self.decimal_minus(self.decimal_multiply(self.c,(self.a_0**now_step_l)),self.amount_l), self.q_l)['orderId'])
                self.step_l = now_step_l
                print_and_log.print_surf_status(self.l, self.s, self.p_l, self.p_s, self.q_l, self.q_s, self.amount_l, self.amount_s, self.step_l, self.step_s)


            elif now_step_l == self.b_0:
                self.amount_l = amount_l
                self.p_l = control.get_p(0, self.l, self.a_1, self.d_1)
                self.q_l = control.get_q(0, self.l, self.a_1, self.d_1)
                self.p_l_id = int(self.limit_close('LONG', self.middle_1, self.p_l)['orderId'])
                self.q_l_id = int(self.limit_open('LONG', self.decimal_minus(self.middle_1,self.amount_l), self.q_l)['orderId'])
                self.step_l = now_step_l
                print_and_log.print_surf_status(self.l, self.s, self.p_l, self.p_s, self.q_l, self.q_s, self.amount_l, self.amount_s, self.step_l, self.step_s)


            elif now_step_l == self.b_1:
                self.amount_l = amount_l
                self.p_l = control.get_p(0, self.l, self.a_1, self.d_1)
                self.q_l = control.get_q_last(0, self.l, self.a_1, self.d_1)
                self.p_l_id = int(self.limit_close('LONG', self.decimal_multiply(self.middle_1,self.a_1**(now_step_l-self.b_0)), self.p_l)['orderId'])
                self.q_l_id = int(self.stop_limit_close('LONG', self.decimal_multiply(self.middle_1,self.a_1**(now_step_l-self.b_0)), self.q_l, self.q_l)['orderId'])
                self.step_l = now_step_l
                print_and_log.print_surf_status(self.l, self.s, self.p_l, self.p_s, self.q_l, self.q_s, self.amount_l, self.amount_s, self.step_l, self.step_s)


            else:
                self.amount_l = amount_l
                self.p_l = control.get_p(0, self.l, self.a_1, self.d_1)
                self.q_l = control.get_q(0, self.l, self.a_1, self.d_1)
                self.p_l_id = int(self.limit_close('LONG', self.decimal_multiply(self.middle_1,self.a_1**(now_step_l-self.b_0)), self.p_l)['orderId'])
                self.q_l_id = int(self.limit_open('LONG', self.decimal_minus(self.decimal_multiply(self.middle_1,self.a_1**(now_step_l-self.b_0)),self.amount_l), self.q_l)['orderId'])
                self.step_l = now_step_l
                print_and_log.print_surf_status(self.l, self.s, self.p_l, self.p_s, self.q_l, self.q_s, self.amount_l, self.amount_s, self.step_l, self.step_s)

            if self.step_l >= self.max_step_l:
                self.max_step_l = self.step_l



        else:   # no step_ long variation
            status = self.fetch_order(0)
            if status == 'FILLED':
                # 현잿 스텝 주문 재설정
                self.step_l = -2
            else:
                pass
            
            if self.step_l == self.b_1:
                if mark_price < self.decimal_multiply(self.l, self.decimal_minus(1,self.decimal_multiply(self.d_1,1.5))):
                    
                    info = self.market_close('LONG', self.decimal_multiply(self.middle_1,self.a_1**(now_step_l-self.b_0)))



        #----------------------------------------------------------------------------
        #----------------------------------------------------------------------------
        #----------------------------------------------------------------------------
        
        
        if now_step_s != self.step_s:     # step_short variated!
            if self.step_s == -1:
                pass
            else:
                self.cancel_all_open_orders(1)
            position = self.binance.fetchPositions(symbols=[self.symbol])
            self.weight_plus(5)#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        #&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
            amount_s = float(position[2]['info']['positionAmt'])
            if amount_s != 0.0:
                amount_s = -amount_s
            self.s = float(position[2]['info']['entryPrice'])
            now_step_s = self.check_step(amount_s)

            if now_step_s == 0:
                if self.step_s == -1:
                    pass
                else:
                    self.done(1)
                if self.program_on_s == True:
                    info = self.market_open('SHORT', self.c)
                    self.s = float(info['avgPrice'])
                    self.amount_s = self.c
                    self.last_closed_s = info['updateTime']

                    self.step_s = 1
                    self.p_s = control.get_p(1, self.s, self.a_0, self.d_0)
                    self.q_s = control.get_q(1, self.s, self.a_0, self.d_0)
                    self.p_s_id = int(self.limit_close('SHORT', self.decimal_multiply(self.c,self.a_0**(self.step_s)), self.p_s)['orderId'])
                    self.q_s_id = int(self.limit_open('SHORT', self.decimal_minus(self.decimal_multiply(self.c,(self.a_0**self.step_s)),self.amount_s), self.q_s)['orderId'])
                    print_and_log.print_surf_status(self.l, self.s, self.p_l, self.p_s, self.q_l, self.q_s, self.amount_l, self.amount_s, self.step_l, self.step_s)
                else:
                    self.step_s = -1

            elif now_step_s < self.b_0:
                self.amount_s = amount_s
                self.p_s = control.get_p(1, self.s, self.a_0, self.d_0)
                self.q_s = control.get_q(1, self.s, self.a_0, self.d_0)
                self.p_s_id = int(self.limit_close('SHORT', self.decimal_multiply(self.c,self.a_0**now_step_s), self.p_s)['orderId'])
                self.q_s_id = int(self.limit_open('SHORT', self.decimal_minus(self.decimal_multiply(self.c,(self.a_0**now_step_s)),self.amount_s), self.q_s)['orderId'])
                self.step_s = now_step_s
                print_and_log.print_surf_status(self.l, self.s, self.p_l, self.p_s, self.q_l, self.q_s, self.amount_l, self.amount_s, self.step_l, self.step_s)

            elif now_step_s == self.b_0:
                self.amount_s = amount_s
                self.p_s = control.get_p(1, self.s, self.a_1, self.d_1)
                self.q_s = control.get_q(1, self.l, self.a_1, self.d_1)
                self.p_s_id = int(self.limit_close('SHORT', self.middle_1, self.p_s)['orderId'])
                self.q_s_id = int(self.limit_open('SHORT', self.decimal_minus(self.middle_1,self.amount_s), self.q_s)['orderId'])
                self.step_s = now_step_s
                print_and_log.print_surf_status(self.l, self.s, self.p_l, self.p_s, self.q_l, self.q_s, self.amount_l, self.amount_s, self.step_l, self.step_s)

            
            elif now_step_s == self.b_1:
                self.amount_s = amount_s
                self.p_s = control.get_p(1, self.s, self.a_1, self.d_1)
                self.q_s = control.get_q_last(1, self.s, self.a_1, self.d_1)
                self.p_s_id = int(self.limit_close('SHORT', self.decimal_multiply(self.middle_1,self.a_1**(now_step_s-self.b_0)), self.p_s)['orderId'])
                self.q_s_id = int(self.stop_limit_close('SHORT', self.decimal_multiply(self.middle_1,self.a_1**(now_step_s-self.b_0)), self.q_s, self.q_s)['orderId'])
                self.step_s = now_step_s
                print_and_log.print_surf_status(self.l, self.s, self.p_l, self.p_s, self.q_l, self.q_s, self.amount_l, self.amount_s, self.step_l, self.step_s)

            else:
                self.amount_s = amount_s
                self.p_s = control.get_p(1, self.s, self.a_1, self.d_1)
                self.q_s = control.get_q(1, self.s, self.a_1, self.d_1)
                self.p_s_id = int(self.limit_close('SHORT', self.decimal_multiply(self.middle_1,self.a_1**(now_step_s-self.b_0)), self.p_s)['orderId'])
                self.q_s_id = int(self.limit_open('SHORT', self.decimal_minus(self.decimal_multiply(self.middle_1,self.a_1**(now_step_s-self.b_0)),self.amount_s), self.q_s)['orderId'])
                self.step_s = now_step_s
                print_and_log.print_surf_status(self.l, self.s, self.p_l, self.p_s, self.q_l, self.q_s, self.amount_l, self.amount_s, self.step_l, self.step_s)


            if self.step_s >= self.max_step_s:
                self.max_step_s = self.step_s


        else:    # no step_ short variation
            status = self.fetch_order(1)
            if status == 'FILLED':
                # 현잿 스텝 주문 재설정
                self.step_s = -2
            else:
                pass
            if self.step_s == self.b_1:
                if mark_price < self.decimal_multiply(self.s, self.decimal_plus(1,self.decimal_multiply(self.d_1,1.5))):
                    info = self.market_close('SHORT', self.decimal_multiply(self.middle_1,self.a_1**(now_step_l-self.b_0)))




#-------------------------------------------------------------------------------------------

    def check_step(self, amount):
        step = 0
        if amount == 0:
            return step
        for i in range(2, self.b_0+1):
                if self.decimal_multiply(self.c,self.a_0**(i-2))<= amount < self.decimal_multiply(self.c,self.a_0**(i-1)):
                    step = i-1
                    return step
        if self.middle_0 <= amount < self.middle_1:
            step = self.b_0
            return step
        for i in range(2, self.b_1-self.b_0+2):
            if self.decimal_multiply(self.middle_1,self.a_1**(i-2))<= amount < self.decimal_multiply(self.middle_1,self.a_1**(i-1)):
                    step = i-1+self.b_0
                    return step



    def done(self, position):
        if position == 0:
            self.update_stack(0)
            won = print_and_log.print_final_profit(0, self.plus_stack_l, self.minus_stack_l)
            if won < 0:
                self.alarm_bot.minus_message(won)
            self.alarm_bot.cycle_situation(0, self.max_step_l, self.step_s,won)
            self.amount_l = 0
            self.l = None
            self.p_l = None
            self.p_l_id = None
            self.q_l = None
            self.q_l_id =None
            self.last_closed_l = None
            self.minus_stack_l = 0
            self.plus_stack_l = 0
            self.max_step_l = 0

    
        else:
            self.update_stack(1)
            won = print_and_log.print_final_profit(1, self.plus_stack_s, self.minus_stack_s)
            if won < 0:
                self.alarm_bot.minus_message(won)
            self.alarm_bot.cycle_situation(1, self.max_step_s, self.step_l, won)
            self.amount_s = 0
            self.s = None
            self.p_s = None
            self.p_s_id = None
            self.q_s = None
            self.q_s_id = None
            self.last_closed_s = None
            self.minus_stack_s = 0
            self.plus_stack_s = 0
            self.max_step_s = 0

        self.income_1 += won
        self.income_24 += won
        self.cycles_1 += 1
        self.cycles_24 += 1
        if won < 0:
            self.bad_cycles_1 += 1
            self.bad_cycles_24 += 1
        if self.program_on == False:
            if position == 0:
                self.program_on_l = False
            else:
                self.program_on_s = False
            self.program_off_counter += 1
            if self.program_off_counter == 2:
                self.alarm_bot.program_end_message()
                raise errors.ProgramEndError


    def update_stack(self, position):
        if position == 0:
            trade = self.binance.fetch_my_trades(symbol = self.symbol, params={
            'startTime' : self.last_closed_l
            })
            self.weight_plus(5)#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        #&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
            is_certain = self.is_certain_profit(0, trade, self.amount_l)
            count = 0
            while is_certain == False:
                count += 1
                if count == 1:
                    print('update stack re-entering...\n\n')
                if count == 100:
                    raise errors.UpdateStackError
                trade = self.binance.fetch_my_trades(symbol=self.symbol, params ={
                'startTime':self.last_closed_l})
                self.weight_plus(5)#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        #&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
                is_certain = self.is_certain_profit(0, trade, self.amount_l)
            for t in trade:
                if t['info']['positionSide'] == 'SHORT':
                    continue
                commission, pnl = float(t['info']['commission']), float(
                t['info']['realizedPnl'])
                self.minus_stack_l += commission
                self.plus_stack_l += pnl

        else:
            trade = self.binance.fetch_my_trades(symbol = self.symbol, params={
            'startTime' : self.last_closed_s
            })
            self.weight_plus(5)#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        #&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
            is_certain = self.is_certain_profit(1, trade, self.amount_s)
            count = 0
            while is_certain == False:
                count += 1
                if count == 1:
                    print('update stack re-entering...\n\n')
                if count == 100:
                    raise errors.UpdateStackError
                trade = self.binance.fetch_my_trades(symbol=self.symbol, params ={
                'startTime':self.last_closed_s})
                self.weight_plus(5)#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        #&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
                is_certain = self.is_certain_profit(1, trade, self.amount_s)
            for t in trade:
                if t['info']['positionSide'] == 'LONG':
                    continue
                commission, pnl = float(t['info']['commission']), float(
                t['info']['realizedPnl'])
                self.minus_stack_s += commission
                self.plus_stack_s += pnl

        

    def decimal_multiply(self, a, b):
        a = str(a)
        b = str(b)
        return float(Decimal(a)*Decimal(b))
    
    def decimal_minus(self, a, b):
        a = str(a)
        b = str(b)
        return float(Decimal(a)-Decimal(b))

    def decimal_plus(self, a, b):
        a = str(a)
        b = str(b)
        return float(Decimal(a)+Decimal(b))


    def is_certain_profit(self, position, trade, amount):
        stack_qty = 0
        if position == 0:
            for t in trade:
                if t['info']['positionSide'] == 'SHORT':
                    continue
                if float(t['info']['realizedPnl']) != 0:
                    stack_qty += float(t['info']['qty'])
            if stack_qty >= amount:
                return True
            else:
                return False
        else:
            for t in trade:
                if t['info']['positionSide'] == 'LONG':
                    continue
                if float(t['info']['realizedPnl']) != 0:
                    stack_qty += float(t['info']['qty'])
            if stack_qty >= amount:
                return True
            else:
                return False

        
#-------------------------------------------------------------------------------------------
    
    def fetch_order(self,position):
        self.weight_plus(1)#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
            #&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        if position == 0:
            status = self.binance.fetchOrder(symbol=self.symbol, id=self.p_l_id)['info']['status']
            return status
        else:
            status = self.binance.fetchOrder(symbol=self.symbol, id=self.p_s_id)['info']['status']
            return status


        
    def cancel_all_open_orders(self, position):
        self.weight_plus(2)#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        #&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        if position == 0:
            try:
                self.binance.cancelOrder(id = self.p_l_id, symbol = self.symbol, params={'orderId' : (self.p_l_id) })
            except:
                pass
            try:
                self.binance.cancelOrder(id = self.q_l_id, symbol = self.symbol, params={'orderId' : (self.q_l_id) })
            except:
                pass
        else:
            try:
                self.binance.cancelOrder(id = self.p_s_id, symbol = self.symbol, params={'orderId' : (self.p_s_id) })
            except:
                pass
            try:
                self.binance.cancelOrder(id = self.q_s_id, symbol = self.symbol, params={'orderId' : (self.q_s_id) })
            except:
                pass

    def market_open(self, position, amount):
        self.weight_plus(1)#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
            #&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        self.orders_num_plus()#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
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

    def market_close(self, position, amount):
        self.weight_plus(1)#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
            #&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        self.orders_num_plus()#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        if position == 'LONG':
            info = self.binance.create_order(symbol=self.symbol, type='MARKET',side='sell', amount=amount, params={
                'positionSide': 'LONG'
            })['info']
            return info
        else:
            info = self.binance.create_order(
                symbol= self.symbol, type='MARKET', side='buy', amount=amount, params={
                    'positionSide': 'SHORT'})['info']
            return info

    def limit_open(self, position, amount, price):
        self.weight_plus(1)#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
            #&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        self.orders_num_plus()#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        if position == 'LONG':
            try:
                info = self.binance.create_order(symbol=self.symbol, type='LIMIT', side='buy', price=price,
                amount = amount, params={
                'positionSide' : 'LONG'
                })['info']
                return info
            except binance_errors.InsufficientFunds as e:
                info = self.market_close('LONG', self.decimal_multiply(self.middle_1,self.a_1**(self.b_1-self.b_0)))
                raise errors.InsufficientError
            except binance_errors.InvalidOrder as e:
                info = self.market_close('LONG', self.decimal_multiply(self.middle_1,self.a_1**(self.b_1-self.b_0)))
                raise errors.LeverageError
                # 추후 업데이트 예정
        else:
            try:
                info = self.binance.create_order(symbol=self.symbol, type='LIMIT', side='sell', price=price,
                amount = amount, params={
                    'positionSide' : 'SHORT'
                })['info']
                return info
            except binance_errors.InsufficientFunds as e:
                info = self.market_close('SHORT', self.decimal_multiply(self.middle_1,self.a_1**(self.b_1-self.b_0)))
                raise errors.InsufficientError
            except binance_errors.InvalidOrder as e:
                info = self.market_close('SHORT', self.decimal_multiply(self.middle_1,self.a_1**(self.b_1-self.b_0)))
                raise errors.LeverageError
                # 추후 업데이트 예정

    def limit_close(self, position, amount, price):
        self.weight_plus(1)#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
            #&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        self.orders_num_plus()#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        if position == 'LONG':
            info = self.binance.create_order(symbol=self.symbol, type='LIMIT', side='sell', price=price,
            amount = amount, params={
                'positionSide' : 'LONG'
            })['info']
            return info
        else:
            info = self.binance.create_order(symbol=self.symbol, type='LIMIT', side='buy', price=price,
            amount = amount, params={
                'positionSide' : 'SHORT'
            })['info']
            return info
    
    def stop_limit_close(self, position, amount, price, stopPrice):
        if position == 'LONG':
            try:
                self.weight_plus(1)#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
            #&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
                self.orders_num_plus()#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                info = self.binance.create_order(
                    symbol= self.symbol, type='STOP', side='sell', price=price, amount=amount, params={
                        'positionSide': 'LONG', 'stopPrice': stopPrice})['info']
                return info
            except:
                self.weight_plus(1)#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
            #&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
                self.orders_num_plus()#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                info = self.binance.create_order(
                    symbol= self.symbol, type='LIMIT', side='sell', price=price, amount=amount, params={
                        'positionSide': 'LONG', })['info']
                return info
        else:
            try:
                self.weight_plus(1)#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
            #&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
                self.orders_num_plus()#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                info = self.binance.create_order(
                    symbol= self.symbol, type='STOP', side='buy', price=price, amount=amount, params={
                        'positionSide': 'SHORT', 'stopPrice': stopPrice})['info']
                return info
            except:
                self.weight_plus(1)#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
            #&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
                self.orders_num_plus()#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                info = self.binance.create_order(
                    symbol= self.symbol, type='LIMIT', side='buy', price=price, amount=amount, params={
                        'positionSide': 'SHORT', })['info']
                return info