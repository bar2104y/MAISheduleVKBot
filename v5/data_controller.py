import db_controller as db
import texts

from vk_api.keyboard import VkKeyboard, VkKeyboardColor


class Schedule:
    @staticmethod
    def response(a, vk_id):

        def get_lesson_time_by_num(num):
            l_time = ["09:00-10:30", "10:00-12:15",
                      "13:00-14:30", "14:45-16:15", "16:30-18:00",
                      "18:15-19:45", "20:00-21:30"]
            return l_time[num - 1]

        def make_text(lessons):
            res = 'Расписание группы <{}>:\n'.format(lessons[0].group.group)
            day_str = None
            for lesson in lessons:
                if day_str != lesson.day:
                    res += '---------------------------\nНа {}:\n'.format(lesson.day)
                    day_str = lesson.day
                try:
                    teacher = '{} {} {}'.format(lesson.teacher.surname, lesson.teacher.first_name,
                                                lesson.teacher.second_name)
                except:
                    teacher = ''
                res += "Время {}:\n{}\n{}\n{}\n{}\n\n".format(get_lesson_time_by_num(lesson.number),
                                                              lesson.subject.name.capitalize(), lesson.type,
                                                              lesson.room.name, teacher)
            return res

        type = a["type"]
        data = a["data"]

        mes = texts.unknown_error()
        keyboard = None

        user = db.Controller.get_user_by_vk_id(vk_id)
        if user.count() < 1:
            mes = texts.user_is_not_regisered()
            return mes, keyboard
        else:
            user = user[0]
            if type == "schedule_today":
                num_days = 1
                day_offset = 0
            elif type == "schedule_tomorrow":
                num_days = 1
                day_offset = 1
            elif type == "schedule_yesterday":
                num_days = 1
                day_offset = -1
            else:
                num_days = 2
                day_offset = 0

            schedule = db.Controller.get_schedule_n_day(user.group, num_days, day_offset)

            if schedule.count() < 1:
                while num_days <= 7 and schedule.count() < 1:
                    schedule = db.Controller.get_schedule_n_day(user.group)
                    num_days += 1
                if schedule.count() < 1:
                    mes = texts.empty_schedule().format(user.group.group)
                else:
                    mes = make_text(schedule)
            else:
                mes = make_text(schedule)

        return mes, keyboard

        # if type == "schedule_today":


class Profile:
    @staticmethod
    def response(a, vk_id):
        type = a["type"]
        data = a["data"]

        mes = texts.unknown_error()
        keyboard = VkKeyboard()

        user = db.Controller.get_user_by_vk_id(vk_id)
        if user.count() < 1:
            mes = texts.user_is_not_regisered()
            keyboard.add_callback_button('Зарегистрироваться', color=VkKeyboardColor.PRIMARY, payload='{"command": "/profile register"}')
            return mes, keyboard

        if type == "profile_register_empty":
            mes = texts.empty_regiter_query()

        elif type == "profile_register_wrong":
            mes = texts.wrong_register_query()
        elif type == "profile_register":
            group = data["group"].upper()
            db.Controller.register_user(group, vk_id)
            mes = str(texts.profile_register_query()).format(group)
        elif type == "profile_clear":
            db.Controller.delete_user(vk_id)
            mes = texts.profile_delete_user()

        elif "notification" in type:
            keyboard.add_callback_button('Переключить уведомления', color=VkKeyboardColor.PRIMARY, payload='{"command": "/profile notification"}')
            if type == "profile_notification_enable":
                res = db.Controller.toggle_notification(vk_id, 1)
                mes = texts.profile_notification(res)
            elif type == "profile_notification_disable":
                res = db.Controller.toggle_notification(vk_id, 0)
                mes = texts.profile_notification(res)
            elif type == "profile_notification_toggle" or type == "profile_notification_default":
                res = db.Controller.toggle_notification(vk_id)
                mes = texts.profile_notification(res)

        keyboard.add_line()
        keyboard.add_callback_button('Помощь', color=VkKeyboardColor.POSITIVE, payload="/help")
        keyboard.add_callback_button('Пнуть админа', color=VkKeyboardColor.NEGATIVE, payload="/admin", type="callback")

        return mes, keyboard


if __name__ == "__main__":
    pass
