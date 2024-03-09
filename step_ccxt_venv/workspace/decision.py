# control에서 설정된 정보, 방정식들을 활용해서  상한선, 하한선에
# 도달된 이후의 행위들을 정리한 파일.
# binance 객체가 필요할 때에는 해당 객체를 함수의 인자로 가져와서 사용
import ccxt
import control
import pprint
import math
import decimal
import alarm
import time


class Judger:
    def __init__(self, a, b, c, d):
        self.a = a
        self.b = b
        self.c = c
        self.d = d   # 테스트넷과 메인넷에서 달라져야한다.    => 뚫림 방지 if 문 과도 관련, 그것도 달라져야한다.
        self.step = -1
        self.strong_position = 'LONG'
        self.weak_position = 'SHORT'
        self.strong_amount = 0
        self.weak_amount = 0
        self.interval = 1
        # -----------------------------
        self.l = None
        self.s = None
        self.p = None
        self.q = None
        self.minus_stack = 0    # 최종 수익 프린트에만 반영되고, control 계산시에는 반영되지 않는다.
        self.plus_stack = 0
        self.plus = 0
        self.minimum_profit = 0
        self.expect_profit = 0
        self.p_cover = None
        self.q_cover = None
        self.cover_count = 0
        self.open_id = None
        # -----------------------------
        self.leverage = 70   # 실전에서는 레버리지 100 고정이다.
        self.minimum_Qty = 0.009
        self.last_closed_id = None
        self.program_on = True
        self.income_24 = 0
        self.income_1 = 0
        self.cycle_1 = 0
        self.cycle_24 = 0
        self.hang1_1 = 0
        self.hang2_1 = 0
        self.hang3_1 = 0
        self.hang4_1 = 0
        self.hang5_1 = 0
        self.hang1_24 = 0
        self.hang2_24 = 0
        self.hang3_24 = 0
        self.hang4_24 = 0
        self.hang5_24 = 0

        self.alarm_bot = alarm.alarm_bot()
        self.test_count = 0                  # 연습용, 곧 삭제할것임

        with open("./requirement_test.txt") as f:
            lines = f.readlines()
            api_key = lines[0].strip()
            api_secret = lines[1].strip()

        self.binance = ccxt.binanceusdm(config={
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
        })
        self.binance.set_sandbox_mode(True)  # 테스트넷 모드
        self.initiate_binance()

    def initiate_binance(self):
        # 레버리지 초기화
        leverage = self.binance.fapiPrivate_post_leverage(
            {"symbol": 'ETHUSDT', 'leverage': self.leverage})['leverage']
        leverage = int(leverage)
        if leverage == self.leverage:
            print('레버리지', leverage, '로 정상입니다.')
        else:
            # 에러 발생시켜라.
            print('레버리지 초기화 안되있다.')
            pass
        balance = self.binance.fetch_balance(
            params={"type": "future"})['used']['USDT']
        if balance == 0.0:
            print('현재 포지션 잘 비워져 있습니다.')
        else:
            # 에러 발생시켜라.
            print('현재 포지션 비워져 있지 않습니다.')
            pass

    def get_income_24(self):
        self.alarm_bot.day_situation(self.income_24)
        self.income_24 = 0

    def get_income_1(self):
        self.alarm_bot.hour_situation(self.income_1)
        self.income_1 = 0
