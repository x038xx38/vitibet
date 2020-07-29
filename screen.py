from lxml import html
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.chrome.options import Options

import logging
from PIL import Image,ImageDraw,ImageOps,ImageFont

def get_screen_game(id_game):
    logging.info('Cкриншот "шапки" для id_game - '+id_game)
    url = 'https://www.myscore.ru/match/'+id_game+'/#match-summary'

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-proxy-server')
    chrome_options.add_argument("--proxy-server='direct://'")
    chrome_options.add_argument("--proxy-bypass-list=*")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.set_window_size(660, 150) # x=660, y=160
    driver.get(url)


    page = driver.page_source
    tree = html.fromstring(page)
    add = 0
    add_content = tree.xpath('//div[@class="team-secondary-content"]/div[@class="info-bubble"]')
    if len(add_content) > 0: add = 27
    logging.info('Проверка "шапки" на дополнительный контент - add=%s'%(add))

    driver.implicitly_wait(10) # seconds
    path = 'scr/res' + id_game+'.png'
    driver.save_screenshot(path)
    driver.quit()

    return add
    logging.info('Скриншот для id_game - '+id_game+' добавлен в '+path)


def get_screen_odds(id_game,add):
    logging.info('Cкриншот "кэффов" для id_game - '+id_game)
    url = 'https://www.myscore.ru/match/'+id_game+'/#odds-comparison;1x2-odds;full-time'

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-proxy-server')
    chrome_options.add_argument("--proxy-server='direct://'")
    chrome_options.add_argument("--proxy-bypass-list=*")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.set_window_size(660, 440+add)
    driver.get(url)
    driver.implicitly_wait(10)                                  # seconds
    path = 'scr/od' + id_game+'.png'
    driver.save_screenshot(path)
    driver.quit()

    logging.info('Скриншот для id_game - '+id_game+' добавлен в '+path)

def compile_screen(data,add):
    id_game = data[0][4:]
    image = Image.new('RGBA', (660, 410), 'white')

    # Накладывает "шапку" на белый холст
    header = Image.open('scr/h'+id_game+'.png')
    image_copy = image.copy()
    position = (0,0)
    image_copy.paste(header, position)
    image_copy.save('scr/temp.png')

    # Накладываем зеленную полоску
    image = Image.open('scr/temp.png')
    header = Image.open('scr/base/head_green.png')
    image_copy = image.copy()
    position = (0,0)
    image_copy.paste(header, position)
    image_copy.save('scr/temp.png')

    # Добавляем панель коэффициентов
    image = Image.open('scr/temp.png')
    header = Image.open('scr/base/panel_odds.png')
    image_copy = image.copy()
    position = (0,190)
    image_copy.paste(header, position)
    image_copy.save('scr/temp.png')

    # Добавляем скриншот коэффициентов
    image = Image.open('scr/temp.png')
    header = Image.open('scr/od'+id_game+'.png')
    header = ImageOps.crop(header,(0,269+add,0,0))
    image_copy = image.copy()
    position = (0,228)
    image_copy.paste(header, position)
    image_copy.save('scr/temp.png')

    # Добавляем текст к изображению
    image = Image.open('scr/temp.png')
    img_draw = ImageDraw.Draw(image)
    #img_draw.rectangle((70, 50, 270, 200), outline='red', fill='blue')
    fontsize = 48
    font = ImageFont.truetype("font/arial bold.ttf", fontsize)
    # Расчитанный счет в предстоящей игре
    goals = data[3]+'  '+data[4]
    img_draw.text((292, 75), goals, fill='#ccc', font=font)
    fontsize = 26
    font = ImageFont.truetype("font/arial bold.ttf", fontsize)
    # Вероятность победы
    pred = data[6]+'                     '+data[7]+'                     '+data[8]
    img_draw.text((105,155),pred,fill='#ccc',font=font)
    path = 'scr/post/pst_'+id_game+'.png'
    image.save(path)
    logging.info('Изображения для поста успешно создано - '+path)

def screen_result(data):
    id_game = data[0][4:]
    image = Image.new('RGBA', (660, 410), 'white')

    header = Image.open('scr/h'+id_game+'.png')
    image_copy = image.copy()
    position = (0,0)
    image_copy.paste(header, position)
    image_copy.save('scr/temp.png')

    # Накладывает "шапку" результатов на белый фон
    image = Image.open('scr/temp.png')
    header = Image.open('scr/res'+id_game+'.png')
    image_copy = image.copy()
    position = (0,220)
    image_copy.paste(header, position)
    image_copy.save('scr/temp.png')

    # Накладываем зеленную полоску
    image = Image.open('scr/temp.png')
    header = Image.open('scr/base/head_green.png')
    image_copy = image.copy()
    position = (0,0)
    image_copy.paste(header, position)
    image_copy.save('scr/temp.png')

    image = Image.open('scr/temp.png')
    img_draw = ImageDraw.Draw(image)
    #img_draw.rectangle((70, 50, 270, 200), outline='red', fill='blue')
    fontsize = 48
    font = ImageFont.truetype("font/arial bold.ttf", fontsize)
    # Расчитанный счет в предстоящей игре
    goals = data[3]+'  '+data[4]
    img_draw.text((292, 75), goals, fill='#ccc', font=font)
    fontsize = 26
    font = ImageFont.truetype("font/arial bold.ttf", fontsize)
    # Вероятность победы
    pred = data[6]+'                     '+data[7]+'                     '+data[8]
    img_draw.text((105,155),pred,fill='#ccc',font=font)

    path = 'scr/post/res_'+id_game+'.png'
    image.save(path)
