import vk_api,time, sqlite3
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from config import token,group_vk
from parse import parse

conn = sqlite3.connect("MAIShedule.db")
cursor = conn.cursor()

def main():
    # Инициализация бота
    vk_session = vk_api.VkApi(token=token)
    longpoll = VkBotLongPoll(vk_session, group_vk)
    vk = vk_session.get_api()

    # Прослушивание событий
    for event in longpoll.listen():
        # Если новое сообщение
        if event.type == VkBotEventType.MESSAGE_NEW:
            # Подготовка данных
            url = 'https://mai.ru/education/schedule/detail.php?group='
            text = event.obj.text.upper()

            # Проверка на сброс данных
            if text in ['НЕТ',"СБРОСИТЬ","ОТМЕНИТЬ"]:
                # Удалиение информации о пользователе из БД
                cursor.execute("DELETE FROM usersgroup WHERE user_id=?", (event.obj.from_id,))
                conn.commit()

                # Уведомляем пользователя
                vk.messages.send(
                        peer_id=event.obj.from_id,
                        random_id=get_random_id(),
                        message='Не твоя - так не твоя('
                    )
            else:
                # Получаем данные о пользователе из БД
                cursor.execute("SELECT * FROM usersgroup WHERE user_id=?", (event.obj.from_id,))
                user_db = cursor.fetchall()

                # Если пользователь есть в БД, то получаем его руппу оттуда
                if len(user_db) > 0:
                    url += user_db[0][1]
                else:
                    # Иначе предполагаем, что он написал номер группы
                    url += text
                #Пробуем получить данные с сайта
                info = parse(url)
                
                # Проверка на наличие данных
                if info != None or len(info) < 3:
                    # Формирование сообщения
                    mes = 'Держи расписание на ближайшие два дня\n\n'
                    for i in range(1, 3):
                        mes += info[i][0]+'\n'
                        for para in info[i][1]:
                            mes += 'Время: '+para[0]+'\n'
                            mes += 'Тип: '+para[1]+'\n'
                            mes += 'Что: '+para[2]+'\n'
                            mes += 'Где: '+para[3]+'\n\n'
                    # Формирование клавиатуры
                    keyboard = VkKeyboard(one_time=False)
                    keyboard.add_button('Сбросить', color=VkKeyboardColor.NEGATIVE)

                    # пробуем отправить сообщение
                    try:
                        vk.messages.send(
                        peer_id=event.obj.from_id,
                        random_id=get_random_id(),
                        keyboard=keyboard.get_keyboard(),
                        message=mes
                        
                    )
                    except Exception as e:
                    # Формируем лог
                    # Потом на функцию заменю
                        logmes = '[{}] {}\n'.format(time.strftime("%d/%m-%H:%M:%S", time.localtime()), str(e))
                        f = open('BotLog.log', 'a')
                        f.write(logmes)
                        f.close()

                    # Если пользователь новый, то пишем его в БД
                    cursor.execute("SELECT * FROM usersgroup WHERE user_id=?", (event.obj.from_id, ))
                    if len(cursor.fetchall()) == 0:
                        cursor.execute("INSERT INTO usersgroup  VALUES (?,?)", (event.obj.from_id, event.obj.text.upper()))
                    conn.commit()
                    
                
                    
                else:
                    # Если ничего не получилось, то уведомляем пользователю
                    vk.messages.send(
                        peer_id=event.obj.from_id,
                        random_id=get_random_id(),
                        message='Скажи номер группы, я нипонял'
                    )
            
            
            # Логи, сделаю функцию
            try:
                logmes = '[{}] Mess from [{}] text: {}\n'.format(time.strftime("%d/%m-%H:%M:%S", time.localtime()), event.obj.from_id, event.obj.text)
                
                f = open('BotLog.log', 'a')
                f.write(logmes)
                f.close()

            except Exception as e:
                print(e.__class__)

        # Далее
        # ничего
        # интересного
        elif event.type == VkBotEventType.GROUP_JOIN:
            logmes = '[{}] Enter to group  user: {}\n'.format(time.strftime("%d/%m-%H:%M:%S", time.localtime()),event.obj.user_id)
            try:
                f = open('BotLog.log', 'a')
                f.write(logmes)
                f.close()
            except Exception as e:
                print(e.__class__)
            print(event.obj.user_id, end=' ')

        elif event.type == VkBotEventType.GROUP_LEAVE:
            logmes = '[{}] Leave from group user: {}\n'.format(time.strftime("%d/%m-%H:%M:%S", time.localtime()),event.obj.user_id)
            try:
                f = open('BotLog.log', 'a')
                f.write(logmes)
                f.close()
            except Exception as e:
                print(e.__class__)

        else:
            logmes = '[{}] Event type [{}]\n'.format(time.strftime("%d/%m-%H:%M:%S", time.localtime()), event.type)
            try:
                f = open('BotLog.log', 'a')
                f.write(logmes)
                f.close()
            except Exception as e:
                print(e.__class__)

# Включаем скрипт навсегда))
while True:
    try:
        main()
    except Exception as e:
        print(e.__class__)