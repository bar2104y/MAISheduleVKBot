import requests, time, re
from bs4 import BeautifulSoup
def parse(base_url):
    # Мои заголовки запроса
    # headers = {'accept': '*/*',
    # 		'user-agent': 'HackerOK/1.0 (X228; MAIUntu; Linux x86_64; rv:68.0) Gecko/20100101 BRoweser/1337.0'}
    
    res = [] # Итоговый результат

    session = requests.Session() # Запрос к серверу
    request = session.get(base_url) # Ответ сервера

    res.append(request.status_code) # Код ответа
    
    logmes = '[{}] Response to [{}] with code: {}\n'.format(time.strftime("%d/%m-%H:%M:%S", time.localtime()),base_url,request.status_code)
    try:
        f = open('BotLog.log', 'a')
        f.write(logmes)
        f.close()
    except Exception as e:
        print(e.__class__)
    
    # Если есть ответ ( страница существует )
    if request.status_code == 200:
        soup = BeautifulSoup(request.content, features="lxml")
        days = soup.find_all('div', "sc-container")
    
        
        for day in days:
            day_t = day.find('div','sc-day-header').text
            day_t = re.sub(r'[^0-9\.]', '', day_t)

            time_s = day.find_all('div', 'sc-item-time')
            type_s = day.find_all('div', 'sc-item-type')
            name_s = day.find_all('span', 'sc-title')
            room_s = day.find_all('div', 'sc-item-location')

            day_res = []
            for i in range(len(time_s)):
                
                day_res.append( [time_s[i].text ,
                                        type_s[i].text,
                                        name_s[i].text,
                                        room_s[i].text] )
                
            
            res.append([day_t, day_res])
    
    return(res)