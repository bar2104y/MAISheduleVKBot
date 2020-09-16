import db_controller as db
import texts


class Schedule:
    @staticmethod
    def response(a, vk_id):
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
            db.Controller.get_schedule_n_day(user.group)



        return mes, keyboard

        #if type == "schedule_today":


class Profile:
    @staticmethod
    def response(a, vk_id):
        type = a["type"]
        data = a["data"]

        mes = texts.unknown_error()
        keyboard = None
        print(type)
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

        return mes, keyboard


if __name__ == "__main__":
    pass
