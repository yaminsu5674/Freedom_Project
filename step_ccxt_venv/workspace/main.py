import ccxt
import time
import alarm
import control
import decision
import logging


global program_on
global step
global timer_count
global timer_1
program_on = True   # 에러 판단.
step = -1   # 손해를 본다면 status 는 -2 로 변경된다.
timer_count = 0
timer_1 = time.time()
logger = logging.getLogger()

# 트레이딩 봇 객체 생성
bot = decision.Judger(5, 5, 0.01, 0.1)   # c 수정시 control 의 a, c 도 직접 바꿔줘라.
#bot = backup_decision.Judger(5, 5, 0.008)
bot.start_message()
# 레버리지 체크 , 포지션 깔끔하게 비워져있는지 체크!

while (1):
    # except Exception as e:
    # 와이파이 문제 혹은
    # 서버로부터 제한받았을때
    # 포지션 잡힌 당장의 상태를 폰에다가 문자로 출력해 보낸다.
    # l, s 교차할때 도 생각해봐 한번 ㅎㅎ(이게 에러라는 건 아닌데 혹시나 까먹을까봐 적어둔다.)
    # print(e)
    #print('에러 발생으로 종료합니다.')
    #print('minimum_difference : ', minimum_difference)
    # break
    try:
        time.sleep(0.1)
        now_time = time.time()
        if now_time-timer_1 > 3600:
            timer_count += 1
            bot.get_income_1()
            bot.get_cycle_1()
            timer_1 = now_time
        if timer_count == 24:
            bot.get_income_24()
            bot.get_cycle_24()
            timer_count = 0
        step = bot.judge(program_on)
    except alarm.MinuseError as e:
        print(e)
        bot.minus_error_message()
        break
    except KeyboardInterrupt as e:
        program_on = False
    except alarm.ProgramEndError as e:
        print(e)
        bot.program_end_message()
        break
    except Exception as e:
        bot.unexpected_end_message(e)
        logger.exception(str(e))
        break
