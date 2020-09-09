from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id

import vk_api

# Импорт конфигурации
from config import token, group_vk
import classifier


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
                res = classifier.Messages.parse(event.obj.text)

                vk.messages.send(
                    peer_id=event.obj.from_id,
                    random_id=get_random_id(),
                    message=res["type"])


# while True:
#     try:
#         main()
#     except Exception as e:
#         print(e.__class__)
#         print(str(e))

main()