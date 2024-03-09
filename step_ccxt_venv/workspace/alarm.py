# 에러 (연결안됨, 제한걸릴때, 손해 발생시, 지지대 위기알림) 시 폰으로 문자 알림.
# 일단은 텔레그램 봇으로 추후에 카톡으로 개선

import telegram

token = '5719425685:AAFx1cNXGuDs7RHFV5-QHMeSHli207550Jo'
chat_id = -1001879846305


class alarm_bot():
    def __init__(self):
        self.bot = telegram.Bot(token=token)

    def enter_step4(self):
        self.bot.sendMessage(chat_id=chat_id, text='스텝4에 진입했습니다.')

    def enter_step5(self):
        self.bot.sendMessage(chat_id=chat_id, text='스텝5에 진입했습니다.')

    def minus_situation(self, minus_won, step, count):
        text = str(minus_won)
        step_text = str(step)
        count_text = str(count)
        text = step_text + '에서 ' + text + '원 손해가 발생했습니다.' + count_text + \
            '번째 손해 \n' + 'ㅠㅠㅠㅠㅠㅠㅠㅠㅠㅠ\nㅠㅠㅠㅠㅠㅠㅠㅠㅠㅠ\nㅠㅠㅠㅠㅠㅠㅠㅠㅠㅠ\n'
        self.bot.sendMessage(chat_id=chat_id, text=text)

    def plus_situation(self, plus_won, step):
        text = str(plus_won)
        step_text = str(step)
        text = step_text + '에서 ' + text + '원 수익이 발생했습니다.'
        self.bot.sendMessage(chat_id=chat_id, text=text)

    def hour_situation(self, won):
        text = str(won)
        text = text + '원을 한 시간 동안 벌었습니다.\n################\n################\n################\n'
        self.bot.sendMessage(chat_id=chat_id, text=text)

    def day_situation(self, won):
        text = str(won)
        text = text + '원을 하루 동안 벌었습니다.\n################\n################\n################\n'
        self.bot.sendMessage(chat_id=chat_id, text=text)

    def cycle_1_situation(self, cycle, step1, step2, step3, step4, step5):
        cycle = str(cycle)
        hwangbo = str(step1)+' '+str(step2)+' '+str(step3) + \
            ' '+str(step4)+' '+str(step5)
        text = cycle + '사이클 동안'+hwangbo+'횡보(step3,4,5) 가 발생했습니다.'
        self.bot.sendMessage(chat_id=chat_id, text=text)

    def cycle_24_situation(self, cycle, step1, step2, step3, step4, step5):
        cycle = str(cycle)
        hwangbo = str(step1)+' '+str(step2)+' '+str(step3) + \
            ' '+str(step4)+' '+str(step5)
        text = cycle + '사이클 동안'+hwangbo+'횡보(step3,4,5) 가 발생했습니다.'
        self.bot.sendMessage(chat_id=chat_id, text=text)

    def start_message(self):
        text = 'program start!\n$$$$$$$$$$$$$$$$$\n$$$$$$$$$$$$$$$$$\n$$$$$$$$$$$$$$$$$\n'
        self.bot.sendMessage(chat_id=chat_id, text=text)

    def minus_error_message(self):
        text = '5번 손해가 발생했습니다. 프로그램을 중단합니다.'
        self.bot.sendMessage(chat_id=chat_id, text=text)

    def program_end_message(self):
        text = '프로그램 사용자 동의 하에 종료합니다.'
        self.bot.sendMessage(chat_id=chat_id, text=text)

    def unexpected_end_message(self, e):
        e = str(e)
        text = '예기치 못한 에러로 인해 종료합니다.\n'+e
        self.bot.sendMessage(chat_id=chat_id, text=text)


class MinuseError(Exception):    # Exception을 상속받아서 새로운 예외를 만듦
    def __init__(self):
        super().__init__('5번 손해가 발생했습니다. 프로그램을 중단합니다.')


class ProgramEndError(Exception):
    def __init__(self):
        super().__init__('프로그램 사용자 동의 하에 종료합니다.')
