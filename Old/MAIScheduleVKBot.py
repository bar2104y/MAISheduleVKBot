import time, sqlite3, re, requests

from bs4 import BeautifulSoup

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from config import token, group_vk  

class MAIScheduleVKBot():
    def __init__(self):
        self.not_found_group = 'Такая группа не найдена'
        self.help_text = 'Привет, я глупый бот, так что ничего особенного от меня не жди).\n\nЧтобы начать, напиши полный номер своей группы(М3О-777с-18) Все буквы должны быть написаны кирилицей, в начале буква О, а не цифра 0. Регистр не имеет значения\nБот автоматически запоминает номер группы, поэтому чтобы повторно получить расписание необходимо лишь нажать на соответсвующую кнопку на клавиатуре.\nЕсли вам необходимо сменить/сбросить номер группы или отказаться от уведомлений, нажмите на клавиатуре "Сбросить"\n\nЕсли возникнут какие-то вопросы, напиши "Помощь"'
        self.add_your_group = 'Я не знаю Ваш номер группы, напишите его мне\n\nПример номера группы: м3о-100с-16'
        self.error_group_number = 'Номер группы написан неправильно, пожалуйста, перепроверьте правильность написания номера группы\n\nПример номера группы: м3о-100с-16'
        self.added_notifications = '\n\nНомер группы звписан, теперь Вы будете получать уведомления перед парами, чтобы отказаться от этих уведомлений, нажмите "Сбросить"'
        self.was_reset = 'Ваши данные были стерты, уведомления приходить не будут'

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
    
    # Функции определения типа запроса
    def is_help(self,txt):
        return(re.search(r'(помо|help|faq|вопро|начать)',txt) != None)

    def is_schedule_request(self,txt):
        return(re.search(r'(распи|скаж|скин|пар|лекци)',txt) != None)
    
    def reset(self,txt):
        return(re.search(r'(сброс|отмен)',txt) != None)

    def valid_group_number(self,txt):
        return(re.search(r'([А-я]{0,1}[0-9]{1,2}[А-я])-([0-9]{2,4}[А-я]{1,2})-([0-9]{2})',txt) != None)


    def parse(self, base_url):
        # Мои заголовки запроса
        # headers = {'accept': '*/*',
        # 		'user-agent': 'HackerOK/1.0 (X228; MAIUntu; Linux x86_64; rv:68.0) Gecko/20100101 BRoweser/1337.0'}
        
        res = [] # Итоговый результат

        session = requests.Session() # Запрос к серверу
        request = session.get(base_url) # Ответ сервера

        res.append(request.status_code) # Код ответа
        
        logmes = '[{}] Response to [{}] with code: {}\n'.format(time.strftime("%d/%m-%H:%M:%S", time.localtime()),base_url,request.status_code)
        try:
            f = open('BotLog.log', 'a')
            f.write(logmes)
            f.close()
        except Exception as e:
            print(e.__class__)
        
        # Если есть ответ ( страница существует )
        if request.status_code == 200:
            soup = BeautifulSoup(request.content, features="lxml")
            days = soup.find_all('div', "sc-container")
        
            
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
        
        return(res)

    def get_schedule(self, group):
        group = group.upper()
        info = self.parse('https://mai.ru/education/schedule/detail.php?group='+group)
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
    
    def save_data(self, group_id, today=time.strftime("%d.%m", time.localtime())):
        res = self.parse('https://mai.ru/education/schedule/detail.php?group='+group_id)
        
        conn = sqlite3.connect("MAIShedule.db")
        cursor = conn.cursor()
        
        if res[0] == 200:
            # Пребор дней
            for i in range(1,len(res)):

                cursor.execute("SELECT * FROM groupsShedule WHERE group_id=? and day_i=?", (group_id, res[i][0]))

                
                if len(cursor.fetchall()) == 0:
                    for j in range(len(res[i][1])):
                        cursor.execute("INSERT INTO groupsShedule VALUES (?,?,?,?,?,?)",
                                    (group_id, res[i][0],
                                    res[i][1][j][0], res[i][1][j][1],
                                    res[i][1][j][2], res[i][1][j][3]))
                else:
                    for j in range(len(res[i][1])):
                        cursor.execute("UPDATE groupsShedule SET type=?,name =?,room=? WHERE group_id=? and day_i=? and time=?",
                                    ( res[i][1][j][1], res[i][1][j][2],
                                    res[i][1][j][3], group_id,
                                    res[i][0], res[i][1][j][0]))

                conn.commit()

                try:
                    logmes = '[{}] Cached group: {} date: {} \n'.format(time.strftime("%d/%m-%H:%M:%S", time.localtime()),group_id, res[i][0])
                
                    f = open('BotLog.log', 'a')
                    f.write(logmes)
                    f.close()

                except Exception as e:
                    print(e.__class__)
            return(True)
        else:
            return(False)
        
    def get_group_pars_today(self, group_id, today=time.strftime("%d.%m", time.localtime())):
        conn = sqlite3.connect("MAIShedule.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM groupsShedule WHERE group_id=? and day_i=?", (group_id, today))
        tmp = cursor.fetchall()

        return(tmp)


class sendPars(MAIScheduleVKBot):
    def __init__(self):
        self.vk_session = vk_api.VkApi(token=token)
        self.vk = self.vk_session.get_api()
        self.users = []
        self.conn = sqlite3.connect("MAIShedule.db")
        self.cursor = self.conn.cursor()
    
    def get_users(self):
        self.cursor.execute("SELECT * FROM usersgroup WHERE 1")
        tmp = self.cursor.fetchall()
        t_users = []

        for tm in tmp:
            if tm[0] not in t_users:
                t_users.append(tm[0])
        return(t_users)
    
    def get_groups(self):
        self.cursor.execute("SELECT * FROM usersgroup WHERE 1")
        tmp = self.cursor.fetchall()
        t_groups = []

        for tm in tmp:
            if tm[0] not in t_groups:
                t_groups.append(tm[1])
        return(t_groups)
    