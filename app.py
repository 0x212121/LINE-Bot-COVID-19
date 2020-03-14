from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
from random import randint
import json
import requests
import config as conf

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi(conf.access_token)
# Channel Secret
handler = WebhookHandler(conf.token_secret)

greetings = "Terima kasih telah menambahkan kaim ke dalam grup " + chr(0x10008D) + "\nUntuk petunjuk penggunaan silahkan ketikkan /help"
keyword = "Gunakan kata kunci berikut untuk mendapatkan informasi seputar virus corona:\n\n/data - Data jumlah kasus corona\n/hotline - Hotline corona\n/info - Informasi penting seputar virus corona\n/tips - Tips singkat\n/help - Bantuan\n/hoax - Kumpulan berita terkait hoax virus corona"

# Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# Number grouping
# Works in integer type only
def group(number):
    s = '%d' % number
    groups = []
    while s and s[-1].isdigit():
        groups.append(s[-3:])
        s = s[:-3]
    return s + '.'.join(reversed(groups))

@handler.add(JoinEvent)
def handle_join(event):
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=greetings))

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg_from_user = event.message.text
    if msg_from_user.lower() == '/help':
        message = TextSendMessage(text=keyword)
        line_bot_api.reply_message(event.reply_token, message)

    elif msg_from_user.lower() == "/fact":
        response = requests.get('https://cat-fact.herokuapp.com/facts')
        kucing = json.loads(response.text)
        i = randint(0, 200) 
        fact = kucing['all'][i]['text']
        message = TextSendMessage(fact)
        line_bot_api.reply_message(event.reply_token, message)

    elif msg_from_user.lower() == '/data':
        abc = "Corona COVID-19 Live Data"
        region, death, confirm, recover = [], [], [], []

        try:
            response = requests.get('https://corona.lmao.ninja/countries/')
            data = json.loads(response.text)
            for i in range(len(data)):
                region.append(data[i]['country'])
                confirm.append(group(data[i]['cases']))
                death.append(group(data[i]['deaths']))
                recover.append(group(data[i]['recovered']))
                if data[i]['country'] == "Indonesia": id = i
            response = requests.get('https://corona.lmao.ninja/all/')
            all_ = json.loads(response.text)
            total = "Total positif: " + group(all_['cases']) + chr(0x10007B)+"\nTotal meninggal: " + group(all_['deaths']) + chr(0x10007C)+ "\nTotal sembuh: " + group(all_['recovered']) + chr(0x10007A)
        except:
            response = requests.get('https://api.kawalcorona.com/')
            status = response.status_code
            data = json.loads(response.text)
            for i in range(len(data)):
                region.append(data[i]['attributes']['Country_Region'])
                confirm.append(group(data[i]['attributes']['Confirmed']))
                death.append(group(data[i]['attributes']['Deaths']))
                recover.append(group(data[i]['attributes']['Recovered']))
                if data[i]['attributes']['Country_Region'] == "Indonesia": id = i
            response_pos = requests.get('https://api.kawalcorona.com/positif/')
            data1 = json.loads(response_pos.text)
            data1 = int(data1['value'].replace(",",""))
            response_rec = requests.get('https://api.kawalcorona.com/sembuh/')
            data2 = json.loads(response_rec.text)
            data2 = int(data2['value'].replace(",",""))
            response_death = requests.get('https://api.kawalcorona.com/meninggal/')
            data3 = json.loads(response_death.text)
            data3 = int(data3['value'].replace(",",""))
            total = "Total positif: " + group(data1) + chr(0x10007B)+"\nTotal meninggal: " + group(data3) + chr(0x10007C)+ "\nTotal sembuh: " + group(data2) + chr(0x10007A)

        carousel = open("carousel_template.json", "r").read()

        bubble_string = carousel

        dictionary = json.loads(bubble_string)
        item = dictionary['contents'][0]['body']['contents'][3]['contents']
        item2 = dictionary['contents'][1]['body']['contents'][3]['contents']

        # Insert data
        # Dictionary index based on json file
        for i in range(len(item)):
            if i == 15:
                item[i]['contents'][0]['text'] = item2[i]['contents'][0]['text'] = region[id]
                item[i]['contents'][2]['text'] = confirm[id]
                item[i]['contents'][4]['text'] = death[id]
                item2[i]['contents'][2]['text'] = recover[id]
                break

            item[i]['contents'][0]['text'] = item2[i]['contents'][0]['text'] = region[i]
            item[i]['contents'][2]['text'] = confirm[i]
            item[i]['contents'][4]['text'] = death[i]
            item2[i]['contents'][2]['text'] = recover[i]

        # Convert dictionary to json
        bubble_string = json.dumps(dictionary)

        message = [FlexSendMessage(alt_text="Flex Message", contents=json.loads(bubble_string)), TextSendMessage(text=total)]
        line_bot_api.reply_message(event.reply_token, message)

    elif msg_from_user.lower() == '/hotline':
        bubble = BubbleContainer(
            direction='ltr',
            hero=ImageComponent(
                url='https://banner2.cleanpng.com/20180323/jyw/kisspng-droid-razr-hd-iphone-computer-icons-telephone-call-phone-5ab5b8eb53a3a3.5126635715218587953426.jpg',
                size='full',
                aspect_ratio='2:1',
                aspect_mode='fit'
            ),
            body=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text='Hotline Corona', weight='bold', size='lg', align='center')
                ],
            ),
            footer=BoxComponent(
                layout='horizontal',
                spacing='sm',
                contents=[
                    SeparatorComponent(),
                    # callAction
                    ButtonComponent(
                        style='link',
                        height='sm',
                        position='relative',
                        action=URIAction(label='Telpon', uri='tel:0215210411'),
                    ),
                    # separator
                    SeparatorComponent(),
                    # websiteAction
                    ButtonComponent(
                        style='link',
                        height='sm',
                        position='relative',
                        action=URIAction(label='HP', uri='tel:081212123119')
                    )
                ]
            ),
        )
        message = FlexSendMessage(alt_text="Hotline Corona", contents=bubble)
        line_bot_api.reply_message(event.reply_token,message)

    elif msg_from_user.lower() == '/info':
        url1 = 'https://www.unicef.org/indonesia/id/coronavirus'
        url2 = 'https://www.kompas.com/tren/read/2020/03/03/183500265/infografik-daftar-100-rumah-sakit-rujukan-penanganan-virus-corona'
        url3 = 'https://infeksiemerging.kemkes.go.id/'
        url4 = 'https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public'

        link = "Informasi penting yang perlu anda diketahui seputar Coronavirus dapat ditemukan pada tautan yang tersedia dibawah:\n\n[1] %s\n[2] %s\n[3] %s\n[4] %s" % (url1, url2, url3, url4)

        message = TextSendMessage(text=link)
        line_bot_api.reply_message(event.reply_token, message)

    elif msg_from_user.lower() == '/tips':
        tips = "Jangan lupa mencuci tangan dengan sabun hingga bersih setelah beraktivitas di luar rumah."
        message = TextSendMessage(text=tips)
        line_bot_api.reply_message(event.reply_token, message)

    elif msg_from_user.lower() == '/hoax':
        bubble = BubbleContainer(
            direction='ltr',
            hero=ImageComponent(
                url='https://www.mafindo.or.id/wp-content/uploads/2017/10/logo-turn-back-hoax-300x300.png',
                size='full',
                aspect_ratio='1:1',
                aspect_mode='cover'
                # action=URIAction(uri='', label='label')
            ),
            body=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text='Kumpulan hoax terkait virus Corona', weight='bold', size='sm', align='center', wrap=True)
                ],
            ),
            footer=BoxComponent(
                layout='vertical',
                spacing='sm',
                contents=[
                    # callAction, separator, websiteAction
                    SpacerComponent(),
                    # callAction
                    ButtonComponent(
                        style='primary',
                        height='sm',
                        size='md',
                        action=URIAction(label='Buka Tautan', uri='https://kominfo.go.id/content/all/virus_corona'),
                    )
                ]
            ),
        )
        message = FlexSendMessage(alt_text="Kumpulan Hoax Virus Corona", contents=bubble)
        line_bot_api.reply_message(event.reply_token,message)

    elif msg_from_user.lower() == '/today':
        region, today_cases, today_deaths = [], [], []

        # try:
        response = requests.get('https://corona.lmao.ninja/countries')
        data = json.loads(response.text)
        for i in range(len(data)):
            region.append(data[i]['country'])
            today_cases.append(data[i]['todayCases'])
            today_deaths.append(group(data[i]['todayDeaths']))

        zipped = list(zip(today_cases, today_deaths, region))
        zipped.sort(reverse=True)

        carousel = open("carousel_today_case.json", "r").read()
        bubble_string = carousel

        dictionary = json.loads(bubble_string)
        print(dictionary)
        item = dictionary['contents'][0]['body']['contents'][3]['contents']

        # Insert data
        # Dictionary index based on json file
        for i in range(len(item)):
            item[i]['contents'][0]['text'] = zipped[i][2]
            item[i]['contents'][2]['text'] = zipped[i][0]
            item[i]['contents'][4]['text'] = zipped[i][1]

        # Convert dictionary to json
        bubble_string = json.dumps(dictionary)
        message = FlexSendMessage(alt_text="Flex Message", contents=json.loads(bubble_string))
        line_bot_api.reply_message(event.reply_token, message)
    else:
        message = TextSendMessage(text="Kata kunci yang anda masukkan salah! Ketikkan '/help' untuk melihat bantuan")
        line_bot_api.reply_message(event.reply_token, message)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
