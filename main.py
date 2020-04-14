import telebot
import config
import requests
from bs4 import BeautifulSoup as BS
import json
import pycountry

bot = telebot.TeleBot(config.TOKEN)
city = ""
city1 = ""


@bot.message_handler(commands=['start','help'])
def main(message):
    bot.send_message(message.chat.id, " Я сервис для прогноза погоды.☂️ С помощью меня ты сможешь узнать прогноз погоды на столько дней, сколько ты хочешь (но не больше 5).\n\
Также ты можешь узнать, какая погода сейчас в твоем городе и получить рекомендации. Итак давай перейдем к комнадам:\n\
Погода - Погода в данный момент времени⏰\n\
Прогноз погоды на x дней - Почасовой прогноз погоды на x дней вперед, где x - целое число больше 0 и меньше 5. Нецелые числа буду округлять.😠\n\
Поменять город - Поменять текущий город🏙\n\
А теперь введи название города и страны через запятую, если еще не вводил конечно же.🌉")


def main_message(city,data,message):
    bot.send_message(message.chat.id,"Температура в городе " + str(city) +  " сейчас: " + str(data["main"]["temp"])+"°C\n" + \
                                        "Максимальная температура: " + str(data["main"]["temp_max"])+"°C\n" + \
                                        "Минимальная температура: " + str(data["main"]["temp_min"])+"°C\n" + \
                                        "Давление: " + str(data["main"]["pressure"]) + "гПа\n" + \
                                        "Скорость ветра: " + str(data["wind"]["speed"]) + "м/с\n" + \
                                        "Погодные  условия: " + data["weather"][0]["description"] )
    flag1 = ('дождь' in data["weather"][0]["description"].split())
    flag2 = ('снег' in data["weather"][0]["description"].split())
    if (data["main"]["temp"] <= -15):
        text = "Cегодня очень холодно. Одевайтесь как можно теплее.🥶"
        if (flag2):
            text = text + "\nНе забывайте, что на улице идёт снег."
        if (flag1):
            text = text + "\nНе забывайте, что на улице идёт дождь. Возьмите зонтик."
        bot.send_message(message.chat.id, text)
    else:
        if (-15 < data["main"]["temp"] <= 0):  
            text = "На улице меньше нуля. Не забывате одеваться теплее.🥶"          
            if (flag2):
                text = text + "\nНе забывайте, что на улице идёт снег."
            if (flag1):
                text = text + "\nНе забывайте, что на улице идёт дождь. Возьмите зонтик."
            bot.send_message(message.chat.id, text)   
        else:
            if (0 < data["main"]["temp"] <= 15): 
                text =  "На улице прохладно. Оденьте пальто или осеннюю куртку.💨"          
                if (flag2):
                    text = text + "\nНе забывайте, что на улице идёт снег."
                if (flag1):
                    text = text + "\nНе забывайте, что на улице идёт дождь. Возьмите зонтик."
                bot.send_message(message.chat.id, text)   
            else:
                if (15 < data["main"]["temp"] < 25): 
                    text = "На улице уже тепло. Можно выходить просто в кофте или футболке.😊"         
                    if (flag2):
                        text = text + "\nНе забывайте, что на улице идёт снег."
                    if (flag1):
                        text = text + "\nНе забывайте, что на улице идёт дождь. Возьмите зонтик."
                    bot.send_message(message.chat.id, text)   
                else:
                    if (data["main"]["temp"] >25): 
                        text =  "На улице жарко. Можете смело идти в футболке🥵"        
                        if (flag2):
                            text = text + "\nНе забывайте, что на улице идёт снег."
                        if (flag1):
                            text = text + "\nНе забывайте, что на улице идёт дождь. Возьмите зонтик."
                        bot.send_message(message.chat.id, text) 
        

@bot.message_handler(content_types=['text'])
def func(message):
    global city
    global city1
    print(city)
    if (city == ""):
        city = message.text.split(',')   
        city1 =  message.text
        if (len(city)!=2):
            bot.send_message(message.chat.id, "Пожалуйста введите город, и страну через запятую.")
            city = ""
        else:
            url = 'https://translate.yandex.net/api/v1.5/tr.json/translate?' 
            key = 'trnsl.1.1.20190227T075339Z.1b02a9ab6d4a47cc.f37d50831b51374ee600fd6aa0259419fd7ecd97' 
            lang = 'ru-en' 
            r1 = requests.post(url, data={'key': key, 'text': city[0], 'lang': lang}) 
            r2 = requests.post(url, data={'key': key, 'text': city[1], 'lang': lang}) 
            try:
                country = pycountry.countries.search_fuzzy(json.loads(r2.text)['text'][0])[0].alpha_2
            except:
                country = "-6"
            city1 = city[0]
            city = json.loads(r1.text)['text'][0]+","+country
            r = requests.get('http://api.openweathermap.org/data/2.5/weather?&units=metric&q=%s&appid=0c9f3c052f1d81b7062750ff0926f345' %(city), params={'lang': 'ru'})
            data = r.json()
            if (data['cod'] == '404'):
                bot.send_message(message.chat.id, "Похоже я не могу найти ваш город. Поробуйте ещё раз. Может вы ошиблись, когда набирали название?")
                city = ""
            else:
                main_message(city1,data,message)
    else:
        if (message.text.lower() == "погода"):
            
            r = requests.get('http://api.openweathermap.org/data/2.5/weather?&units=metric&q=%s&appid=0c9f3c052f1d81b7062750ff0926f345' %(city), params={'lang': 'ru'})
            data = r.json()
            main_message(city1,data,message)
        else:
            mes = message.text.split()
            if (mes[0].lower() == 'прогноз'):
                if(len(mes) != 5):
                    bot.send_message(message.chat.id, "Введите, пожалуйста фразу в виде Прогноз погоды на x дней")
                else:
                    try:
                        if (int(mes[3]) < 0) or (int(mes[3]) > 5):
                            bot.send_message(message.chat.id, "Напоминаю количество дней должно быть меньше 5, но больше 0")
                        else:
                            r = requests.get('http://api.openweathermap.org/data/2.5/forecast?&units=metric&q=%s&appid=0c9f3c052f1d81b7062750ff0926f345' %(city), params={'lang': 'ru'})
                            data = r.json()
                            str1 = ""
                            k = 0
                            start = -2
                            for i in data['list']:
                                if (int(i['dt_txt'][8:10]) != start):
                                    k = k+1
                                    start = int(i['dt_txt'][8:10])
                                    if ( k > int(mes[3])):
                                        break
                                str1 = str1 +  str(i['dt_txt']) + " "  + '{0:+3.0f}'.format(i['main']['temp']) +  " " + i['weather'][0]['description'] + "\n"
                            bot.send_message(message.chat.id, str1)
                    except:
                            bot.send_message(message.chat.id, "Напоминаю количество дней должно быть меньше 5, но больше 0")
            else:
                if (message.text.lower()=="поменять город"):
                    city = ""
                    bot.send_message(message.chat.id, "Пожалуйста введите город, и страну через запятую.")
                else:
                    bot.send_message(message.chat.id, "Я вас не понимаю. Напишите команду /help")




bot.polling()