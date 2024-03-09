import alarm
import asyncio
import time
from decimal import Decimal
import telegram

mode = 0
a = 3
b = 6
c = 0.001

print(float(Decimal('9')*Decimal('0.001')))

def check_step(strong_amount):
        step = 0
        if strong_amount == 0:
            return step
        if mode == 0:
            for i in range(2, b+2):
                print(c*a**(i-2),'<=',strong_amount,'<', c*a**(i-1),'?\n')
                if c*a**(i-2)<= strong_amount < c*a**(i-1):
                    step = i-1
                    break
                else:
                    pass
            print('step :',step)
            return step
        else:
            pass

check_step(0.009)


