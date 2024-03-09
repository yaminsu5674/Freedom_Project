import time

global unit
unit = 'BTC'


def print_surf_status(position, l, s, p, q, amount, surf):
    interval = p - l
    interval = '{:.1f}'.format(interval)
    l = '{:.1f}'.format(l)
    p = '{:.1f}'.format(p)
    q = '{:.1f}'.format(q)
    now_time = time.strftime('%c', time.localtime(time.time()))
    if position == 'LONG':
        print('surf :', surf)
        print(now_time)
        print('----------------------- ', p)
        print('LLLLLLLLLLLLLLLLLLLLLLL ', l, str(amount)+str(unit))
        print('----------------------- ', q)
        print('p-l interval :',interval)
        print('\n\n')
        
    else:
        pass


def print_final_profit(position, plus_stack, minus_stack):
        profit = plus_stack - minus_stack
        print('minus_stack :', minus_stack)
        print('plus_stack :', plus_stack)
        if position == 0:
            print("Long cycle's final profit :", profit)
        else:
            print("Short cycle's final profit :", profit)
        won = round(profit*1230, 2)
        print(won, 'won')
        print('###################################################\n###################################################\n\n\n\n')
        return won