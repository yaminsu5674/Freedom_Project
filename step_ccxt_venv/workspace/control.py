# a,b,c 배율, 지지대개수, 최소단위 등을 유동적으로 관리하기 위한 모듈
# 적절한 상황에서 이 모듈로부터의 객체를 사용할 예정
# 방정식 함수들을 객체가 가지고 있다.
# api 위반을 제한하기 위한 기능도 있다.
# 에러 타입들도 정리돼 있다.

global a
a = 5
global interval
interval = 1


def get_p_or_q_step(direction, foot, now_step, l, s, strong_amount, weak_amount, minus_stack, plus_stack, minimum_profit):
    p, q = None, None
    #want_profit = minimum_profit*a**(now_step-1)
    want_profit = minimum_profit*a**(now_step-1)/2
    #want_profit = minimum_profit

    if foot == 'BOTH':
        if direction == 'LONG':

            p = round((want_profit + strong_amount*l-weak_amount*s-plus_stack+minus_stack) /
                      (strong_amount-weak_amount-(strong_amount*0.0002+weak_amount*0.0004)), 2)+0.01
            q = l-interval*(p-l)
            #q = l-(p-l)

        else:

            q = round((want_profit - strong_amount*s+weak_amount*l-plus_stack+minus_stack) /
                      (weak_amount-strong_amount-(strong_amount*0.0002+weak_amount*0.0004)), 2)-0.01
            #p = s+(s-q)
            p = s+interval*(s-q)

    else:  # 회귀한 케이스
        want_profit = want_profit*a
        if direction == 'LONG':

            p = round((want_profit+strong_amount*l-plus_stack +
                      minus_stack)/(strong_amount-strong_amount*0.0002), 2)+0.01
            #q = round(l*0.9992, 2)+0.01
            q = round(l*(1-0.0008*interval), 2)+0.01

        else:
            #p = round(s*1.0008, 2)-0.01
            p = round(s*(1+0.0008*interval), 2)-0.01
            q = round((want_profit-strong_amount*s-plus_stack+minus_stack) /
                      (-strong_amount-strong_amount*0.0002), 2)-0.01
    return p, q


def get_p_or_q_last(direction, foot, now_step, l, s, strong_amount, weak_amount, minus_stack, plus_stack, minimum_profit):
    p, q = None, None
    #want_profit = minimum_profit * a**(now_step-1)
    want_profit = minimum_profit*a**(now_step-1)/2
    #want_profit = minimum_profit
    if foot == 'BOTH':
        if direction == 'LONG':
            p = round((want_profit-plus_stack+strong_amount*l-weak_amount*s+minus_stack) /
                      (strong_amount-weak_amount-(strong_amount*0.0002+weak_amount*0.0004)), 2)
            #q = l - 0.01
            q = round((l+s)/2, 2)+0.01
        else:
            #p = s+0.01
            p = round((l+s)/2, 2)-0.01
            q = round((want_profit-plus_stack-strong_amount*s+l*weak_amount+minus_stack) /
                      (weak_amount-strong_amount-(strong_amount*0.0002+weak_amount*0.0004)), 2)
    else:
        if direction == 'LONG':
            p = round((want_profit-plus_stack+strong_amount*l +
                      minus_stack)/(strong_amount-strong_amount*0.0002), 2)
            #q = l - 0.01
            q = round(l*0.9995, 2)+0.01
        else:
            #p = s + 0.01
            p = round(s*1.0005, 2)-0.01
            q = round((want_profit-plus_stack-strong_amount*s +
                      minus_stack)/(-strong_amount-strong_amount*0.0002), 2)
    return p, q
