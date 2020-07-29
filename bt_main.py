# -*- coding: utf-8 -*-
import getopt
import sys
import config, telebot                                                          # библиотека для telegram
from telebot import apihelper                                                   # прокси для telegram

import logging
import time
from datetime import datetime, timedelta
import bt_funcfile
import bt_analysis
import bt_sheetClass

def send_text_channel(text):
    bot.send_message(config.channel, text)
    logging.info('Send message - %s'%(config.channel))
def scraping_data():
    logging.info('Loading games from vitibet.com')
    start_time = time.time()
    v_data = bt_analysis.list_games_from_vitibet(date_now.strftime('%d.%m'))
    fn = 'vitibet_' + date_now.strftime('%d%m%y') + '.csv'
    bt_funcfile.write_csv(fn,v_data)
    logging.info('Time to loading %s seconds'%round((time.time() - start_time),1))

    logging.info('Loading games from livescore.in')
    start_time = time.time()
    one_day = datetime.today().strftime('%d/%m %a')
    two_day = datetime.today() + timedelta(days=1)
    two_day = two_day.strftime('%d/%m %a')
    l_data = bt_analysis.list_games_from_livescore(one_day,two_day)
    fn = 'livescore_' + date_now.strftime('%d%m%y') + '.csv'
    bt_funcfile.write_csv(fn,l_data)
    logging.info('Time to loading %s seconds'%round((time.time() - start_time),1))

    logging.info('Search for identical games in downloaded data')
    join = bt_analysis.find_games_in_livescore(v_data,l_data)

    join = bt_analysis.del_notFoundGames(join)
    join = bt_analysis.del_index(join)
    join = bt_analysis.update_datetime(join)

    fn = 'vitilive_' + date_now.strftime('%d%m%y') + '.csv'
    bt_funcfile.write_csv(fn,join)
def update_info_match(delta=0):
    date_now = datetime.today()
    if (delta > 0):
        date_now = date_now - timedelta(days=delta)

    fn = 'vitilive_' + date_now.strftime('%d%m%y') + '.csv'
    join = bt_funcfile.read_csv(fn)
    join = bt_analysis.data_for_sheet(join)
    fn = 'join_' + date_now.strftime('%d%m%y') + '.csv'
    bt_funcfile.write_csv(fn,join,encode='cp1251')
def update_googlesheet(delta=0):
    date_now = datetime.today()
    fn = 'join_' + date_now.strftime('%d%m%y') + '.csv'
    if (delta > 0):
        date_now = date_now - timedelta(days=delta)
        fn = 'join_' + date_now.strftime('%d%m%y') + '.csv'

    join = bt_funcfile.read_csv(fn)

    fn = 'list_googlesheets.csv'
    listSheet = bt_funcfile.read_csv(fn)

    #any(x == date_now.strftime('%d%m%y') for x, *_ in listSheet):
    r = [i for i, x in enumerate(listSheet) if x[0] == date_now.strftime('%d%m%y')]
    if len(r) > 0:
        ss = bt_sheetClass.Spreadsheet(CREDENTIALS_FILE,debugMode=False)
        ss.set_spreadsheetById(listSheet[r[0]][1])
        logging.info('Use spreadsheet %s'%ss.spreadsheetId)
        #print(a[0])
    else:
        ss = bt_sheetClass.Spreadsheet(CREDENTIALS_FILE)
        title = 'SoccerInfo_' + date_now.strftime('%d%m%y')
        rows = len(join)+1
        ss.create_sheets(title,'Soccer',rows)
        ss.share_sheets()
        spreadsheet = ss.spreadsheetId
        logging.info('Create new spreadsheetId')
        new = [[date_now.strftime('%d%m%y'), spreadsheet]]
        bt_funcfile.write_add_csv('list_googlesheets.csv',new)
        logging.info('SpreadsheetId write in file "list_googlesheets.csv"')
        #print(a[0])

    msg = bt_sheetClass.get_reportSheet(join,ss)
    logging.info(msg)
    return msg

def main():
    logging.info('ARGV      : %s'%sys.argv[1:])
    options, remainder = getopt.getopt(sys.argv[1:], '', ['updodd','finish'])
    logging.info('OPTIONS   : %s'%options)

    for opt, arg in options:
        if opt in ('--updodd'):
            update_info_match()
            update_googlesheet()
            bot.send_message(config.creator, '--updodd')
            exit()
        elif opt in ('--finish'):
            update_info_match(1)
            update_googlesheet(1)
            bot.send_message(config.creator, '--finish')
            exit()

    scraping_data()
    update_info_match()
    msg = update_googlesheet()
    bot.send_message(config.channel, msg)
    logging.info('Send message in channel')

if __name__ == '__main__':
    CREDENTIALS_FILE = 'scoreInfo-6794ceb9b944.json'
    bot = telebot.TeleBot(config.token)
    apihelper.proxy = config.proxy
    # Настраиваем логгер
    date_now = datetime.today()
    logname = 'log/bt_' + date_now.strftime('%d%m%y') + '.log'
    logging.basicConfig(
        handlers = [logging.FileHandler(logname, 'a', 'utf-8'),logging.StreamHandler()],
        format = '[%(asctime)s] %(filename)s:%(lineno)d %(levelname)s - %(message)s',
        datefmt = '%d.%m.%y %H:%M:%S',
        level = logging.INFO
    )
    main()
