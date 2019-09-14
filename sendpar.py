import time,  sys

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

# Импорт конфигурации
from config import token, group_vk
from ScheduleBot import ScheduleBot

Controller = ScheduleBot() 


vk_session = vk_api.VkApi(token=token)
vk = vk_session.get_api()

number = sys.argv[1]

groups = Controller.get_groups()

for group in groups:
    Controller.save_data(group[0])
    g_users = Controller.get_users_by_group(group[0])
    ids = ''
    for user in g_users:
        ids += user[0]+','
    
    print(ids[:-1])
    
    mes = Controller.generate_text_lesson(group[0], number)
    
    if mes:
        try:
            vk.messages.send(
                    user_ids=ids,
                    random_id=get_random_id(),
                    message=mes
                )
        except Exception as e:
            Controller.logError(e)
