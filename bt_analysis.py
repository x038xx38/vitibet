# -*- coding: utf-8 -*-
from lxml import html
import requests
import unicodedata
import logging

from datetime import datetime, timedelta
from operator import itemgetter #sort

import pytz
import re

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.chrome.options import Options


# BetTraffic
def get_moreInfo_vitibet(url):
    '''
    Берем более подробную информация по игре
    '''
    url = 'http://www.vitibet.com/' + url
    page = requests.get(url)
    tree = html.fromstring(page.content)
    path = '//table[@class="malypismonasedym"][1]/'
    try:
        power_home = tree.xpath(path+'tr[1]/td[2]/text()')[0]
        power_away = tree.xpath(path+'tr[1]/td[4]/text()')[0]
        recent_form_home = tree.xpath(path+'tr[2]/td[2]/text()')[0]
        recent_form_away = tree.xpath(path+'tr[2]/td[4]/text()')[0]
        power_home = re.sub('^\s+|\n|\t|\r|\s+$', '', power_home)
        power_away = re.sub('^\s+|\n|\t|\r|\s+$', '', power_away)
        recent_form_home = re.sub('^\s+|\n|\t|\r|\s+$', '', recent_form_home)
        recent_form_away = re.sub('^\s+|\n|\t|\r|\s+$', '', recent_form_away)
    except IndexError:
        power_home = power_away = recent_form_away = recent_form_home = '-'
    #print('power_home - ', power_home, ' power_away -', power_away, ' form_home - ', recent_form_home, ' form_away - ', recent_form_away)
    info = [power_home,power_away,recent_form_home,recent_form_away]
    return info
# BetTraffic
def list_games_from_vitibet(date_now):
    '''
    Функция возвращает данные по играм за текущую дату
    '''
    url = 'http://www.vitibet.com/index.php?clanek=quicktips&sekce=fotbal&lang=en'
    page = requests.get(url)
    logging.info('URL - %s'%page.url)
    logging.info('Response code - %s'%page.status_code)
    tree = html.fromstring(page.content)
    path = '//table[@class="tabulkaquick"]/tr'
    row = tree.xpath(path)
    tips = []
    n = 1 # Порядковый номер
    i = 3 # Первые 2 строки заголовки, пропускаем их
    while i <= len(row):
        try:
            date_game = tree.xpath(path+'['+str(i)+']/td[1]')[0]
            if (date_game.text == date_now):
                team_home = tree.xpath(path+'['+str(i)+']/td[2]/a/text()')[0]
                team_away = tree.xpath(path+'['+str(i)+']/td[3]/a/text()')[0]
                score_home = tree.xpath(path+'['+str(i)+']/td[4]/text()')[0]
                score_away = tree.xpath(path+'['+str(i)+']/td[6]/text()')[0]
                wh = tree.xpath(path+'['+str(i)+']/td[7]/text()')[0]
                draw = tree.xpath(path+'['+str(i)+']/td[8]/text()')[0]
                wa = tree.xpath(path+'['+str(i)+']/td[9]/text()')[0]
                tip = tree.xpath(path+'['+str(i)+']/td[10]/text()')[0]
                index = tree.xpath(path+'['+str(i)+']/td[11]/text()')[0]
                more = tree.xpath(path+'['+str(i)+']/td[12]/a/@href')[0]
                info = get_moreInfo_vitibet(more)
                # Нормализуем к латинским символам
                team_home = unicodedata.normalize('NFKD', team_home).encode('ascii','ignore').decode('utf-8')
                team_away = unicodedata.normalize('NFKD', team_away).encode('ascii','ignore').decode('utf-8')
                line_tip = [str(n),date_now,team_home,info[0],info[2],team_away,info[1],info[3],index,tip,score_home,score_away,wh,draw,wa]
                tips.append(line_tip)
                n += 1
                logging.info('Tips - %s'%line_tip)
        except IndexError as Ex:
            logging.info('Error parsing vitibet.com - %s'%Ex)        
        i += 1
    return tips
