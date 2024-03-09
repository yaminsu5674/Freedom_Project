import telegram

global token
global chat_id
global rate
token = '5719425685:AAFx1cNXGuDs7RHFV5-QHMeSHli207550Jo'  #  for cycle log
chat_id = -1001879846305                                  #  for cycle log
system_token = '6050965360:AAGOn8b7wz7xSLXbENK6V8L4fpbQWOYej8U'              # for system log
system_chat_id = 5792856686
rate = 1300

class alarm_bot:
    def __init__(self):
        self.bot = telegram.Bot(token = token)
        self.system_bot = telegram.Bot(token = system_token)

    def start_message(self):
        text = 'program start!\n$$$$$$$$$$$$$$$$$\n$$$$$$$$$$$$$$$$$\n$$$$$$$$$$$$$$$$$\n\n'
        self.bot.sendMessage(chat_id=chat_id, text=text)
        self.system_bot.sendMessage(chat_id=system_chat_id, text=text)

    def program_end_message(self):
        text = 'On agree of User, Program will close.'
        self.bot.sendMessage(chat_id=chat_id, text=text)
        self.system_bot.sendMessage(chat_id=system_chat_id, text=text)

    def unexpected_end_message(self, e):
        e = str(e)
        text = 'By unexpected error, program will close.\n'+e
        self.bot.sendMessage(chat_id=chat_id, text=text)
        self.system_bot.sendMessage(chat_id=system_chat_id, text=text)

    def update_stack_error_message(self):
        text = 'UpdateStack Refetching Error, immediately enter with root for cleaning position yourself!'
        self.bot.sendMessage(chat_id=chat_id, text=text)
        self.system_bot.sendMessage(chat_id=system_chat_id, text=text)

    def ip_limit_over_message(self):
        text = 'IP- limit is dangerous. Update limit calculating!\n************************************\n************************************\n************************************\n************************************\n************************************\n************************************\n'
        self.bot.sendMessage(chat_id=chat_id, text=text)
        self.system_bot.sendMessage(chat_id=system_chat_id, text=text)

    def orders_over_message(self, num):
        text = '10초당 주문 수 과다 위험 ! 주문수 : '+str(num)+'\n************************************\n************************************\n************************************\n************************************\n************************************\n************************************\n'
        print(text)
        self.bot.sendMessage(chat_id=chat_id, text=text)
        self.system_bot.sendMessage(chat_id=system_chat_id, text=text)

        


    def day_situation(self, income_24, cycles_24, bad_cycles_24, good_cycles_24):
        text = "#################\n"+"24시간 수익 :"+str(income_24)+"원"+"\n"+"bad_cycles/cycles : "+str(bad_cycles_24)+"/"+str(cycles_24)+"\n"+"good_cycles/cycles : "+str(good_cycles_24)+"/"+str(cycles_24)+"\n\n"
        print(text)
        self.bot.sendMessage(chat_id=chat_id, text=text)

    def hour_situation(self, income_1, cycles_1, bad_cycles_1, good_cycles_1,balance):
        text = "1시간 수익 :"+str(income_1)+"원"+"\n"+"bad_cycles/cycles : "+str(bad_cycles_1)+"/"+str(cycles_1)+"\n"+"good_cycles/cycles : "+str(good_cycles_1)+"/"+str(cycles_1)+'\n'+"#################\n"+str(round(balance*rate,2))+'원 계좌'
        print(text)
        self.bot.sendMessage(chat_id=chat_id, text=text)

    def cycle_situation(self, position, step, other, won):
        if position == 0:
            text = "Long의 "+str(step)+"step에서 "+str(won)+"원의 수익이 발생했습니다.\nShort는 "+str(other)+"step.\n"
        else:
            text = "Short의 "+str(step)+"step에서 "+str(won)+"원의 수익이 발생했습니다.\nLong은 "+str(other)+"step.\n"
        self.bot.sendMessage(chat_id=chat_id, text=text)

    def minus_message(self, won):
        text = str(won)+"원 손해가 발생했습니다."
        self.system_bot.sendMessage(chat_id=system_chat_id, text=text)


