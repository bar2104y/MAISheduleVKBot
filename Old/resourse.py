import time,re, sqlite3
from parse import parse

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

class Log():
    # Сохранение в файл
    def saveToFile(self, e):
        filename = time.strftime("%d-%m.log", time.localtime())
        f = open(filename, 'a')
        f.write("[{}] {}\n".format(time.strftime("%d/%m-%H:%M:%S", time.localtime()), e))
        f.close()
    
    # Логгирование ошибок
    def logError(self,e):
        try:
            self.saveToFile( str(e.__class__) + str(e) )            
        except Exception as err:
            print(str(err))

    # Логгирование входящего сообщения
    def logInputMessage(self, vk_id, text):
        try:
            self.saveToFile( "message from: {} text: {}".format(vk_id,text) )
        except Exception as err:
            print(str(err))

class Classificator(Log):
    def __init__(self):
        self.not_found_group = 'Такая группа не найдена'
        self.help_text = 'Привет, я глупый бот, так что ничего особенного от меня не жди).\n\nЧтобы начать, напиши полный номер своей группы(М3О-777с-18) Все буквы должны быть написаны кирилицей, в начале буква О, а не цифра 0. Регистр не имеет значения\nБот автоматически запоминает номер группы, поэтому чтобы повторно получить расписание необходимо лишь нажать на соответсвующую кнопку на клавиатуре.\nЕсли вам необходимо сменить/сбросить номер группы или отказаться от уведомлений, нажмите на клавиатуре "Сбросить"\n\nЕсли возникнут какие-то вопросы, напиши "Помощь"'
        self.add_your_group = 'Я не знаю Ваш номер группы, напишите его мне\n\nПример номера группы: м3о-100с-16'
        self.error_group_number = 'Номер группы написан неправильно, пожалуйста, перепроверьте правильность написания номера группы\n\nПример номера группы: м3о-100с-16'
        self.added_notifications = '\n\nНомер группы звписан, теперь Вы будете получать уведомления перед парами, чтобы отказаться от этих уведомлений, нажмите "Сбросить"'
        self.was_reset = 'Ваши данные были стерты, уведомления приходить не будут'

    # Функции определения типа запроса
    def is_help(self,txt):
        return(re.search(r'(помо|help|faq|вопро|начать)',txt) != None)

    def is_schedule_request(self,txt):
        return(re.search(r'(распи|скаж|скин|пар|лекци)',txt) != None)
    
    def reset(self,txt):
        return(re.search(r'(сброс|отмен)',txt) != None)

    def valid_group_number(self,txt):
        return(re.search(r'([А-я]{0,1}[0-9]{1,2}[А-я])-([0-9]{2,4}[А-я]{1,2})-([0-9]{2})',txt) != None)
    

    def get_schedule(self, group):
        group = group.upper()
        info = parse('https://mai.ru/education/schedule/detail.php?group='+group)
        if len(info) >= 3:
            mes = 'Держи расписание на ближайшие два дня\n\n'
            for i in range(1, 3):
                mes += info[i][0]+'\n'
                for para in info[i][1]:
                    mes += 'Время: '+para[0]+'\n'
                    mes += 'Тип: '+para[1]+'\n'
                    mes += 'Что: '+para[2]+'\n'
                    mes += 'Где: '+para[3]+'\n\n'
        else:
            mes = self.error_group_number

        return(mes)



    def thread(self, txt, user_id):
        txt = txt.lower()
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('Помощь', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()

        conn = sqlite3.connect("MAIShedule.db")
        cursor = conn.cursor()

        # Запрос на помощь
        if self.is_help(txt):
            mes = self.help_text
            cursor.execute("SELECT * FROM usersgroup WHERE user_id=?", (user_id,))
            user_db = cursor.fetchall()
            if len(user_db) > 0:
                keyboard.add_button('Расписание', color=VkKeyboardColor.PRIMARY)
                keyboard.add_line()
                
        elif self.reset(txt):
            cursor.execute("DELETE FROM usersgroup WHERE user_id=?", (user_id,))
            conn.commit()

            mes = self.was_reset

        # ЗАпрос на расписание
        elif self.is_schedule_request(txt):
            
            cursor.execute("SELECT * FROM usersgroup WHERE user_id=?", (user_id,))
            user_db = cursor.fetchall()
            if len(user_db) <= 0:
                mes = self.add_your_group
            else:
                mes = self.get_schedule(user_db[0][1])

                keyboard.add_button('Расписание', color=VkKeyboardColor.PRIMARY)
                keyboard.add_line()
        elif self.valid_group_number(txt):
            txt = txt.upper()
            mes = self.get_schedule(txt)

            cursor.execute("SELECT * FROM usersgroup WHERE user_id=?", ( user_id , ))
            if len(cursor.fetchall()) == 0:
                cursor.execute("INSERT INTO usersgroup  VALUES (?,?)", (user_id, txt))
            conn.commit()

            mes += self.added_notifications  
            keyboard.add_button('Расписание', color=VkKeyboardColor.PRIMARY)
            keyboard.add_line()           
        else:
            mes = self.error_group_number

        keyboard.add_button('Сбросить', color=VkKeyboardColor.NEGATIVE)

        return(mes, keyboard.get_keyboard())