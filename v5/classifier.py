import re


class Classifier:
    @staticmethod
    def is_schedule(txt):
        return '/schedule' in txt

    @staticmethod
    def is_to_admin(txt):
        return '/admin' in txt

    @staticmethod
    def is_profile(txt):
        return '/profile' in txt


class Messages:
    __doc__ = """
    HackerOK 2020
    Модуль производит первичную обработку сообщения
    """

    @staticmethod
    def parse(message):
        response = {"is_to_bot": False, "type": False, "data": False}

        message = str(message).strip().lower()

        if message[0] == "/":
            response["is_to_bot"] = True

            # Запрос расписания
            if Classifier.is_schedule(message):
                if "today" in message:
                    response["type"] = "schedule_today"
                elif "tomorrow" in message:
                    response["type"] = "schedule_tomorrow"
                elif "yesterday" in message:
                    response["type"] = "schedule_yesterday"
                else:
                    response["type"] = "schedule"

            elif Classifier.is_to_admin(message):
                response["type"] = "to_admin"

            elif Classifier.is_profile(message):
                if "register" in message:

                    if re.search(r'([А-я]{0,1}[0-9]{0,2}[А-я]{1,2})-([0-9]{2,4}[А-я]{1,2})-([0-9]{2})', message) is not None:
                        response["type"] = "profile_register"
                        response["data"] = {"group": re.search(r'([А-я]{0,1}[0-9]{0,2}[А-я]{1,2})-([0-9]{2,4}[А-я]{1,2})-([0-9]{2})', message).group(0)}

                    elif message == "/profile register":
                        response["type"] = "profile_register_empty"

                    else:
                        response["type"] = "profile_register_wrong"

                elif "delete" in message:
                    response["type"] = "profile_clear"

                elif "notification" in message:
                    if "enable" in message:
                        response["type"] = "profile_notification_enable"
                    elif "disable" in message:
                        response["type"] = "profile_notification_disable"
                    elif "toggle" in message:
                        response["type"] = "profile_notification_toggle"
                    else:
                        response["type"] = "profile_notification_default"
                else:
                    response["type"] = "profile_info"
            elif len(message) == 1:
                response["type"] = "empty_request"
            else:
                response["type"] = "wrong_request"

        return response

    @staticmethod
    def tests():
        data = [
            ["Сообщение", {"is_to_bot": False, "type": False, "data": False}, "Неклассифицируемое событие"],
            ["/", {"is_to_bot": True, "type": "empty_request", "data": False}, "Сообщение для бота с ошибкой 1"],
            ["/random", {"is_to_bot": True, "type": "wrong_request", "data": False}, "Сообщение для бота с неправильной командой"],

            ["/schedule", {"is_to_bot": True, "type": "schedule", "data": False}, "Пустой запрос расписания"],
            ["/schedule today", {"is_to_bot": True, "type": "schedule_today", "data": False}, "Пустой запрос расписания на сегодня"],
            ["/schedule tomorrow", {"is_to_bot": True, "type": "schedule_tomorrow", "data": False}, "Запрос расписания на завтра"],
            ["/schedule yesterday", {"is_to_bot": True, "type": "schedule_yesterday", "data": False}, "Запрос расписания на вчера"],

            ["/admin", {"is_to_bot": True, "type": "to_admin", "data": False}, "Пинг админа"],

            ["/profile", {"is_to_bot": True, "type": "profile_info", "data": False}, "Профиль"],
            ["/profile register", {"is_to_bot": True, "type": "profile_register_empty", "data": False}, "Регистрация пользователя без группы"],
            ["    /profile register   ", {"is_to_bot": True, "type": "profile_register_empty", "data": False}, "Регистрация пользователя без группы с пробелами"],
            ["/profile register м70-200с-20", {"is_to_bot": True, "type": "profile_register_wrong", "data": False}, "Регистрация пользователя с неправильной группой"],
            ["/profile register м7о-209с-19", {"is_to_bot": True, "type": "profile_register", "data": {"group": "м7о-209с-19"}}, "Регистрация с правильной группой"],
            ["/profile register м7О-209С-19", {"is_to_bot": True, "type": "profile_register", "data": {"group": "м7о-209с-19"}}, "Регистрация с правильной группой разным регистром"],

            ["/profile delete", {"is_to_bot": True, "type": "profile_clear", "data": False}, "Удаление пользователя"],

            ["/profile notification", {"is_to_bot": True, "type": "profile_notification_default", "data": False}, "Уведомление по умолчанию"],
            ["/profile notification enable", {"is_to_bot": True, "type": "profile_notification_enable", "data": False}, "Вкл уведомления"],
            ["/profile notification disable", {"is_to_bot": True, "type": "profile_notification_disable", "data": False}, "Выкл уведомления"],
            ["/profile notification toggle", {"is_to_bot": True, "type": "profile_notification_toggle", "data": False}, "Переключить уведомление"],


        ]

        k = 0
        allRight  = True
        for i in data:
            k += 1
            res = Messages.parse(i[0]) == i[1]
            if not res:
                allRight = False
            print("{} : {} -- {} | {}".format(k, res, i[0], i[2]))

        print("--------RESULT--------")
        print(allRight)
        print("--------RESULT--------")



if __name__ == "__main__":
    print(Messages.__doc__)
    Messages.tests()