# 횡보 통계 테스트

    def get_cycle_1(self):
        self.alarm_bot.cycle_1_situation(
            self.cycle_1, self.hang1_1, self.hang2_1, self.hang3_1, self.hang4_1, self.hang5_1)
        self.cycle_1 = 0
        self.hang1_1 = 0
        self.hang2_1 = 0
        self.hang3_1 = 0
        self.hang4_1 = 0
        self.hang5_1 = 0

    def get_cycle_24(self):
        self.alarm_bot.cycle_24_situation(
            self.cycle_24, self.hang1_24, self.hang2_24, self.hang3_24, self.hang4_24, self.hang5_24)
        self.cycle_24 = 0
        self.hang1_24 = 0
        self.hang2_24 = 0
        self.hang3_24 = 0
        self.hang4_24 = 0
        self.hang5_24 = 0

    def start_message(self):
        self.alarm_bot.start_message()

    def minus_error_message(self):
        self.alarm_bot.minus_error_message()

    def program_end_message(self):
        self.alarm_bot.program_end_message()

    def unexpected_end_message(self, e):
        self.alarm_bot.unexpected_end_message(e)

    def judge(self, program_on):
        self.program_on = program_on
        position = self.binance.fetchPositions(symbols=['ETH/USDT'])
        long_amount, short_amount, mark_price = float(position[1]['info']['positionAmt']), float(
            position[2]['info']['positionAmt']), float(position[2]['info']['markPrice'])
        if short_amount != 0.0:
            short_amount = -short_amount

        if long_amount >= short_amount:
            self.strong_position = 'LONG'
            self.weak_position = 'SHORT'
            self.strong_amount = long_amount
            self.weak_amount = short_amount
        else:
            self.strong_position = 'SHORT'
            self.weak_position = 'LONG'
            self.strong_amount = short_amount
            self.weak_amount = long_amount
        now_step = self.check_step(self.strong_amount)

        if now_step != self.step:  # 스텝의 변화가 생겼다.  now_step 은 딱 지금의 변화 전 self.step으로는 절대 못 되돌아감.
            self.cancel_all_open_orders()
            position = self.binance.fetchPositions(symbols=['ETH/USDT'])
            long_amount, short_amount, mark_price = float(position[1]['info']['positionAmt']), float(
                position[2]['info']['positionAmt']), float(position[2]['info']['markPrice'])
            l, s = float(position[1]['info']['entryPrice']), float(
                position[2]['info']['entryPrice'])
            if long_amount == 0.0:
                l = None
            if short_amount == 0.0:
                s = None
            self.l = l
            self.s = s
            if short_amount != 0.0:
                short_amount = -short_amount
            if long_amount >= short_amount:
                self.strong_position = 'LONG'
                self.weak_position = 'SHORT'
                self.strong_amount = long_amount
                self.weak_amount = short_amount
            else:
                self.strong_position = 'SHORT'
                self.weak_position = 'LONG'
                self.strong_amount = short_amount
                self.weak_amount = long_amount

            # self.l, self.s 최신화    각 케이스 고려해서 각 케이스 내부에 집어넣어라. 그래야 pq 주문을 잘 넣지 .

            now_step = self.check_step(self.strong_amount)
            # 양발인지 외발인지 확인
            if self.strong_amount == 0 or self.weak_amount == 0:  # 외발일 경우
                if self.strong_amount == 0 and self.weak_amount == 0:   # step 0 인 경우
                    if self.step == -1:
                        print('program start ! ')
                        print('\n\n\n')
                    else:
                        self.program_on = program_on
                        self.done()  # 인스턴스 변수들을 싹다 초기화 시켜준다.

                    # step0 주문 넣고
                    info = self.binance.create_order(
                        symbol='ETHUSDT', type='MARKET', side='buy', amount=self.c, params={
                            'positionSide': 'LONG'})['info']
                    self.l = float(info['avgPrice'])
                    info = self.binance.fetch_my_trades(
                        symbol='ETHUSDT', params={'limit': 1})[0]['info']

                    self.last_closed_id = info['id']
                    self.minus_stack = float(info['commission'])
                    self.plus_stack = float(info['realizedPnl'])
                    # 테스트 목적으로 훙 ㅔ 후에 꼭 지워라
                    print('minus_stack :', self.minus_stack)
                    print('plus_stack :', self.plus_stack)
                    count = 0
                    while self.plus_stack != 0:
                        count += 1
                        time.sleep(0.001)
                        info = self.binance.fetch_my_trades(
                            symbol='ETHUSDT', params={'limit': 1})[0]['info']

                        self.last_closed_id = info['id']
                        self.minus_stack = float(info['commission'])
                        self.plus_stack = float(info['realizedPnl'])
                        print(count, '번째')
                        print('minus_stack :', self.minus_stack)
                        print('plus_stack :', self.plus_stack)

                    '''print('minus_stack :', self.minus_stack)
                    print('plus_stack :', self.plus_stack)
                    print('---\n---\n---\n')'''
                    # self.l,s,p,q 최신화
                    # last_closed_id 최신화
                    self.p = round(self.l*1.0008, 2)+0.02
                    # 테스트다.888888888888888888888888888888888888888888888888888888888888888888888888888888888888
                    self.q = round(self.l*(1-0.0008*self.interval), 2)+0.01
                    #self.q = round(self.l*0.9992, 2)+0.01
                    self.q_cover = self.q
                    # stp0 에서 최소 이익 최신화

                    self.minimum_profit = self.c * \
                        (-1.0004*self.l+0.9998*self.p)
                    print('최소 보장 수익 달러 :', self.minimum_profit)
                    # step 1 주문 (p, q) 넣기
                    self.limit_close('LONG', self.p, self.c)
                    self.open_id = self.stop_limit_open(
                        'SHORT', self.q+self.d, self.c*self.a, self.q)
                    self.step = 1
                    self.strong_amount = self.c

                else:   # 찐 외발인 경우
                    # print('스텝', now_step, '진입!')
                    # print('외발')
                    # print('\n\n\n')
                    std_strong_amount = self.c*self.a**(now_step-1)
                    strong_need = std_strong_amount - self.strong_amount
                    if strong_need == 0.0:
                        pass
                    elif strong_need < self.minimum_Qty:                                        # minimum Qty 재조사!!
                        pass
                    else:
                        average = self.market_open(
                            self.strong_position, strong_need)
                        if self.strong_position == 'LONG':

                            self.l = round(
                                (l*self.strong_amount+average*strong_need)/std_strong_amount, 2)+0.01
                            self.strong_amount = std_strong_amount

                        else:
                            self.s = round(
                                (s*self.strong_amount+average*strong_need)/std_strong_amount, 2)-0.01
                            self.strong_amount = std_strong_amount

                    self.update_stack()

                    if now_step == self.b:  # 마자막 스텝인 경우
                        print('mark_price :', mark_price)
                        self.order_pq_by_last(
                            now_step,  'ONE')
                    else:
                        self.order_pq_by_step(
                            now_step,  'ONE')
                    # print('바로 위의 스텝에서 p, q 를 ', self.p, self.q, )
                    self.step = now_step

            else:  # 양발일 경우
                # print('스텝', now_step, '진입!')
                # print('양발')
                # print('\n\n\n')
                std_strong_amount = self.c*self.a**(now_step-1)
                std_weak_amount = std_strong_amount/self.a
                strong_need = std_strong_amount - self.strong_amount
                weak_need = std_weak_amount - self.weak_amount
                if strong_need == 0.0:
                    pass
                elif strong_need < self.minimum_Qty:                                        # minimum Qty 재조사!!
                    pass
                else:
                    # last_id 와 self.l 또는 self.s, 강약세 amount 최신화 필요,
                    average = self.market_open(
                        self.strong_position, strong_need)
                    if self.strong_position == 'LONG':

                        self.l = round(
                            (l*self.strong_amount+average*strong_need)/std_strong_amount, 2)+0.01
                        self.strong_amount = std_strong_amount

                    else:

                        self.s = round(
                            (s*self.strong_amount+average*strong_need)/std_strong_amount, 2)-0.01
                        self.strong_amount = std_strong_amount

                if weak_need == 0.0:
                    pass
                elif weak_need < self.minimum_Qty:
                    pass
                else:
                    average = self.market_open(self.weak_position, weak_need)
                    if self.weak_position == 'LONG':

                        self.l = round(
                            (l*self.weak_amount+average*weak_need)/std_weak_amount, 2)+0.01
                        self.weak_amount = std_weak_amount
                    else:

                        self.s = round(
                            (s*self.weak_amount+average*weak_need)/std_weak_amount, 2)-0.01
                        self.weak_amount = std_weak_amount

                self.update_stack()
                if now_step == self.b:
                    print('mark_price :', mark_price)
                    self.order_pq_by_last(
                        now_step,  'BOTH')
                else:
                    self.order_pq_by_step(
                        now_step, 'BOTH')
                # print('바로 위의 스텝에서 p, q 를 ', self.p, self.q, )
                self.step = now_step

            self.print_status()

        else:  # 계속 대기, 혹여나 뚫리는 상황만 없는지 감시해줌.
            # control 을 통해 마켓가로 살 수 있는 상, 하한선을 지정해 그 이상 혹은 이하가 되면 마켓가로 즉시 pq 주문 개별적으로 넣는다. 이후 다음 스텝 관찰.
            if self.step == self.b:
                pass
            else:

                if self.weak_position == 'SHORT':
                    if mark_price < self.q_cover:
                        try:
                            self.binance.cancelOrder(
                                self.open_id, symbol='ETHUSDT')
                        except:
                            pass
                        if self.cover_count == 2:
                            self.market_open(
                                self.weak_position, self.strong_amount*self.a-self.weak_amount)
                        else:

                            print('q 뚫림 방지 가동!')
                            self.cover_count += 1
                            self.open_id = self.stop_limit_open(self.weak_position, self.q_cover-self.d,
                                                                self.strong_amount*self.a-self.weak_amount, self.q_cover-self.d*2)
                            self.q_cover = self.q_cover - self.d*2

                else:
                    if mark_price > self.p_cover:
                        try:
                            self.binance.cancelOrder(
                                self.open_id, symbol='ETHUSDT')
                        except:
                            pass
                        if self.cover_count == 2:
                            self.market_open(
                                self.weak_position, self.strong_amount*self.a-self.weak_amount)
                        else:
                            print('p 뚫림 방지 가동!')
                            self.cover_count += 1
                            self.open_id = self.stop_limit_open(self.weak_position, self.p_cover+self.d,
                                                                self.strong_amount*self.a-self.weak_amount, self.p_cover+self.d*2)
                            self.p_cover = self.p_cover+self.d*2

        return self.step

    def done(self):   # 수익 얻을 시 모든 것들 초기화
        # 수익 얻기 위해 포지션들 정리한다.
        self.print_final_profit()
        self.l = None
        self.s = None
        self.p = None
        self.q = None
        self.minus_stack = 0
        self.plus_stack = 0
        self.plus = 0
        self.strong_position = 'LONG'
        self.weak_position = 'SHORT'
        self.strong_amount = self.c
        self.weak_amount = 0
        self.last_closed_id = None
        self.minimum_profit = 0
        self.expect_profit = 0
        self.p_cover = None
        self.q_cover = None
        self.cover_count = 0
        self.open_id = None

    def print_final_profit(self):
        self.update_stack()
        profit = self.plus_stack - self.minus_stack + self.plus
        print('minus_stack :', self.minus_stack)
        print('plus_stack :', self.plus_stack)
        print('최종 사이클 수익 :', profit)
        won = round(profit*1325.63, 2)
        # won = round(profit*1404.81, 2)
        print(won, '원')
        print('###################################################\n###################################################\n\n\n\n\n')
        self.income_24 += won
        self.income_1 += won
        self.cycle_24 += 1
        self.cycle_1 += 1
        if self.step == 1:
            self.hang1_1 += 1
            self.hang1_24 += 1
        elif self.step == 2:
            self.hang2_1 += 1
            self.hang2_24 += 1
        elif self.step == 3:
            self.hang3_1 += 1
            self.hang3_24 += 1
        elif self.step == 4:
            self.hang4_1 += 1
            self.hang4_24 += 1
        else:
            self.hang5_1 += 1
            self.hang5_24 += 1

        if profit < 0:
            self.test_count += 1
            self.alarm_bot.minus_situation(won, self.step, self.test_count)
            # 횡보를 알기 위해 일단 아래는 잠시 알림 안함
            '''if self.test_count == 5:
                raise alarm.MinuseError'''
        else:
            self.alarm_bot.plus_situation(won, self.step)
        if self.program_on == False:
            raise alarm.ProgramEndError

    def check_step(self, strong_amount):
        step = 0
        if strong_amount == 0:
            return step
        for i in range(1, self.b+1):
            if strong_amount <= self.c*self.a**(i-1):  # 이전스텝 이상 다음스텝이하 이런식으로
                step = i
                break
            else:
                pass
        return step

    def cancel_all_open_orders(self):
        self.binance.cancelAllOrders(symbol='ETHUSDT')

    # 마지막 id로부터 최신까지의 수수료, 수익을 정리해서 self.minus_stack, self.plus_stack 을 자동으로 업데이트해준다.

    def update_stack(self):
        # self.last_clsoed_id 를 통해 주문내역들 불러오고 가장 최신에 실행된 주문을 새로우 self.last_closed_id로 지정
        trade = self.binance.fetch_my_trades(
            symbol='ETHUSDT', params={'fromId': self.last_closed_id})
        while trade[-1]['info']['realizedPnl'] == 0:
            print('update stack 조회중!')
            trade = self.binance.fetch_my_trades(
                symbol='ETHUSDT', params={'fromId': self.last_closed_id})

        for t in trade[1:]:
            commission, pnl = float(t['info']['commission']), float(
                t['info']['realizedPnl'])
            self.minus_stack += commission
            self.plus_stack += pnl
            '''print(self.minus_stack)   # 확인용
            print(self.plus_stack)
            print('-----------\n\n')'''
        self.last_closed_id = trade[-1]['info']['id']

    def print_status(self):
        self.cover_count = 0
        print('step :', self.step, '\n')
        if self.step == self.b-1:
            self.alarm_bot.enter_step4()
        elif self.step == self.b:
            self.alarm_bot.enter_step5()
        else:
            pass
        # print('l, s, p, q : ', self.l, self.s, self.p, self.q)
        if self.strong_position == 'LONG':
            long_amount = self.strong_amount
            short_amount = self.weak_amount
        else:
            long_amount = self.weak_amount
            short_amount = self.strong_amount
        if self.l != None:
            if self.l == self.p:
                print('L-L-L-L-L-L-L-L-L-L-L-L ',
                      self.l, ' amt :', long_amount)
            else:
                print('----------------------- ', self.p)
                print('LLLLLLLLLLLLLLLLLLLLLLL ',
                      self.l, ' amt :', long_amount)
        else:
            print('----------------------- ', self.p)
        if self.s != None:
            if self.s == self.q:
                print('S-S-S-S-S-S-S-S-S-S-S-S ',
                      self.s, ' amt :', short_amount)
            else:
                print('SSSSSSSSSSSSSSSSSSSSSSS ',
                      self.s, ' amt :', short_amount)
                print('----------------------- ', self.q)
        else:
            print('----------------------- ', self.q)
        print('p와 q의 간격 : ', self.p-self.q)
        print('\n\n\n')

    def order_pq_by_last(self, now_step, foot):
        if foot == 'BOTH':
            if self.strong_position == 'LONG':
                # self.p, q 최신화
                self.p, self.q = control.get_p_or_q_last(self.strong_position, foot, now_step, self.l, self.s,
                                                         self.strong_amount, self.weak_amount, self.minus_stack, self.plus_stack, self.minimum_profit)

                '''if self.p < self.l:
                    self.p = self.l'''

                # p쪽 주문 2개
                self.limit_close(self.strong_position,
                                 self.p, self.strong_amount)

                self.stop_limit_close(self.weak_position,
                                      self.p, self.weak_amount, self.p-self.d)

                # q쪽 주문 2개
                self.stop_limit_close(self.weak_position,
                                      self.q, self.weak_amount, self.q+self.d)
                self.stop_limit_close(
                    self.strong_position, self.q-self.d, self.strong_amount, self.q-self.d)
                '''self.stop_limit_close(self.weak_position,
                                      self.q+self.d*0.5, self.weak_amount, self.q+self.d)
                self.stop_limit_close(
                    self.strong_position, self.q, self.strong_amount, self.q+self.d*0.5)'''

            else:
                # self.p, q 최신화
                self.p, self.q = control.get_p_or_q_last(self.strong_position, foot, now_step, self.l, self.s,
                                                         self.strong_amount, self.weak_amount, self.minus_stack, self.plus_stack, self.minimum_profit)

                '''if self.q > self.s:
                    self.q = self.s'''
                # p쪽 주문 2개
                '''self.stop_limit_close(self.weak_position,
                                      self.p-self.d*0.5, self.weak_amount, self.p-self.d)
                self.stop_limit_close(
                    self.strong_position, self.p-self.p*0.5, self.strong_amount, self.p)'''
                self.limit_close(self.weak_position,
                                 self.p, self.strong_amount)
                self.stop_market_close(
                    self.strong_position, self.p, self.strong_amount, self.p)

                # q쪽 주문 2개
                self.limit_close(self.strong_position,
                                 self.q, self.strong_amount)
                self.stop_limit_close(self.weak_position,
                                      self.q, self.weak_amount, self.q+self.d)
                '''self.stop_market_close(self.weak_position,
                                       self.q, self.weak_amount, self.q)'''
        else:
            if self.strong_position == 'LONG':
                # self.p, q 최신화
                self.p, self.q = control.get_p_or_q_last(self.strong_position, foot, now_step, self.l, self.s,
                                                         self.strong_amount, self.weak_amount, self.minus_stack, self.plus_stack, self.minimum_profit)
                '''if self.p < self.l:
                    self.p = self.l'''
                # p쪽 주문 1개
                self.limit_close(self.strong_position,
                                 self.p, self.strong_amount)
                # q쪽 주문 1개
                self.stop_limit_close(
                    self.strong_position, self.q, self.strong_amount, self.q+self.d)
            else:
                # self.p, q 최신화
                self.p, self.q = control.get_p_or_q_last(self.strong_position, foot, now_step, self.l, self.s,
                                                         self.strong_amount, self.weak_amount, self.minus_stack, self.plus_stack, self.minimum_profit)
                '''if self.q > self.s:
                    self.q = self.s'''
                # p쪽 주문 1개
                self.stop_limit_close(
                    self.strong_position, self.p, self.strong_amount, self.p-self.d)
                # q쪽 주문 1개
                self.limit_close(self.strong_position,
                                 self.q, self.strong_amount)

    def order_pq_by_step(self, now_step,  foot):
        if foot == 'BOTH':
            # 실험용
            '''print('pq 계산 전에 넣을')
            print('마이너스 스택 :', self.minus_stack)
            print('플러스 스택 :', self.plus_stack)
            print('\n\n')'''
            if self.strong_position == 'LONG':
                # self.p, q 최신화
                self.p, self.q = control.get_p_or_q_step(
                    self.strong_position, foot, now_step, self.l, self.s, self.strong_amount, self.weak_amount, self.minus_stack, self.plus_stack, self.minimum_profit)
                self.q_cover = self.q

                # p 쪽 주문 2개
                self.limit_close(self.strong_position,
                                 self.p, self.strong_amount)
                self.stop_limit_close(self.weak_position,
                                      self.p, self.weak_amount, self.p-self.d)
                # 슬리퍼리 현상 때문에 일단 폐지
                '''self.stop_market_close(self.weak_position,
                                       self.p, self.weak_amount, self.p)'''

                # q 쪽 주문 1개
                self.open_id = self.stop_limit_open(
                    self.weak_position, self.q+self.d, self.strong_amount*self.a-self.weak_amount, self.q)
            else:
                # self.p, q 최신화
                self.p, self.q = control.get_p_or_q_step(
                    self.strong_position, foot, now_step, self.l, self.s, self.strong_amount, self.weak_amount, self.minus_stack, self.plus_stack, self.minimum_profit)
                self.p_cover = self.p

                # p 쪽 주문 1개
                self.open_id = self.stop_limit_open(
                    self.weak_position, self.p-self.d, self.strong_amount*self.a-self.weak_amount, self.p)
                # q 쪽 주문 2개
                self.limit_close(self.strong_position,
                                 self.q, self.strong_amount)
                self.stop_limit_close(self.weak_position,
                                      self.q, self.weak_amount, self.q+self.d)
                '''self.stop_market_close(self.weak_position,
                                       self.q, self.weak_amount, self.q)'''
        else:
            if self.strong_position == 'LONG':
                # self.p, q 최신화
                self.p, self.q = control.get_p_or_q_step(
                    self.strong_position, foot, now_step, self.l, self.s, self.strong_amount, self.weak_amount, self.minus_stack, self.plus_stack, self.minimum_profit)
                self.q_cover = self.q
                # p 쪽 주문
                self.limit_close(self.strong_position,
                                 self.p, self.strong_amount)
                # q 쪽 주문
                self.open_id = self.stop_limit_open(self.weak_position,
                                                    self.q+self.d, self.strong_amount*self.a, self.q)
            else:
                # self.p, q 최신화
                self.p, self.q = control.get_p_or_q_step(
                    self.strong_position, foot, now_step, self.l, self.s, self.strong_amount, self.weak_amount, self.minus_stack, self.plus_stack, self.minimum_profit)
                self.p_cover = self.p
                # p 쪽 주문
                self.open_id = self.stop_limit_open(self.weak_position,
                                                    self.p-self.d, self.strong_amount*self.a, self.p)
                # q 쪽 주문
                self.limit_close(self.strong_position,
                                 self.q, self.strong_amount)

    def market_open(self, position, amount):
        if position == 'LONG':
            info = self.binance.create_order(
                symbol='ETHUSDT', type='MARKET', side='buy', amount=amount, params={
                    'positionSide': 'LONG'})['info']
            average = float(info['avgPrice'])
            self.update_stack()
            return average

        else:
            info = self.binance.create_order(
                symbol='ETHUSDT', type='MARKET', side='sell', amount=amount, params={
                    'positionSide': 'SHORT'})['info']
            average = float(info['avgPrice'])
            self.update_stack()
            return average

    def market_close(self, position, amount):
        if position == 'LONG':
            info = self.binance.create_order(
                symbol='ETHUSDT', type='MARKET', side='sell', amount=amount, params={
                    'positionSide': 'LONG'})['info']
            average = float(info['avgPrice'])
            self.update_stack()
            return average

        else:
            info = self.binance.create_order(
                symbol='ETHUSDT', type='MARKET', side='buy', amount=amount, params={
                    'positionSide': 'SHORT'})['info']
            average = float(info['avgPrice'])
            self.update_stack()
            return average

    def limit_close(self, position, price, amount):

        if position == 'LONG':
            # immedaiately error 커버하라.
            try:
                order = self.binance.create_order(
                    symbol='ETHUSDT', type='LIMIT', side='sell', price=price, amount=amount, params={
                        'positionSide': 'LONG'})  # 일단은 트리거 시장가 발동으로 해놓음. 연구가 필요함.
            except:
                pass

        else:
            try:
                order = self.binance.create_order(
                    symbol='ETHUSDT', type='LIMIT', side='buy', price=price, amount=amount, params={
                        'positionSide': 'SHORT'})  # 일단은 트리거 시장가 발동으로 해놓음. 연구가 필요함.
            except:
                pass

    def stop_limit_open(self, position, price, amount, stopPrice):
        if position == 'LONG':
            try:
                order = self.binance.create_order(
                    symbol='ETHUSDT', type='STOP', side='buy', price=price, amount=amount, params={
                        'positionSide': 'LONG', 'stopPrice': stopPrice})
            except:
                order = self.binance.create_order(
                    symbol='ETHUSDT', type='LIMIT', side='buy', price=price, amount=amount, params={
                        'positionSide': 'LONG', })

        else:
            try:
                order = self.binance.create_order(
                    symbol='ETHUSDT', type='STOP', side='sell', price=price, amount=amount, params={
                        'positionSide': 'SHORT', 'stopPrice': stopPrice})
            except:
                order = self.binance.create_order(
                    symbol='ETHUSDT', type='LIMIT', side='sell', price=price, amount=amount, params={
                        'positionSide': 'SHORT', })

        return order['id']

    def stop_limit_close(self, position, price, amount, stopPrice):
        if position == 'LONG':
            try:
                order = self.binance.create_order(
                    symbol='ETHUSDT', type='STOP', side='sell', price=price, amount=amount, params={
                        'positionSide': 'LONG', 'stopPrice': stopPrice})
            except:
                order = self.binance.create_order(
                    symbol='ETHUSDT', type='LIMIT', side='sell', price=price, amount=amount, params={
                        'positionSide': 'LONG', })
        else:
            try:
                order = self.binance.create_order(
                    symbol='ETHUSDT', type='STOP', side='buy', price=price, amount=amount, params={
                        'positionSide': 'SHORT', 'stopPrice': stopPrice})
            except:
                order = self.binance.create_order(
                    symbol='ETHUSDT', type='LIMIT', side='buy', price=price, amount=amount, params={
                        'positionSide': 'SHORT', })

    def stop_market_close(self, position, price, amount, stopPrice):
        if position == 'LONG':
            try:
                order = self.binance.create_order(
                    symbol='ETHUSDT', type='STOP_MARKET', side='sell', amount=amount, params={
                        'positionSide': 'LONG', 'stopPrice': stopPrice})
            except:
                order = self.binance.create_order(
                    symbol='ETHUSDT', type='MARKET', side='sell', amount=amount, params={
                        'positionSide': 'LONG', })
        else:
            try:
                order = self.binance.create_order(
                    symbol='ETHUSDT', type='STOP_MARKET', side='buy', amount=amount, params={
                        'positionSide': 'SHORT', 'stopPrice': stopPrice})
            except:
                order = self.binance.create_order(
                    symbol='ETHUSDT', type='MARKET', side='buy', amount=amount, params={
                        'positionSide': 'SHORT', })

    def take_profit_close(self, position, price, amount, stopPrice):
        pass
