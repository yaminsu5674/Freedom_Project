import time

global unit
global rate
unit = 'BTC'
rate = 1300


def print_surf_status(l, s, p_l, p_s,  q_l, q_s, amount_l, amount_s, step_l, step_s):
    interval_l = p_l - l
    interval_l = '{:.1f}'.format(interval_l)
    l = '{:.1f}'.format(l)
    p_l = '{:.1f}'.format(p_l)
    q_l = '{:.1f}'.format(q_l)
    try:
        interval_s = s - p_s
        interval_s = '{:.1f}'.format(interval_s)
    except:
        interval_s = None
    
    try:
        s = '{:.1f}'.format(s)
    except:
        s = None
    try:
        p_s = '{:.1f}'.format(p_s)
    except:
        p_s = None
    try:
        q_s = '{:.1f}'.format(q_s)
    except:
        q_s = None
    now_time = time.strftime('%c', time.localtime(time.time()))
    print(now_time)
    a = '%-35s%-35s' % ('step_L : '+str(step_l),'step_S : '+str(step_s) )
    print(a)
    a = '%-35s%-35s' % ('------------ '+str(p_l), '------------ '+str(q_s))
    print(a)
    a = '%-35s%-35s' % ('LLLLLLLLLLLL '+str(l)+'  '+str(amount_l)+str(unit), 'SSSSSSSSSSSS '+str(s)+'  '+str(amount_s)+str(unit))
    print(a)
    a = '%-35s%-35s' % ('------------ '+str(q_l), '------------ '+str(p_s))
    print(a)
    a = '%-35s%-35s' % ('p-l interval : '+str(interval_l),'s-p interval : '+str(interval_s) )
    print(a)
    print('\n\n')
        
   


def print_final_profit(position, plus_stack, minus_stack):
        profit = plus_stack - minus_stack
        print('minus_stack :', minus_stack)
        print('plus_stack :', plus_stack)
        if position == 0:
            print("Long cycle's final profit :", profit)
        else:
            print("Short cycle's final profit :", profit)
        won = round(profit*rate, 2)
        print(won, 'won')
        print('###################################################\n###################################################\n\n\n\n')
        return won