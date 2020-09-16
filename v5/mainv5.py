import classifier
import texts
import data_controller
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id

# Импорт конфигурации
from config import token, group_vk


def main():
    # Инициализация бота
    vk_session = vk_api.VkApi(token=token)
    longpoll_session = VkBotLongPoll(vk_session, group_vk)
    vk = vk_session.get_api()

    # Прослушивание событий
    for event in longpoll_session.listen():
        # Из всех событий нас интересуют только новые сообщения
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.obj.from_id == 209832291:
                if event.obj.text == "stop":
                    exit(111)
                res = classifier.Messages.parse(event.obj.text)
                if res["is_to_bot"]:
                    if "schedule" in res["type"]:
                        mes, keyboard = data_controller.Schedule.response(res, event.obj.from_id)
                    elif "profile" in res["type"]:
                        mes, keyboard = data_controller.Profile.response(res, event.obj.from_id)
                    else:
                        pass
                else:
                    mes = texts.no_to_bot_mes()

                vk.messages.send(
                    peer_id=event.obj.from_id,
                    random_id=get_random_id(),
                    message=mes)


# while True:
#     try:
#         main()
#     except Exception as e:
#         print(e.__class__)
#         print(str(e))

if __name__ == "__main__":
    main()
