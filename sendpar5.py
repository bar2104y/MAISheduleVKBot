import vk_api,sqlite3,time
from vk_api.utils import get_random_id
from dbcontroller import get_group_pars_today, save_data
from config import token

vk_session = vk_api.VkApi(token=token)
vk = vk_session.get_api()

users = [str(209832291)]

#Определение требуемых групп
conn = sqlite3.connect("MAIShedule.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM usersgroup WHERE 1")
data = cursor.fetchall()
groups = []

for dat in data:
    if dat[0] not in users:
        users.append(dat[0])
    
    if dat[1] not in groups:
        groups.append(dat[1])

logmes = '[{}] Find users ({}) {}\n'.format(time.strftime("%d/%m-%H:%M:%S", time.localtime()), len(users) , users)
logmes += '[{}] Find groups ({}) {}\n'.format(time.strftime("%d/%m-%H:%M:%S", time.localtime()), len(groups), groups)
try:
    f = open('BotLog.log', 'a')
    f.write(logmes)
    f.close()
except Exception as e:
    print(e.__class__)

for group in groups:
    save_data(group)


for group in groups:
    cursor.execute("SELECT `user_id` FROM usersgroup WHERE `group_n` = ?", (group,))
    user_ids_db = cursor.fetchall()
    user_ids = ''
    for user_id in user_ids_db:
        user_ids += str(user_id[0])+','

    tmp = get_group_pars_today(group)

    try:
        i=0
        while tmp[i][2] != '16:30 – 18:00': i+=1
        tmp = tmp[i]
        mes = 'Сегодня наверное '+tmp[1]+'\nГруппа: ' +tmp[0]+'\n\nСледущая пара '+tmp[2]+'\n'
        mes += tmp[4]+'\n'+tmp[3]+'\n'+tmp[5]+'\n'

        try:
            vk.messages.send(
                user_ids=user_ids,
                random_id=get_random_id(),
                message=mes
            )
            logmes = '[{}]User [{}] from group [{}] SUCCESSFUL\n'.format(time.strftime("%d/%m-%H:%M:%S", time.localtime()),dat[0],dat[1])
        except Exception as e:
            logmes = '[{}] {}\n'.format(time.strftime("%d/%m-%H:%M:%S", time.localtime()), str(e))
        finally:
            f = open('BotLog.log', 'a')
            f.write(logmes)
            f.close()

    except Exception as e:
        print(str(e))
    
    time.sleep(1)