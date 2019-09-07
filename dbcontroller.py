import sqlite3
from parse import parse
import time

def save_data(group_id, today=time.strftime("%d.%m", time.localtime())):
    res = parse('https://mai.ru/education/schedule/detail.php?group='+group_id)
    
    conn = sqlite3.connect("MAIShedule.db")
    cursor = conn.cursor()
    
    if res[0] == 200:
        # Пребор дней
        for i in range(1,len(res)):

            cursor.execute("SELECT * FROM groupsShedule WHERE group_id=? and day_i=?", (group_id, res[i][0]))

            
            if len(cursor.fetchall()) == 0:
                for j in range(len(res[i][1])):
                    cursor.execute("INSERT INTO groupsShedule VALUES (?,?,?,?,?,?)",
								(group_id, res[i][0],
                                res[i][1][j][0], res[i][1][j][1],
                                res[i][1][j][2], res[i][1][j][3]))
            else:
                for j in range(len(res[i][1])):
                    cursor.execute("UPDATE groupsShedule SET type=?,name =?,room=? WHERE group_id=? and day_i=? and time=?",
								( res[i][1][j][1], res[i][1][j][2],
                                res[i][1][j][3], group_id,
                                res[i][0], res[i][1][j][0]))

            conn.commit()

            try:
                logmes = '[{}] Cached group: {} date: {} \n'.format(time.strftime("%d/%m-%H:%M:%S", time.localtime()),group_id, res[i][0])
            
                f = open('BotLog.log', 'a')
                f.write(logmes)
                f.close()

            except Exception as e:
                print(e.__class__)

        
    


def get_group_pars_today(group_id):
    today=time.strftime("%d.%m", time.localtime())
    # today="10.09"

    conn = sqlite3.connect("MAIShedule.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM groupsShedule WHERE group_id=? and day_i=?", (group_id, today))
    tmp = cursor.fetchall()

    return(tmp)
