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
news_api_key = (conf.news_key)

greetings = "Terima kasih telah menambahkan kami ke dalam grup " + chr(0x10008D) + "\nUntuk petunjuk penggunaan silahkan ketik /help"
keyword = "Gunakan kata kunci berikut untuk mendapatkan informasi seputar virus corona:\n\n/data - Data jumlah kasus COVID-19\n\
/data(spasi)nama_negara - Data kasus berdasarkan negara tertentu\n\
/today - Jumlah kasus COVID-19 hari ini\n/hotline - Hotline COVID-19\n/info - Informasi penting seputar COVID-19\n/tips - Tips singkat\n\
/hoax - Kumpulan berita terkait hoax virus corona\n/news - Headline berita tentang COVID-19\n/help - Bantuan"
frame = """{"type": "carousel", "contents": []}"""

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
# Output are string
def group(number):
    s = '%d' % number
    groups = []
    while s and s[-1].isdigit():
        groups.append(s[-3:])
        s = s[:-3]
    return s + ','.join(reversed(groups))

@handler.add(JoinEvent)
def handle_join(event):
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=greetings))

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg_from_user = event.message.text.split()
    
    if msg_from_user[0].lower() == '/help':
        message = TextSendMessage(text=keyword)
        line_bot_api.reply_message(event.reply_token, message)

    elif msg_from_user[0].lower() == "/fact":
        response = requests.get('https://cat-fact.herokuapp.com/facts')
        kucing = json.loads(response.text)
        i = randint(0, 200) 
        fact = kucing['all'][i]['text']
        message = TextSendMessage(fact)
        line_bot_api.reply_message(event.reply_token, message)

    elif msg_from_user[0].lower() == '/data':
        #add Country
        try:
            if len(msg_from_user) > 1:
                param = msg_from_user[1]
                print(param)
                response = requests.get('https://corona.lmao.ninja/countries/'+param)
                data = json.loads(response.text)
                country = data['country']
                cases = group(data['cases'])
                deaths = group(data['deaths'])
                recovered = group(data['recovered'])
                today_cases = group(data['todayCases'])
                today_deaths = group(data['todayDeaths'])
                critical = group(data['critical'])
                res = """%s\nPositif: %s\nMeninggal: %s\nSembuh: %s\nKasus hari ini: %s
Meninggal hari ini: %s\nKritis: %s""" %(country, cases, deaths, recovered, today_cases, today_deaths, critical)
                print(res)
                message = TextSendMessage(text=res)
                line_bot_api.reply_message(event.reply_token, message)
            else:
                region, death, confirm, recover, rate = [], [], [], [], []
                response = requests.get('https://corona.lmao.ninja/countries/')
                data = json.loads(response.text)
                for i in range(len(data)):
                    region.append(data[i]['country'])
                    confirm.append(group(data[i]['cases']))
                    death.append(group(data[i]['deaths']))
                    recover.append(group(data[i]['recovered']))
                    if data[i]['country'] == "Indonesia": id = i
                    try:
                        res = int(data[i]['deaths'])/int(data[i]['cases'])*100
                        rate.append(str(round(res, 2)))
                    except Exception as e:
                        rate.append(0)
                response = requests.get('https://corona.lmao.ninja/all/')
                all_ = json.loads(response.text)
                total = "Total positif: " + group(all_['cases']) + chr(0x10007B)+"\nTotal meninggal: " + group(all_['deaths']) + chr(0x10007C)+ \
                "\nTotal sembuh: " + group(all_['recovered']) + chr(0x10007A)

                carousel = open("carousel_template.json", "r").read()

                bubble_string = carousel

                dictionary = json.loads(bubble_string)
                item = dictionary['contents'][0]['body']['contents'][4]['contents']
                item2 = dictionary['contents'][1]['body']['contents'][4]['contents']

                # Insert data
                # Dictionary index based on json file
                for i in range(len(item)):
                    if i == 15:
                        item[i]['contents'][0]['text'] = item2[i]['contents'][0]['text'] = region[id]
                        item[i]['contents'][2]['text'] = confirm[id]
                        item[i]['contents'][4]['text'] = death[id]
                        item2[i]['contents'][2]['text'] = recover[id]
                        item2[i]['contents'][4]['text'] = rate[id]
                        break

                    item[i]['contents'][0]['text'] = item2[i]['contents'][0]['text'] = region[i]
                    item[i]['contents'][2]['text'] = confirm[i]
                    item[i]['contents'][4]['text'] = death[i]
                    item2[i]['contents'][2]['text'] = recover[i]
                    item2[i]['contents'][4]['text'] = rate[i]

                # Convert dictionary to json
                bubble_string = json.dumps(dictionary)
                message = [FlexSendMessage(alt_text="Flex Message", contents=json.loads(bubble_string)), TextSendMessage(text=total)]
                line_bot_api.reply_message(event.reply_token, message)
        except Exception as e:
            print(e)
            message = TextSendMessage(text="Data tidak ada/tidak dapat dimuat")
            line_bot_api.reply_message(event.reply_token, message)

    elif msg_from_user[0].lower() == '/news':
        url = ('http://newsapi.org/v2/top-headlines?country=id&q=virus corona&apiKey='+news_api_key)
        response = requests.get(url)
        results = json.loads(response.text)

        title = []
        source = []
        desc = []
        author = []
        url = []
        urlToImage = []

        news = len(results['articles'])
        if news > 5:
            news = 5

        for i in range(news):
            title.append(results['articles'][i]['title'])
            source.append(results['articles'][i]['source']['name'])
            desc.append(results['articles'][i]['description'])
            author.append(results['articles'][i]['author'])
            url.append(results['articles'][i]['url'])
            urlToImage.append(results['articles'][i]['urlToImage'])

        zipped = list(zip(title, desc, source, author, url, urlToImage))

        # Flex message dynamic json
        # ==========================================================================================
        flex =   """{"type": "bubble", "hero": {"type": "image", "url": "https://awsimages.detik.net.id/api/wm/2020/03/20/ebcede5d-4b8c-4d75-8f96-29be8e617aab_169.jpeg?wid=54&w=650&v=1&t=jpeg", "size": "full", "aspectMode": "cover", "aspectRatio": "16:9"}, "body": {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "JUDUL BERITA", "weight": "bold", "size": "lg", "wrap": true }, {"type": "text", "text": "lorem ipsum dolor sit amet", "wrap": true, "size": "sm", "style": "normal", "weight": "regular"}, {"type": "box", "layout": "vertical", "margin": "lg", "spacing": "sm", "contents": [{"type": "box", "layout": "baseline", "spacing": "sm", "contents": [{"type": "text", "text": "Penulis", "color": "#aaaaaa", "size": "sm", "flex": 2 }, {"type": "text", "text": "Author Name", "wrap": true, "color": "#666666", "size": "sm", "flex": 7 } ] }, {"type": "box", "layout": "baseline", "spacing": "sm", "contents": [{"type": "text", "text": "Sumber", "color": "#aaaaaa", "size": "sm", "flex": 2 }, {"type": "text", "text": "example.com", "wrap": true, "color": "#666666", "size": "sm", "flex": 7 } ] } ] } ] }, "footer": {"type": "box", "layout": "vertical", "spacing": "sm", "contents": [{"type": "button", "style": "link", "height": "sm", "action": {"type": "uri", "label": "Buka Tautan", "uri": "https://example.com"}, "color": "#fafafa"}, {"type": "spacer", "size": "sm"} ], "flex": 0, "backgroundColor": "#c0392b"} }"""
        results = ""
        for i in range(news):
            results += flex
            if i < news-1:
                results += ","

        carousel = frame[0:-2] + results + frame[-2:]
        dictionary = json.loads(carousel)
        item = dictionary['contents']
        # ==========================================================================================

        # Add title, desc, source, author, url, urlImage
        for i in range(news):
            item[i]['body']['contents'][0]['text'] = zipped[i][0]
            item[i]['body']['contents'][1]['text'] = zipped[i][1]
            item[i]['body']['contents'][2]['contents'][1]['contents'][1]['text'] = zipped[i][2]
            item[i]['body']['contents'][2]['contents'][0]['contents'][1]['text'] = str(zipped[i][3])
            item[i]['footer']['contents'][0]['action']['uri'] = zipped[i][4]
            item[i]['hero']['url'] = zipped[i][5]

        bubble_string = json.dumps(dictionary)
        message = FlexSendMessage(alt_text="Flex Message", contents=json.loads(bubble_string))
        line_bot_api.reply_message(event.reply_token, message)

    elif msg_from_user[0].lower() == '/hotline':
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

    elif msg_from_user[0].lower() == '/info':
        url1 = 'https://www.unicef.org/indonesia/id/coronavirus'
        url2 = 'https://www.kompas.com/tren/read/2020/03/03/183500265/infografik-daftar-100-rumah-sakit-rujukan-penanganan-virus-corona'
        url3 = 'https://infeksiemerging.kemkes.go.id/'
        url4 = 'https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public'

        link = "Informasi penting yang perlu anda diketahui seputar Coronavirus dapat ditemukan pada tautan yang tersedia dibawah:\n\n[1] %s\n[2] %s\n[3] %s\n[4] %s" % (url1, url2, url3, url4)

        message = TextSendMessage(text=link)
        line_bot_api.reply_message(event.reply_token, message)

    elif msg_from_user[0].lower() == '/tips':
        tips = "Jangan lupa mencuci tangan dengan sabun hingga bersih setelah beraktivitas di luar rumah."
        message = TextSendMessage(text=tips)
        line_bot_api.reply_message(event.reply_token, message)

    elif msg_from_user[0].lower() == '/hoax':
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
                        action=URIAction(label='Tautan Kominfo', uri='https://kominfo.go.id/content/all/virus_corona'),
                    ),
                    ButtonComponent(
                        style='secondary',
                        height='sm',
                        size='md',
                        action=URIAction(label='Tautan TurnBackHoax', uri='https://turnbackhoax.id/2020/02/06/kompilasi-post-periksa-fakta-mafindo-berkaitan-dengan-virus-corona/'),
                    )
                ]
            ),
        )
        message = FlexSendMessage(alt_text="Kumpulan Hoax Virus Corona", contents=bubble)
        line_bot_api.reply_message(event.reply_token,message)

    elif msg_from_user[0].lower() == '/today':
        region, today_cases, today_deaths, rate = [], [], [], []

        try:
            response = requests.get('https://corona.lmao.ninja/countries')
            data = json.loads(response.text)
            for i in range(len(data)):
                region.append(data[i]['country'])
                today_cases.append(data[i]['todayCases'])
                today_deaths.append(data[i]['todayDeaths'])
                try:
                    res = int(data[i]['todayDeaths'])/int(data[i]['todayCases'])*100
                    rate.append(str(round(res, 2)))
                except Exception as e:
                    rate.append(0)

            zipped = list(zip(today_cases, today_deaths, region, rate))
            zipped.sort(reverse=True)

            var = """{"type": "bubble", "size": "giga", "body": {"type": "box", "layout": "vertical", "contents": []} }"""
            header = """{"type": "text", "text": "Data COVID-19 Hari Ini", "weight": "bold", "wrap": true, "align": "center", "color": "#0a0a0a", "margin": "md"}, {"type": "separator"},{"type": "box", "layout": "horizontal", "contents": [{"type": "text", "text": "Negara", "weight": "bold", "margin": "xs", "color": "#0a0a0a", "size": "xs", "flex": 6, "gravity": "center", "align": "center"}, {"type": "separator"}, {"type": "text", "text": "Jumlah Positif", "weight": "bold", "margin": "xs", "color": "#0a0a0a", "size": "xs", "flex": 5, "gravity": "center", "wrap": true, "align": "center"}, {"type": "separator"}, {"type" : "text", "text" : "Jumlah Meninggal", "weight" : "bold", "margin" : "xs", "color" : "#0a0a0a", "size" : "xs", "flex" : 5, "gravity" : "center", "wrap": true, "align" : "center"}, {"type" : "separator"}, {"type" : "text", "text" : "% Meninggal", "weight" : "bold", "margin" : "xs", "color" : "#0a0a0a", "size" : "xs", "flex" : 5, "gravity" : "center", "wrap": true, "align" : "center"} ] }, {"type": "separator"},"""
            box_item = """{"type": "box", "layout": "vertical", "margin": "none", "contents": []}"""
            item = """{"type": "box", "layout": "horizontal", "contents": [{"type": "text", "text": "region", "wrap": false, "color": "#0a0a0a", "margin": "xs", "size": "xs", "flex": 6 }, {"type": "separator"}, {"type": "text", "text": "positive", "align": "end", "wrap": false, "color": "#0a0a0a", "margin": "xs", "size": "xs", "flex": 5 }, {"type": "separator"}, {"type": "text", "text": "death", "align": "end", "wrap": false, "color": "#0a0a0a", "margin": "xs", "size": "xs", "flex": 5 } , {"type": "separator"}, {"type": "text", "text": "% death", "align": "end", "wrap": false, "color": "#0a0a0a", "margin": "xs", "size": "xs", "flex": 5 }]}"""
            items = ""
            run = len(zipped)
            for i in zipped:
                if i[0] == 0:
                    run-=1

            for i in range(run):
                items += item
                if i < run-1:
                    items += ','

            box_full = box_item[:-2] + items + box_item[-2:]
            results = frame[:-2] + var[:-4] + header + box_full + var[-4:] + frame[-2:]
            dictionary = json.loads(results)
            item = dictionary['contents'][0]['body']['contents'][4]['contents']
            # Insert data
            # Dictionary index based on json file
            for i in range(len(item)):
                item[i]['contents'][0]['text'] = zipped[i][2]
                item[i]['contents'][2]['text'] = group(zipped[i][0])
                item[i]['contents'][4]['text'] = group(zipped[i][1])
                item[i]['contents'][6]['text'] = zipped[i][3]

            total_cases = sum(today_cases)
            total_deaths = sum(today_deaths)
            # Convert dictionary to json
            total_all = "Total Positif: " + group(total_cases) + "\nTotal Meninggal: " + group(total_deaths)
            bubble_string = json.dumps(dictionary)
            message = [FlexSendMessage(alt_text="Flex Message", contents=json.loads(bubble_string)), TextSendMessage(text=total_all)]
        except Exception as e:
            print(e)
            message = TextSendMessage(text="Data tidak dapat dimuat, coba lagi nanti")
        line_bot_api.reply_message(event.reply_token, message)
    
    else:
        message = TextSendMessage(text="Kata kunci yang anda masukkan salah! Ketik /help untuk melihat bantuan")
        line_bot_api.reply_message(event.reply_token, message)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
