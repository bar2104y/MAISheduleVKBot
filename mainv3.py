import vk_api,time, sqlite3
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor 
from parse import parse
from config import token,group_vk

conn = sqlite3.connect("MAIShedule.db")
cursor = conn.cursor()



def main():
    vk_session = vk_api.VkApi(token=token)
    longpoll = VkBotLongPoll(vk_session, group_vk)
    vk = vk_session.get_api()

    for event in longpoll.listen():
        
        if event.type == VkBotEventType.MESSAGE_NEW:
            url = 'https://mai.ru/education/schedule/detail.php?group='
            text = event.obj.text.upper()

            if text in ['НЕТ',"СБРОСИТЬ","ОТМЕНИТЬ"]:
                cursor.execute("DELETE FROM usersgroup WHERE user_id=?", (event.obj.from_id,))
                print('Удалено')
                conn.commit()
                vk.messages.send(
                        peer_id=event.obj.from_id,
                        random_id=get_random_id(),
                        message='Не твоя - так не твоя('
                    )
            else:
                cursor.execute("SELECT * FROM usersgroup WHERE user_id=?", (event.obj.from_id,))
                user_db = cursor.fetchall()
                
                

                if len(user_db) > 0:
                    url += user_db[0][1]
                else:
                    url += text
                info = parse(url)
                
                if info != None or len(info) < 3:
                    mes = 'Держи расписание на ближайшие два дня\n\n'
                    for i in range(1, 3):
                        mes += info[i][0]+'\n'
                        for para in info[i][1]:
                            mes += 'Время: '+para[0]+'\n'
                            mes += 'Тип: '+para[1]+'\n'
                            mes += 'Что: '+para[2]+'\n'
                            mes += 'Где: '+para[3]+'\n\n'

                    keyboard = VkKeyboard(one_time=False)
                    keyboard.add_button('Сбросить', color=VkKeyboardColor.NEGATIVE)

                    try:
                        vk.messages.send(
                        peer_id=event.obj.from_id,
                        random_id=get_random_id(),
                        keyboard=keyboard.get_keyboard(),
                        message=mes
                        
                    )
                    except Exception as e:
                        logmes = '[{}] {}\n'.format(time.strftime("%d/%m-%H:%M:%S", time.localtime()), str(e))
                
                        f = open('BotLog.log', 'a')
                        f.write(logmes)
                        f.close()

                    cursor.execute("SELECT * FROM usersgroup WHERE user_id=?", (event.obj.from_id, ))
                    
                    if len(cursor.fetchall()) == 0:
                        cursor.execute("INSERT INTO usersgroup  VALUES (?,?)", (event.obj.from_id, event.obj.text.upper()))
                    
                    conn.commit()
                    
                
                    
                else:
                    vk.messages.send(
                        peer_id=event.obj.from_id,
                        random_id=get_random_id(),
                        message='Скажи номер группы, я нипонял'
                    )
            
            
            try:
                logmes = '[{}] Mess from [{}] text: {}\n'.format(time.strftime("%d/%m-%H:%M:%S", time.localtime()), event.obj.from_id, event.obj.text)
                
                f = open('BotLog.log', 'a')
                f.write(logmes)
                f.close()

            except Exception as e:
                print(e.__class__)

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


while True:
    try:
        main()
    except Exception as e:
        print(e.__class__)