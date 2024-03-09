import ccxt
import time
import alarm
import decision
import errors


global program_on
global step
global timer_count
global timer_mini
global timer_0
global timer_1
program_on = True
syscall_counter = 0
step = 0  # 손해 발생시 step -1으로 전환
timer_count = 0
timer_mini = time.time()
timer_0 = time.time()
timer_1 = time.time()


bot = decision.Judger(3, 3, 4, 9, 0.001, 0.0008, 0.0016,"BTCUSDT", 125, 1) # step배율1,step배율2, 지지대1, 지지대2, 최소 시드, 간격1, 간격2, 종목, 주포지션, 레버리지, 넷 선택
bot.alarm_bot.start_message()

while(1):
    try:
        now_time = time.time()
        if now_time - timer_mini > 10:
            syscall_counter = 0
            orders_num = bot.orders_num_show()
            timer_mini = now_time
            if orders_num > 18:
                bot.alarm_bot.orders_over_message(orders_num)

        if now_time-timer_0 >60:
            weight = bot.weight_show()
            if weight >= 1200:
                bot.alarm_bot.ip_limit_over_message()
            timer_0 = now_time
        if now_time-timer_1 >3600:
            timer_count += 1
            bot.check_balance()
            bot.get_1()
            timer_1 = now_time
        if timer_count == 24:
            bot.get_24()
            timer_count = 0
        bot.judge(program_on)
        time.sleep(0.5)
    except errors.LeverageError as e:
        print(e)
        break
    except errors.BalanceError as e:
        print(e)
        break
    except KeyboardInterrupt as e:
        syscall_counter+=1 
        if syscall_counter == 1:   # 모드 전환
            bot.change_mode()
        if syscall_counter ==2:    # 안전하게 종료
            program_on = False
        if syscall_counter == 3:   # 즉시 종료
            bot.alarm_bot.program_end_message()
            raise errors.ProgramEndError
            break
       
    except errors.ProgramEndError as e:
        print(e)
        bot.alarm_bot.program_end_message()
        break
    except errors.UpdateStackError as e:
        print(e)
        bot.alarm_bot.update_stack_error_message()
        break
    except errors.LeverageError as e:
        print(e)
        bot.alarm_bot.unexpected_end_message(e)
        break
    except errors.InsufficientError as e:
        print(e)
        bot.alarm_bot.unexpected_end_message(e)
        break
    except Exception as e:
        print(e)
        bot.alarm_bot.unexpected_end_message(e)
        break

        
        


