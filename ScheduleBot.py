import random
import re
import requests
import sqlite3
import time

from bs4 import BeautifulSoup
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


class Log:
    """Ведение логов"""

    def saveToFile(self, e):
        filename = str(time.strftime("%d-%m.log", time.localtime()))
        f = open(filename, 'a')
        f.write("[{}] {}\n".format(time.strftime("%d/%m-%H:%M:%S", time.localtime()), e))
        f.close()

    # Логгирование ошибок
    def logError(self, e):
        try:
            self.saveToFile(str(e.__class__) + ' | ' + str(e))
        except Exception as err:
            print(str(err))

    # Логгирование входящего сообщения
    def logInputMessage(self, vk_id, text):
        try:
            self.saveToFile("message from: {} text: {}".format(vk_id, text))
        except Exception as err:
            print(str(err))


class DetectionRequests:
    def is_help(self, txt):
        return re.search(r'(помо|help|faq|вопро|начать)', txt) is not None

    def is_schedule_request(self, txt):
        return re.search(r'(распи|скаж|скин|пар|лекци)', txt) is not None

    def reset(self, txt):
        return re.search(r'(сброс|отмен)', txt) is not None

    def is_session(self, txt):
        return re.search(r'(сесси|экзам)', txt) is not None

    def valid_group_number(self, txt):
        return re.search(r'([А-я]{0,1}[0-9]{0,2}[А-я]{1,2})-([0-9]{2,4}[А-я]{1,2})-([0-9]{2})', txt) is not None

    def get_count_days(self, txt):
        d = 2
        try:
            d = re.search(r'(распи|скаж|скин|пар|лекци)(.*?)([0-9]{1,3})', txt).group(3)
        finally:
            return d


class DataBase:
    def __init__(self):
        self.conn = sqlite3.connect("MAISchedule2.db")
        self.cursor = self.conn.cursor()

    def get_groups(self):
        self.cursor.execute("SELECT DISTINCT group_number FROM users")
        return self.cursor.fetchall()

    def get_users_by_group(self, group):
        self.cursor.execute("SELECT user_id FROM users WHERE group_number = ?", (group,))
        return self.cursor.fetchall()


