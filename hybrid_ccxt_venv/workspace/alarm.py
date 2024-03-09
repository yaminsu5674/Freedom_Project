import telegram
import asyncio

global token
global chat_id
token = '5719425685:AAFx1cNXGuDs7RHFV5-QHMeSHli207550Jo'
chat_id = -1001879846305

class alarm_bot:
    def __init__(self):
        self.bot = telegram.Bot(token = token)

    def start_message(self):
        text = 'program start!\n$$$$$$$$$$$$$$$$$\n$$$$$$$$$$$$$$$$$\n$$$$$$$$$$$$$$$$$\n\n'
        self.bot.sendMessage(chat_id=chat_id, text=text)

    def program_end_message(self):
        text = 'On agree of User, Program will close.'
        self.bot.sendMessage(chat_id=chat_id, text=text)

    def unexpected_end_message(self, e):
        e = str(e)
        text = 'By unexpected error, program will close.\n'+e
        self.bot.sendMessage(chat_id=chat_id, text=text)

    def print_surf_status(self, text):
        pass
        #asyncio.run(self.bot.sendMessage(chat_id=chat_id, text=text))


    def day_situation(self, income_24, cycles_24, bad_cycles_24, good_cycles_24):
        text = "#################\n"+"24시간 수익 :"+str(income_24)+"\n"+"bad_cycles/cycles : "+str(bad_cycles_24)+"/"+str(cycles_24)+"\n"+"good_cycles/cycles : "+str(good_cycles_24)+"/"+str(cycles_24)+"\n\n"
        print(text)
        self.bot.sendMessage(chat_id=chat_id, text=text)

    def hour_situation(self, income_1, cycles_1, bad_cycles_1, good_cycles_1):
        text = "1시간 수익 :"+str(income_1)+"\n"+"bad_cycles/cycles : "+str(bad_cycles_1)+"/"+str(cycles_1)+"\n"+"good_cycles/cycles : "+str(good_cycles_1)+"/"+str(cycles_1)+'n'+"#################\n"
        print(text)
        self.bot.sendMessage(chat_id=chat_id, text=text)

    def cycle_situation(self, surf, won):
        text = str(surf)+"step에서 "+str(won)+"원의 수익이 발생했습니다.\n"
        self.bot.sendMessage(chat_id=chat_id, text=text)