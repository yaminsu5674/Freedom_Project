import ccxt
import time
import alarm
import decision
import errors

global program_on
global step
global timer_count
global timer_1
program_on = True
step = 0  # 손해 발생시 step -1으로 전환
timer_count = 0
timer_1 = time.time()

bot = decision.Judger(3, 6, 0.001, "BTCUSDT", "LONG", 100) # step배율, 지지대 개수, 최소 시드, 종목, 주포지션, 레버리지
bot.alarm_bot.start_message()

while(1):
    try:
        now_time = time.time()
        if now_time-timer_1 >3600:
            timer_count += 1
            bot.get_1()
            timer_1 = now_time
        if timer_count == 24:
            bot.get_24()
            timer_count = 0
        bot.judge(program_on)
    except errors.LeverageError as e:
        print(e)
        break
    except errors.BalanceError as e:
        print(e)
        break
    except KeyboardInterrupt as e:
        program_on = False
        raise errors.ProgramEndError
    except errors.ProgramEndError as e:
        print(e)
        bot.alarm_bot.program_end_message()
        break
    except Exception as e:
        print(e)
        bot.alarm_bot.unexpected_end_message(e)
        break

        
        