class ScheduleBot(Log, DetectionRequests, DataBase):
    def __init__(self):
        try:
            super(ScheduleBot, self).__init__()
        except Exception as e:
            self.logError(e)

        self.not_found_group = 'Такая группа не найдена'
        self.help_text = 'Привет, я глупый бот, так что ничего особенного от меня не жди).\n\nЧтобы начать, напиши полный номер своей группы(М3О-777с-18) Все буквы должны быть написаны кирилицей, в начале буква О, а не цифра 0. Регистр не имеет значения\nБот автоматически запоминает номер группы, поэтому чтобы повторно получить расписание необходимо лишь нажать на соответсвующую кнопку на клавиатуре.\nЕсли вам необходимо сменить/сбросить номер группы или отказаться от уведомлений, нажмите на клавиатуре "Сбросить"\n\nЕсли возникнут какие-то вопросы, напиши "Помощь"'
        self.add_your_group = 'Я не знаю Ваш номер группы, напишите его мне\n\nПример номера группы: м3о-100с-16'
        self.error_group_number = 'Номер группы написан неправильно, пожалуйста, перепроверьте правильность написания номера группы\n\nПример номера группы: м3о-100с-16'
        self.added_notifications = '\n\nНомер группы записан, теперь Вы будете получать уведомления перед парами, чтобы отказаться от этих уведомлений, нажмите "Сбросить"'
        self.was_reset = 'Ваши данные были стерты, уведомления приходить не будут'

    def parse(self, base_url):

        res = []  # Итоговый результат
        # Защита от падения сайта
        try:
            session = requests.Session()  # Запрос к серверу
            request = session.get(base_url)  # Ответ сервера

            res.append(request.status_code)  # Код ответа
        except Exception as e:
            request.status_code = 404

        # Если есть ответ ( страница существует )
        # Хотя, как выяснилось, 200 в любом случае, даже если группы нет, уши оторвать тем, кто не может повесить 404
        # За все время было только 200 или 502
        if request.status_code == 200:
            soup = BeautifulSoup(request.content, features="lxml")
            days = soup.find_all('div', "sc-container")

            # Разбираем все дни по отдельности
            for day in days:
                day_t = day.find('div', 'sc-day-header').text
                day_t = re.sub(r'[^0-9\.]', '', day_t)

                time_s = day.find_all('div', 'sc-item-time')
                type_s = day.find_all('div', 'sc-item-type')
                name_s = day.find_all('span', 'sc-title')
                room_s = day.find_all('div', 'sc-item-location')

                day_res = []
                for i in range(len(time_s)):
                    day_res.append([time_s[i].text,
                                    type_s[i].text,
                                    name_s[i].text,
                                    room_s[i].text])

                res.append([day_t, day_res])
        # Затычку else:
        return res

    def save_data(self, group_id, is_session=False):

        if is_session:
            res = self.parse('https://mai.ru/education/schedule/session.php?group=' + group_id.upper())
        else:
            res = self.parse('https://mai.ru/education/schedule/detail.php?group=' + group_id.upper())

        if res[0] == 200:
            # Пребор дней
            for i in range(1, len(res)):
                # Находим этот день в базе данных
                if is_session:
                    self.cursor.execute("DELETE FROM sessions WHERE group_id=? and day_i=?", (group_id, res[i][0]))
                else:
                    self.cursor.execute("DELETE FROM data WHERE group_id=? and day_i=?", (group_id, res[i][0]))
                # self.cursor.execute("SELECT * FROM data WHERE group_id=? and day_i=?", (group_id, res[i][0]))

                # Если не найдено - добавляем
                if True:
                    # if len(self.cursor.fetchall()) == 0:
                    for j in range(len(res[i][1])):
                        try:
                            if is_session:
                                self.cursor.execute("INSERT INTO sessions VALUES (?,?,?,?,?,?)",
                                                    (group_id, res[i][0].strip(),
                                                     res[i][1][j][0].strip(), res[i][1][j][1].strip(),
                                                     res[i][1][j][2].strip(), res[i][1][j][3].strip()))
                            else:
                                self.cursor.execute("INSERT INTO data VALUES (?,?,?,?,?,?)",
                                                    (group_id, res[i][0].strip(),
                                                     res[i][1][j][0].strip(), res[i][1][j][1].strip(),
                                                     res[i][1][j][2].strip(), res[i][1][j][3].strip()))
                        except Exception as e:
                            self.logError(e)

                self.conn.commit()

            return True
        else:
            return False

    def get_group_pars_day(self, group_id, today=time.strftime("%d.%m", time.localtime())):
        # Выделяем всю информацию по группе в определенный день
        try:
            self.cursor.execute("SELECT * FROM data WHERE group_id=? and day_i=?", (group_id, today))
            tmp = self.cursor.fetchall()

            return tmp
        except Exception as e:
            self.logError(e)

    def get_group_session(self, group_id):
        # Выделяем всю информацию по группе в определенный день
        try:
            self.cursor.execute("SELECT * FROM sessions WHERE group_id=?", (group_id,))
            tmp = self.cursor.fetchall()

            return tmp
        except Exception as e:
            self.logError(e)

    def generate_text_schedule_at_days(self, group, days=2):
        hello = ['Вот расписание на {}\n',
                 'Это расписание на {}\n',
                 'Держи расписание на {}\n',
                 'Это тебя ждет в ближайшие {}\n']
        if days == 1:
            mes = random.choice(hello).format('один день')
        elif 1 < days < 5:
            mes = random.choice(hello).format(str(days) + ' дня')
        else:
            mes = random.choice(hello).format(str(days) + ' дней')

        k = 0
        j = 0
        day = 0
        while day < days and k < 30:
            today = time.strftime("%d.%m", time.localtime(time.time() + 24 * 3600 * j))
            schedule = self.get_group_pars_day(group, today)

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
                mes += 'Время:  {}\nТип:    {}\nЧто:    {}\nГде:    {}\n\n'.format(schedule[i][2], schedule[i][3], schedule[i][4], schedule[i][5])

        return mes

    def generate_text_session(self, group, days=2):
        hello = ['Сессия приближается {}\n']
        mes = random.choice(hello)

        schedule = self.get_group_session(group)

        mes += '---\n'

        mes += 'Группа: ' + schedule[0][0] + '\n'
        for i in range(len(schedule)):
            mes += schedule[i][1] + ':\n'
            mes += 'Время: ' + schedule[i][2] + '\n'
            mes += 'Тип: ' + schedule[i][3] + '\n'
            mes += 'Что: ' + schedule[i][4] + '\n'
            mes += 'Где: ' + schedule[i][5] + '\n\n'

        return mes

    def generate_text_lesson(self, group, lesson, day=time.strftime("%d.%m", time.localtime())):
        lesson = int(lesson)
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
        elif lesson == 6:
            l_time = '18:15 – 19:45'
        else:
            return False

        try:
            self.cursor.execute("SELECT * FROM data WHERE group_id=? and day_i=? and time=?", (group, day, l_time,))
            lesson_data = self.cursor.fetchall()
        except Exception as e:
            self.logError(e)

        if len(lesson_data) == 1:
            lesson_data = lesson_data[0]
            mes = 'Следущая пара ' + lesson_data[2] + '\n' + lesson_data[5] + '\n' + lesson_data[4] + '\n' + \
                  lesson_data[3] + '\n' + '\n' + 'Сегодня наверное ' + lesson_data[1] + '\nГруппа: ' + lesson_data[0]
            return mes
        else:
            return False

    def get_users_group(self, user_id):
        try:
            self.cursor.execute("SELECT `group_number` FROM users WHERE user_id=?", (user_id,))
            groups = self.cursor.fetchall()
        except Exception as e:
            self.logError(e)
        return groups

    def thread(self, text, user_id):
        mes = ''
        txt = text.lower()
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('❔Помощь❔', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()

        # Запрос на помощь
        if self.is_help(txt):
            mes = self.help_text
            # self.cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
            # user_db = self.cursor.fetchall()
            # if len(user_db) > 0:
            #     keyboard.add_button('🍺Расписание🍺', color=VkKeyboardColor.PRIMARY)
            #     keyboard.add_line()
            #     keyboard.add_button('😈Сессия😈', color=VkKeyboardColor.PRIMARY)
            #     keyboard.add_line()
        elif self.reset(txt):
            try:
                self.cursor.execute("DELETE FROM users WHERE user_id=?", (user_id,))
                self.conn.commit()
            except Exception as e:
                self.logError(e)

            mes = self.was_reset

        # ЗАпрос на расписание
        elif self.is_schedule_request(txt):
            d = int(self.get_count_days(txt))

            groups = self.get_users_group(user_id)
            if not groups:
                mes = self.add_your_group
            else:
                for group in groups:
                    try:
                        self.save_data(group[0])
                        mes += self.generate_text_schedule_at_days(group[0], d)
                    except Exception as e:
                        self.logError(e)

        elif self.is_session(txt):
            groups = self.get_users_group(user_id)
            if not groups:
                mes = self.add_your_group
            else:
                for group in groups:
                    try:
                        self.save_data(group[0], True)
                        mes += self.generate_text_session(group[0])
                    except Exception as e:
                        self.logError(e)
        elif self.valid_group_number(txt):
            txt = txt.upper()
            self.save_data(txt)
            mes = self.generate_text_schedule_at_days(txt)

            try:
                self.cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
                if len(self.cursor.fetchall()) < 1:
                    self.cursor.execute("INSERT INTO users  VALUES (NULL,?,?)", (user_id, txt))
                self.conn.commit()
            except Exception as e:
                self.logError(e)

            mes += self.added_notifications
        else:
            mes = self.error_group_number

        keyboard.add_button('🍺Расписание🍺', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('😈Сессия😈', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('😡Сбросить😡', color=VkKeyboardColor.NEGATIVE)

        return mes, keyboard.get_keyboard()
