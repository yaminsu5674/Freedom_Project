from decimal import Decimal


def get_p(position, avgPrice, a, d):
    if position == 0:
        p = round(avgPrice*(1+d), 1)+0.1
        return p
    else:
        p = round(avgPrice*(1-d), 1)-0.1
        return p

def get_q(position, avgPrice, a, d):
    if position == 0:
        q = round((a*(avgPrice*(1-d))-avgPrice)/(a-1), 1)
        return q
    else:
        q = round((a*(avgPrice*(1+d))-avgPrice)/(a-1), 1)
        return q

def get_q_last(position, avgPrice, a, d):
    if position == 0:
        q = round(avgPrice*(1-d), 1)+0.1
        return q
    else:
        q = round(avgPrice*(1+d), 1)-0.1
        return q