# BetTraffic
def list_games_from_livescore(date_now,date_next):
    '''
    Поиск игра на livescore
    На входе значения периода, для расширения диапазона поиска
    '''
    url = 'http://www.livescore.in/free/721594/'
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-proxy-server')
    chrome_options.add_argument("--proxy-server='direct://'")
    chrome_options.add_argument("--proxy-bypass-list=*")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    logging.info('Google Chrome run in mode --headless')
    driver.get(url)
    logging.info('URL - %s'%driver.current_url)
    # Now day
    logging.info('The process of downloading data for %s ...'%date_now)
    try:
        Wait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//span/a[text()="'+date_now[:-1]+'"]')))
    except TimeoutException as ex:
        logging.info('TimeoutException "date_now" - %s'%ex.message)
    page = driver.page_source
    tree = html.fromstring(page)
    day = tree.xpath('//span[@class="day today"]/span/a/text()')
    logging.info('Data for %s uploaded successfully'%day)
    event_games = []
    id_game = tree.xpath('//table[@class="soccer"]/tbody/tr/@id')
    for i in range(0,len(id_game)):
        t_home = tree.xpath('//*[@id="'+id_game[i]+'"]/td[3]/span/text()')[0]
        t_away = tree.xpath('//*[@id="'+id_game[i]+'"]/td[5]/span/text()')[0]
        event_games.append((id_game[i],t_home,t_away))
    logging.info('List of games for %s created. Count of games - %s'%(day,str(len(event_games))))
    # Next day
    logging.info('The process of downloading data for %s ...'%date_next)
    try:
        Wait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//span[@class="day today"]'))).click()
        Wait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//span[text()="'+date_next[:-1]+'"]'))).click()
        Wait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//span/a[text()="'+date_next[:-1]+'"]')))
    except TimeoutException as ex:
        logging.info('TimeoutException "date_next" - %s'%ex.message)
    page = driver.page_source
    tree = html.fromstring(page)
    day = tree.xpath('//span[@class="day today"]/span/a/text()')
    logging.info('Data %s uploaded successfully'%day)
    id_game = tree.xpath('//table[@class="soccer"]/tbody/tr/@id')
    for i in range(0,len(id_game)):
        t_home = tree.xpath('//*[@id="'+id_game[i]+'"]/td[3]/span/text()')[0]
        t_away = tree.xpath('//*[@id="'+id_game[i]+'"]/td[5]/span/text()')[0]
        event_games.append((id_game[i],t_home,t_away))
    logging.info('List of games for %s created. Total count of games - %s'%(day,str(len(event_games))))
    driver.quit()
    return event_games
# BetTraffic
def scan_teamName(w_home,w_away,list):
    line = []
    for j in range(0,len(list)):
        H = A = 0   # Счетчики совпадений
        # Проходим по названию первой команды
        for k in range(0,len(w_home)):
            str = list[j][1]
            if (str.find(w_home[k]) != -1) and (len(w_home[k]) > 2):
                H += 1
        # Проходим по названию второй команды
        for k in range(0, len(w_away)):
            str = list[j][2]
            if (str.find(w_away[k]) != -1) and (len(w_away[k]) > 2):
                A += 1
        # Если там и там количество совпадений >= 1 - игра найдена
        if (H>=1) and (A>=1):
            line =[list[j][0],list[j][1],list[j][2]]
    return line
# BetTraffic
def find_games_in_livescore(list_v,list_LS):
    '''
    Поиск игр по совпадениям слов в названии команд
    Помогает сканировать scan_teamName()
    '''
    find = 0
    for i in range(0,len(list_v)):
        words_home = list_v[i][2].split(' ')
        words_away = list_v[i][5].split(' ')
        line = scan_teamName(words_home,words_away,list_LS)
        if len(line) > 0:
            list_v[i].append(line[0])
            find += 1
        else:
            list_v[i].append('NOT_FOUND')
            logging.info('Not found - %s'%list_v[i])
    logging.info('Number of games found - %s'%find)
    return list_v
# BetTraffic
def del_notFoundGames(list):
    ''''''
    i = 0
    while i < len(list):
        if list[i][15] == 'NOT_FOUND':
            del list[i]
        elif list[i][12] == 'x' or list[i][13] == 'x' or list[i][14] == 'x':
            del list[i]
        else:
            i += 1
    logging.info('Not found games deleted')
    return list
# BetTraffic
def del_index(list,range='-2:2'):
    '''
    Для итоговой таблицы отображаем записи с индексом в интервале (-2 < x < 2)
    '''
    i = 0
    a,b = range.split(':')[0:2]
    while i < len(list):
        if float(list[i][8]) >= 0 and float(list[i][8]) < float(b):
            del list[i]
        elif float(list[i][8]) > float(a) and float(list[i][8]) <= 0:
            del list[i]
        else:
            list[i][0] = str(i+1)    # Обновляем порядковый номер
            i += 1
    logging.info('Index deleted')
    return list
# BetTraffic
def update_datetime(join):
    for i in range(0,len(join)):
        id_game = join[i][15][4:]
        url = 'https://d.myscore.ru/x/feed/dc_1_' + id_game
        page = requests.get(url,headers={'X-Fsign':'SW9D1eZo'})
        response = page.text
        pos = response.find('DC')
        dt = ''
        for j in range(pos+3,pos+13):
            dt = dt + response[j]

        utc_dt = datetime.utcfromtimestamp(int(dt))
        utc_dt = utc_dt.replace(tzinfo=pytz.UTC).astimezone(pytz.timezone('Europe/Moscow'))
        msk_dt = utc_dt.strftime('%d.%m.%d %H:%M')
        join[i][1] = msk_dt
    logging.info('Datetime updated')
    return join

