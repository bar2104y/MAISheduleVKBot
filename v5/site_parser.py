import requests
import re

from bs4 import BeautifulSoup
import db_controller


def get_lesson_num(txt):
    if txt == '09:00 – 10:30':
        return 1
    if txt == '10:45 – 12:15':
        return 2
    if txt == '13:00 – 14:30':
        return 3
    if txt == '14:45 – 16:15':
        return 4
    if txt == '16:30 – 18:00':
        return 5
    if txt == '18:15 – 19:45':
        return 6
    if txt == '20:00 – 21:30':
        return 7


class SiteParser:

    @staticmethod
    def parse_page(url):
        res = []  # Итоговый результат

        # Защита от падения сайта
        try:
            session = requests.Session()  # Запрос к серверу
            request = session.get(url)  # Ответ сервера

            # Если есть ответ ( страница существует )
            if request.status_code == 200:
                soup = BeautifulSoup(request.content, features="lxml")
                days = soup.find_all('div', "sc-container")

                # Разбираем все дни по отдельности
                for day in days:
                    day_t = day.find('div', 'sc-day-header').text
                    day_t = re.sub(r'[^0-9.]', '', day_t)

                    time_s = day.find_all('div', 'sc-item-time')
                    type_s = day.find_all('div', 'sc-item-type')
                    name_s = day.find_all('span', 'sc-title')
                    teacher_s = day.find_all('span', 'sc-lecturer')
                    room_s = day.find_all('div', 'sc-item-location')

                    day_res = []
                    for i in range(len(time_s)):
                        day_res.append({"time": time_s[i].text.strip(),
                                        "type": type_s[i].text.strip(),
                                        "name": name_s[i].text.strip(),
                                        "teacher": teacher_s[i].text.strip(),
                                        "room": room_s[i].text.strip()
                                        })

                    res.append({"day": day_t, "lessons": day_res})

        except requests.exceptions.MissingSchema:
            pass

        except Exception as e:
            print(e.__str__())
        return res

    @staticmethod
    def save_data_by_group(group):
        group = str(group).upper()

        group_id = db_controller.Controller.get_group_id(group)

        url = "https://mai.ru/education/schedule/detail.php?group="+group
        data = SiteParser.parse_page(url)
        for day in data:
            print(day["day"])
            for lesson in day["lessons"]:
                teacher_id = db_controller.Controller.get_teacher_id(lesson["teacher"])
                subject_id = db_controller.Controller.get_subject_id(lesson["name"])
                room_id = db_controller.Controller.get_room_id(lesson["room"])

                db_controller.Controller.save_lesson(subject_id, day["day"], lesson["type"],
                                                     get_lesson_num(lesson["time"]),
                                                     teacher_id, room_id, group_id)

                print(lesson)


if __name__ == "__main__":
    SiteParser.save_data_by_group("М7О-209С-19")
