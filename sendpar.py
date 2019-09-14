import time, sys

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

# Импорт конфигурации
from config import token, group_vk
from ScheduleBot import ScheduleBot

# Инициаизация класса бота
Controller = ScheduleBot() 

#Авторизация в ВК
vk_session = vk_api.VkApi(token=token)
vk = vk_session.get_api()

number = sys.argv[1] # Номер пары читаем из терминала

groups = Controller.get_groups() # Получаем все группы которые отслеживает бот

#Перебираем все группы
for group in groups:
    # Сохраняем (кэшируем группу)
    Controller.save_data(group[0])
    # Получаем всех пользователей из данной группы
    g_users = Controller.get_users_by_group(group[0])
    ids = ''
    # Составляем список id, допусаем что в группе <= 100 человек
    for user in g_users:
        ids += user[0]+','
    
    # Обрезаем последний(пустой)
    print(ids[:-1])
    
    # Получаем текст уведомления
    mes = Controller.generate_text_lesson(group[0], number)
    
    # Если сообщение есть
    if mes:
        # Пробуем отправить сообщение
        try:
            vk.messages.send(
                    user_ids=ids,
                    random_id=get_random_id(),
                    message=mes
                )
        except Exception as e:
            Controller.logError(e)
