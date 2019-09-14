import time, sqlite3, re, requests, random

from bs4 import BeautifulSoup

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

class Log():
    """Ведение логов"""

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

class DetectionRequests():
    def is_help(self,txt):
        return(re.search(r'(помо|help|faq|вопро|начать)',txt) != None)

    def is_schedule_request(self,txt):
        return(re.search(r'(распи|скаж|скин|пар|лекци)',txt) != None)
    
    def reset(self,txt):
        return(re.search(r'(сброс|отмен)',txt) != None)

    def valid_group_number(self,txt):
        return(re.search(r'([А-я]{0,1}[0-9]{1,2}[А-я])-([0-9]{2,4}[А-я]{1,2})-([0-9]{2})',txt) != None)

class DataBase():
    def __init__(self):
        self.conn = sqlite3.connect("MAISchedule2.db")
        self.cursor = self.conn.cursor()


class ScheduleBot(Log, DetectionRequests,DataBase):
    def __init__(self):
        super(ScheduleBot, self).__init__()
        self.not_found_group = 'Такая группа не найдена'
        self.help_text = 'Привет, я глупый бот, так что ничего особенного от меня не жди).\n\nЧтобы начать, напиши полный номер своей группы(М3О-777с-18) Все буквы должны быть написаны кирилицей, в начале буква О, а не цифра 0. Регистр не имеет значения\nБот автоматически запоминает номер группы, поэтому чтобы повторно получить расписание необходимо лишь нажать на соответсвующую кнопку на клавиатуре.\nЕсли вам необходимо сменить/сбросить номер группы или отказаться от уведомлений, нажмите на клавиатуре "Сбросить"\n\nЕсли возникнут какие-то вопросы, напиши "Помощь"'
        self.add_your_group = 'Я не знаю Ваш номер группы, напишите его мне\n\nПример номера группы: м3о-100с-16'
        self.error_group_number = 'Номер группы написан неправильно, пожалуйста, перепроверьте правильность написания номера группы\n\nПример номера группы: м3о-100с-16'
        self.added_notifications = '\n\nНомер группы звписан, теперь Вы будете получать уведомления перед парами, чтобы отказаться от этих уведомлений, нажмите "Сбросить"'
        self.was_reset = 'Ваши данные были стерты, уведомления приходить не будут'

    
    def parse(self, base_url):
        # Мои заголовки запроса
        # headers = {'accept': '*/*',
        # 		'user-agent': 'HackerOK/1.0 (X228; MAIUntu; Linux x86_64; rv:68.0) Gecko/20100101 BRoweser/1337.0'}
        
        res = [] # Итоговый результат

        session = requests.Session() # Запрос к серверу
        request = session.get(base_url) # Ответ сервера

        res.append(request.status_code) # Код ответа
                
        # Если есть ответ ( страница существует )
        # Хотя, как выяснилось, 200 в любом случае, даже если группы нет, уши оторвать тем, чкто не может повесить 404
        # За все время было только 200 или 502
        if request.status_code == 200:
            soup = BeautifulSoup(request.content, features="lxml")
            days = soup.find_all('div', "sc-container")
        
            # Разбираем все дни по отдельности
            for day in days:
                day_t = day.find('div','sc-day-header').text
                day_t = re.sub(r'[^0-9\.]', '', day_t)

                time_s = day.find_all('div', 'sc-item-time')
                type_s = day.find_all('div', 'sc-item-type')
                name_s = day.find_all('span', 'sc-title')
                room_s = day.find_all('div', 'sc-item-location')

                day_res = []
                for i in range(len(time_s)):
                    
                    day_res.append( [time_s[i].text ,
                                            type_s[i].text,
                                            name_s[i].text,
                                            room_s[i].text] )
                    
                res.append([day_t, day_res])
        #Затычку else:
        
        return(res)

    def save_data(self, group_id):

        res = self.parse('https://mai.ru/education/schedule/detail.php?group='+group_id.upper())
                
        if res[0] == 200:
            # Пребор дней
            for i in range(1,len(res)):
                # Находим этот день в базе данных
                self.cursor.execute("SELECT * FROM data WHERE group_id=? and day_i=?", (group_id, res[i][0]))

                # Если не найдено - добавляем
                if len(self.cursor.fetchall()) == 0:
                    for j in range(len(res[i][1])):
                        self.cursor.execute("INSERT INTO data VALUES (?,?,?,?,?,?)",
                                    (group_id, res[i][0],
                                    res[i][1][j][0], res[i][1][j][1],
                                    res[i][1][j][2], res[i][1][j][3]))
                # Иначе - обновляем
                else:
                    for j in range(len(res[i][1])):
                        self.cursor.execute("UPDATE data SET type=?,name =?,room=? WHERE group_id=? and day_i=? and time=?",
                                    ( res[i][1][j][1], res[i][1][j][2],
                                    res[i][1][j][3], group_id,
                                    res[i][0], res[i][1][j][0]))
                # Применяем изменения
                self.conn.commit()

            return(True)
        else:
            return(False)

    def get_group_pars_day(self, group_id, today=time.strftime("%d.%m", time.localtime())):
        # Выделяем всю информацию по группе в определенный день
        self.cursor.execute("SELECT * FROM data WHERE group_id=? and day_i=?", (group_id, today))
        tmp = self.cursor.fetchall()

        return(tmp)
    
    def generate_text_schedule_at_days(self,group,days=2):
        hello = ['Вот расписание на {}\n',
                'Это расписание на {}\n',
                'Держи расписание на {}\n',
                'Это тебя ждет в ближайшие {}\n']
        if days == 1:
            mes = random.choice(hello).format('один день')
        elif days > 1 and days < 5:
            mes = random.choice(hello).format(str(days)+' дня')
        else:
            mes = random.choice(hello).format(str(days)+' дней')
        
        k = 0
        j = 0
        day = 0
        while day < days and k < 30:
            today = time.strftime("%d.%m", time.localtime(time.time()+24*3600*j))
            print(today)
            schedule = self.get_group_pars_day(group,today)
            
            k += 1
            j += 1
            
            if len(schedule) < 1:
                continue
            else:
                day += 1
            
            mes += '---------------------\n'
            mes += 'На ' + schedule[0][1] + ':\n'
            mes += 'Группа: ' + schedule[0][0] + '\n'
            for i in range(len(schedule)):
                mes += 'Время: ' + schedule[i][2] +'\n'
                mes += 'Тип: ' + schedule[i][3] +'\n'
                mes += 'Что: ' + schedule[i][4] +'\n'
                mes += 'Где: ' + schedule[i][5] +'\n\n'
        
        return(mes)
            
    def generate_text_lesson(self,group,lesson,day = time.strftime("%d.%m", time.localtime())):
        if lesson == 1:
            l_time = '09:00 – 10:30'
        elif lesson == 2:
            l_time = '10:45 – 12:15'
        elif lesson == 3:
            l_time = '13:00 – 14:30'
        elif lesson == 4:
            l_time = '14:45 – 16:15'
        elif lesson == 5:
            l_time = '16:30 – 18:00'
        else:
            return(False)
        
        self.cursor.execute("SELECT * FROM data WHERE group_id=? and day_i=? and time=?", (group, day, l_time))
        lesson_data = self.cursor.fetchall()
        
        if len(lesson_data) == 1:
            lesson_data = lesson_data[0]
            mes = 'Сегодня наверное ' + lesson_data[1]+ '\nГруппа: ' + lesson_data[0]+ '\n\nСледущая пара ' + lesson_data[2]+ '\n' + lesson_data[4]+'\n' + lesson_data[3]+'\n' + lesson_data[5] + '\n'
        else:
            return(False)
        
        print(mes)
    
    def get_users_group(self, user_id):
        self.cursor.execute("SELECT `group_number` FROM users WHERE user_id=?", (user_id, ))
        groups = self.cursor.fetchall()
        return(groups)

    def thread(self,text,user_id):
        mes = ''
        txt = text.lower()
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('Помощь', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()

        # Запрос на помощь
        if self.is_help(txt):
            mes = self.help_text
            self.cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
            user_db = self.cursor.fetchall()
            if len(user_db) > 0:
                keyboard.add_button('Расписание', color=VkKeyboardColor.PRIMARY)
                keyboard.add_line()
                
        elif self.reset(txt):
            self.cursor.execute("DELETE FROM users WHERE user_id=?", (user_id,))
            self.conn.commit()

            mes = self.was_reset

        # ЗАпрос на расписание
        elif self.is_schedule_request(txt):
             
            groups = self.get_users_group(user_id)
            if not groups:
                mes = self.add_your_group
            else:
                for group in groups:
                    self.save_data(group[0])
                    mes += self.generate_text_schedule_at_days(group[0])

                keyboard.add_button('Расписание', color=VkKeyboardColor.PRIMARY)
                keyboard.add_line()

        elif self.valid_group_number(txt):
            txt = txt.upper()
            mes = self.generate_text_schedule_at_days(txt)

            self.cursor.execute("SELECT * FROM users WHERE user_id=?", ( user_id , ))
            if len(self.cursor.fetchall()) < 1:
                self.cursor.execute("INSERT INTO users  VALUES (NULL,?,?)", (user_id, txt))
            self.conn.commit()

            mes += self.added_notifications  
            keyboard.add_button('Расписание', color=VkKeyboardColor.PRIMARY)
            keyboard.add_line()           
        else:
            mes = self.error_group_number

        keyboard.add_button('Сбросить', color=VkKeyboardColor.NEGATIVE)

        return(mes, keyboard.get_keyboard())