def transform_odds(odd):
    odd = odd[:-1]
    odd = odd.replace('[u]','*')
    odd = odd.replace('[d]','*')
    try:
        old, new = odd.split('*')[0:2]
    except:
        return odd
        exit()
    dlt = float(new) - float(old)
    if dlt >= 0:
        odd = new + ' (+' + str(round(dlt,2)) + ')'
    else:
        odd = new + ' (' + str(round(dlt,2)) + ')'
    return odd

# BetTraffic
def get_match_odds(id_game):
    ''' transform_odds'''
    line = []
    logging.info('Get odds for the match %s'%id_game)
    url = 'https://d.myscore.ru/x/feed/d_od_'+id_game+'_ru_1_eu'
    page = requests.get(url,headers={'X-Fsign':'SW9D1eZo'})
    tree = html.fromstring(page.content)
    odd1 = odd2 = oddX = '-'
    book = ''
    try:
        book = tree.xpath('//*[@id="block-1x2-ft"]/table/tbody/tr/td[1]/div[1]/a/@title')[0]
        odd1 = tree.xpath('//*[@id="block-1x2-ft"]/table/tbody/tr/td[2]/span/text()')[0]
        oddX = tree.xpath('//*[@id="block-1x2-ft"]/table/tbody/tr/td[3]/span/text()')[0]
        odd2 = tree.xpath('//*[@id="block-1x2-ft"]/table/tbody/tr/td[4]/span/text()')[0]
        #print(odd1,oddX,odd2)
        #odd1 = transform_odds(odd1)
        #oodX = transform_odds(oddX)
        #ood2 = transform_odds(odd2)
        #print(odd1,oddX,odd2)
        line =['','','','','','','','','','','','',odd1,oddX,odd2,book]
    except IndexError:
        logging.info('Error read odds for match - %s'%id_game)
        line =['','','','','','','','','','','','','-','-','-','']
    #logging.info('bookmaker - ',book)
    #logging.info('1 - %s'%odd1)
    #logging.info('X - %s'%oddX)
    #logging.info('2 - %s'%odd2)
    logging.info(line)
    return line
# BetTraffic
def get_match_status(id_game):

    url = 'https://www.myscore.ru/match/'+id_game+'/'
    page = requests.get(url,headers={'X-Fsign':'SW9D1eZo'})
    #page.encoding = 'utf-8'
    tree = html.fromstring(page.content)
    try:
        scoreboard = tree.xpath('//div[@class="match-info"]//span[@class="scoreboard"]/text()')
        info = [scoreboard[0],scoreboard[1],'']
    except IndexError:
        info = ['','','']
        logging.info('The match - %s did not start'%id_game)
    # Делаем так, потому что иногда бывают матчи со статусом "Отменен"
    try:
        infostatus = tree.xpath('//div[@class="match-info"]/div[@class="info-status mstat"]/text()')[0]
        infostatus = re.sub('^\s+|\n|\t|\r|\s+$', '', infostatus)
        infostatus = infostatus.encode('utf-8').decode('cp1251')
        info[2] = infostatus
    except IndexError:
        info[2] = ['']
    #logging.info(info)
    return info

# BetTraffic
def data_for_sheet(join):
    '''
    get_match_odds
    get_match_status
    '''
    join.sort(key=itemgetter(1))
    # Список для подробностей ...
    list = []
    for i in range(0,len(join)):
        id_game = join[i][15][4:]
        # Получаем список коэффициентов на предстоящее событие
        list.append(get_match_odds(id_game))
        # Обновляем результат матча, если он прошел
        info = get_match_status(id_game)
        list[i][10] = info[0]
        list[i][11] = info[1]
        list[i][1] = info[2]
        join[i][0] = ' ' + str(i+1) + '.'   # Обновляем порядковый номер после сортировки
        join[i][15] = 'Myscore.ru/match/'+id_game+'/'

    total = []
    for i in range(0,len(join)):
        total.append(join[i])
        total.append(list[i])
    return total

def find_win(join):
    result = []
    for i in range(0,len(join),2):
        if join[i+1][10] != '' and join[i+1][11] != '':
            if join[i][9] == '2' and int(join[i+1][11])>int(join[i+1][10]):
                result.append('green')
            elif join[i][9] == '1' and int(join[i+1][10])>int(join[i+1][11]):
                result.append('green')
            else:
                result.append('red')
        else:
            result.append('white')
    return result
