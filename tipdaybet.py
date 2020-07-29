from lxml import html
import requests
import logging

#   type:
#       - 1 - soccer
#       - 2 - hockey
#       - 3 - basketball
#
def find_tip_of_day(type):
	url = 'http://www.vitibet.com/index.php?clanek=tipoftheday&sekce=fotbal&lang=en'
	page = requests.get(url)
	tree = html.fromstring(page.content)

	tipoftheday = []
	count_tip = tree.xpath('//*[@id="tipoftheday"]/table['+str(type)+']/tr')

	liga_name=date_game=url_game=team_home=team_away=tip=index=' '

	for i in range(2,len(count_tip),2):
		try:
			liga_name = tree.xpath('//*[@id="tipoftheday"]/table['+str(type)+']/tr['+str(i)+']/td[1]/text()')[0]
			date_game = tree.xpath('//*[@id="tipoftheday"]/table['+str(type)+']/tr['+str(i)+']/td[2]/text()')[0]
			url_game = tree.xpath('//*[@id="tipoftheday"]/table['+str(type)+']/tr['+str(i)+']/td[1]/a/@href')[0]

			team_home = tree.xpath('//*[@id="tipoftheday"]/table['+str(type)+']/tr['+str(i+1)+']/td[2]/text()')[0]
			team_away = tree.xpath('//*[@id="tipoftheday"]/table['+str(type)+']/tr['+str(i+1)+']/td[3]/text()')[0]
			tip = tree.xpath('//*[@id="tipoftheday"]/table['+str(type)+']/tr['+str(i+1)+']/td[5]/text()')[0]
			index = tree.xpath('//*[@id="tipoftheday"]/table['+str(type)+']/tr['+str(i+1)+']/td[6]/text()')[0]
		except IndexError:
			logging.exception('Ошибка при добавление строки i -'+i)

		tipoftheday.append((liga_name.strip(' '),
							date_game.strip(' '),
							url_game.strip(' '),
							team_home.strip(' '),
							team_away.strip(' '),
							tip.strip(' '),
							index.strip(' ')))
	return tipoftheday
