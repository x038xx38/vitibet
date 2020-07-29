# -*- coding: utf-8 -*-
import config, telebot
from telebot import apihelper
import sheetClass
import funcfile
import analysis
from datetime import datetime, timedelta

bot = telebot.TeleBot(config.token)
#apihelper.proxy = config.proxy

@bot.message_handler(commands=['start'])
def send_server(message):
    #try:
        delta = 1
        date_now = datetime.today()
        date_find = date_now - timedelta(days=delta)

        # Этапы прохождения/проверки данных для join_(date).csv
        fn = 'vitibet_' + date_find.strftime('%d%m%y') + '.csv'
        v_data = funcfile.read_csv(fn)

        fn = 'livescore_' + date_find.strftime('%d%m%y') + '.csv'
        l_data = funcfile.read_csv(fn)

        join = analysis.find_games_in_livescore(v_data,l_data)
        join = analysis.del_notFindGames(join)
        join = analysis.del_index(join)                                         #[ <=-2 ... 2>= ]
        join = analysis.data_forSheet(join)

        print('join total - ', join)

        fn = 'list_googlesheets.csv'
        listSheet = funcfile.read_csv(fn)
        spreadsheet = listSheet[len(listSheet)-delta-1][1]

        msg = sheetClass.get_reportSheet(join,spreadsheet)


        # Берем данные из архива
        #fn = 'join_' + date_find.strftime('%d%m%y') + '.csv'
        #join = funcfile.read_csv(fn)

        #msg = 'Today - ' + date_now.strftime('%d%m%y') + '\n' + 'Find date - ' + date_find.strftime('%d%m%y')
        bot.send_message(config.creator, msg)
    #except Exception as e:
    #    bot.send_message(config.creator, "Ошибка обработки команды.")

def main():
    bot.polling()

if __name__ == '__main__':
    main()

# Набросок для расчета банка по авто прогнозам ...
#        bank = 100
#        msg =  'Your start bank - ' + str(bank) + '$ \n'
#        for i in range(0,len(join),2):
            #print(join[i])
            #print(join[i+1])
#            if join[i][4] == '2' and join[i+1][6]>join[i+1][6]:
                #print('+')
#                bank = bank - 10
#                sum = 10 * float(join[i+1][9])
#            elif join[i][4] == '1' and join[i+1][5]>join[i+1][6]:
                #print('+')
#                bank = bank - 10
#                sum = 10 * float(join[i+1][7])
#            else:
                #print('-')
#                bank = bank - 10
#                sum = 0

#            bank += sum
            #print('bank - ',bank)
#            msg += '- upd bank - ' + str(bank) + '$\n'
