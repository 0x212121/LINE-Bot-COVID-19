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
import re
import config as conf

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi(conf.access_token)
# Channel Secret
handler = WebhookHandler(conf.token_secret)
news_api_key = (conf.news_key)

greetings = "Terima kasih telah menambahkan kami ke dalam grup " + chr(0x10008D) + "\nUntuk petunjuk penggunaan silahkan pilih help pada menu yang tersedia"
keyword = """Gunakan kata kunci berikut untuk mendapatkan informasi seputar virus corona:
\n/data - Data jumlah kasus Covid-19
/data(spasi)nama_negara - Data kasus berdasarkan negara tertentu
/today - Jumlah kasus Covid-19 hari ini
/hotline - Hotline Covid-19
/info - Informasi penting seputar Covid-19
/tips - Tips singkat
/hoax - Tautan berita terkait hoax Covid-19
/news - Headline berita tentang Covid-19
/istilah - Infografis istilah dalam Covid-19
/help - Bantuan"""
frame = """{"type": "carousel", "contents": []}"""

# Rich Menu
rich_menu_to_create = RichMenu(
    size=RichMenuSize(width=800, height=540),
    selected=False,
    name="Nice richmenu",
    chat_bar_text="Menu",
    areas=[
        RichMenuArea(bounds=RichMenuBounds(x=0, y=0, width=265, height=270),
        action=MessageAction(label="Berita", text="/data")),
        RichMenuArea(bounds=RichMenuBounds(x=270, y=0, width=265, height=270),
        action=MessageAction(label="HOAX", text="/today")),
        RichMenuArea(bounds=RichMenuBounds(x=536, y=0, width=265, height=270),
        action=MessageAction(label="Bantuan", text="/hotline")),
        RichMenuArea(RichMenuBounds(x=0, y=270, width=265, height=270),
        action=MessageAction(label="Data Global", text="/news")),
        RichMenuArea(bounds=RichMenuBounds(x=270, y=270, width=265, height=270),
        action=MessageAction(label="Data Hari ini", text="/hoax")),
        RichMenuArea(bounds=RichMenuBounds(x=536, y=270, width=265, height=270),
        action=MessageAction(label="Hotline", text="/help"))
        ]
)
# MessageAction, PostbackAction, UriAction Example
# PostbackAction(
#     label='postback',
#     display_text='postback text',
#     data='action=buy&itemid=1'
# ),
# MessageAction(
#     label='message',
#     text='message text'
# ),
# URIAction(
#     label='uri',
#     uri='http://example.com/'
# )

rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)
print("rich menu id:" + rich_menu_id)
with open('img/menu_bot.png', 'rb') as f:
    line_bot_api.set_rich_menu_image(rich_menu_id, "image/png", f)
line_bot_api.set_default_rich_menu(rich_menu_id)

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
                response = requests.get('https://corona.lmao.ninja/countries/'+param)
                data = json.loads(response.text)
                flag = data['countryInfo']['flag']
                country = data['country']
                cases = group(data['cases'])
                deaths = group(data['deaths'])
                recovered = group(data['recovered'])
                today_cases = group(data['todayCases'])
                today_deaths = group(data['todayDeaths'])
                critical = group(data['critical'])

                rate = int(data['deaths'])/int(data['cases'])*100
                mortality_rate = str(round(rate,2)) + "%"

                bubble_string = open("country_case.json", "r").read()
                dictionary = json.loads(bubble_string)
                dictionary['hero']['url'] = flag
                dictionary['body']['contents'][0]['text'] = country
                dictionary['body']['contents'][1]['contents'][1]['text'] = mortality_rate
                dictionary['body']['contents'][2]['contents'][0]['contents'][1]['text'] = cases
                dictionary['body']['contents'][2]['contents'][1]['contents'][1]['text'] = recovered
                dictionary['body']['contents'][2]['contents'][2]['contents'][1]['text'] = deaths
                dictionary['body']['contents'][2]['contents'][3]['contents'][1]['text'] = today_cases
                dictionary['body']['contents'][2]['contents'][4]['contents'][1]['text'] = today_deaths
                dictionary['body']['contents'][2]['contents'][5]['contents'][1]['text'] = critical

                bubble_string = json.dumps(dictionary)
                message = FlexSendMessage(alt_text="Flex Message", contents=json.loads(bubble_string))
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
                    try:
                        res = int(data[i]['deaths'])/int(data[i]['cases'])*100
                        rate.append(str(round(res, 2)))
                    except Exception as e:
                        rate.append(0)
                response = requests.get('https://corona.lmao.ninja/all/')
                all_ = json.loads(response.text)
                total = "Total positif: " + group(all_['cases']) +"\nTotal meninggal: " + group(all_['deaths']) + \
                "\nTotal sembuh: " + group(all_['recovered'])

                carousel = open("carousel_template.json", "r").read()

                bubble_string = carousel

                dictionary = json.loads(bubble_string)
                item = dictionary['contents'][0]['body']['contents'][4]['contents']
                item2 = dictionary['contents'][1]['body']['contents'][4]['contents']

                # Insert data
                # Dictionary index based on json file
                for i in range(len(item)):
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
        try:
            url = ('http://newsapi.org/v2/top-headlines?country=id&q=virus corona&apiKey='+news_api_key)
            response = requests.get(url)
            results = json.loads(response.text)
            titles = []
            sources = []
            descs = []
            authors = []
            urls = []
            urlsToImage = []

            news = len(results['articles'])
            news = 5 if news > 5 else news

            for i in range(news):
                titles.append(results['articles'][i]['title'])
                sources.append(results['articles'][i]['source']['name'])
                descs.append(results['articles'][i]['description'])
                authors.append(results['articles'][i]['author'])
                urls.append(results['articles'][i]['url'])
                urlsToImage.append(results['articles'][i]['urlToImage'])

            zipped = list(zip(titles, descs, sources, authors, urls, urlsToImage))

            # Flex message dynamic json
            # ==========================================================================================
            flex = """{"type": "bubble", "hero": {"type": "image", "url": "url_image", "size": "full", "aspectMode": "cover", "aspectRatio": "16:9"}, "body": {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "JUDUL BERITA", "weight": "bold", "size": "md", "wrap": true }, {"type": "text", "text": "lorem ipsum dolor sit amet", "wrap": true, "size": "sm", "style": "normal", "weight": "regular"}, {"type": "box", "layout": "vertical", "margin": "lg", "spacing": "sm", "contents": [{"type": "box", "layout": "baseline", "spacing": "sm", "contents": [{"type": "text", "text": "Penulis", "color": "#aaaaaa", "size": "sm", "flex": 2 }, {"type": "text", "text": "Author Name", "wrap": true, "color": "#666666", "size": "sm", "flex": 7 } ] }, {"type": "box", "layout": "baseline", "spacing": "sm", "contents": [{"type": "text", "text": "Sumber", "color": "#aaaaaa", "size": "sm", "flex": 2 }, {"type": "text", "text": "example.com", "wrap": true, "color": "#666666", "size": "sm", "flex": 7 } ] } ] } ] }, "footer": {"type": "box", "layout": "vertical", "spacing": "sm", "contents": [{"type": "button", "style": "link", "height": "sm", "action": {"type": "uri", "label": "Buka Tautan", "uri": "https://example.com"}, "color": "#fafafa"}, {"type": "spacer", "size": "sm"} ], "flex": 0, "backgroundColor": "#c0392b"} }"""
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
                news_title = re.split("\s-\s", zipped[i][0])
                item[i]['body']['contents'][0]['text'] = news_title[0]
                item[i]['body']['contents'][1]['text'] = zipped[i][1]
                item[i]['body']['contents'][2]['contents'][1]['contents'][1]['text'] = zipped[i][2]
                item[i]['body']['contents'][2]['contents'][0]['contents'][1]['text'] = zipped[i][3]
                # LINE's thumbnails only eat https, not eat http!
                item[i]['footer']['contents'][0]['action']['uri'] = zipped[i][4]
                item[i]['hero']['url'] = zipped[i][5]

            bubble_string = json.dumps(dictionary)
            dict_replace = {'http://' : '"https://"', 'null' : '"-"'}
            
            for i, j in dict_replace.items():
                bubble_string = bubble_string.replace(i, j)

            message = FlexSendMessage(alt_text="Flex Message", contents=json.loads(bubble_string))
        except Exception as e:
            message = e
            line_bot_api.reply_message(event.reply_token, message)
            # raise e
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
            size='kilo',
            hero=ImageComponent(
                url='https://www.mafindo.or.id/wp-content/uploads/2017/10/logo-turn-back-hoax-300x300.png',
                size='full',
                aspect_ratio='2:1',
                aspect_mode='fit'
            ),
            body=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text='Kumpulan HOAX terkait Covid-19', weight='bold', size='md', align='center', wrap=True)
                ],
            ),
            footer=BoxComponent(
                layout='vertical',
                spacing='sm',
                margin='xs',
                contents=[
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
        message = FlexSendMessage(alt_text="HOAX Covid-19", contents=bubble)
        line_bot_api.reply_message(event.reply_token,message)

    elif msg_from_user[0].lower() == '/today':
        region = [] 
        today_cases = []
        today_deaths = []
        try:
            response = requests.get('https://corona.lmao.ninja/countries')
            data = json.loads(response.text)
            for i in range(len(data)):
                region.append(data[i]['country'])
                today_cases.append(data[i]['todayCases'])
                today_deaths.append(data[i]['todayDeaths'])

            zipped = list(zip(today_cases, today_deaths, region))
            zipped.sort(reverse=True)

            var = """{"type": "bubble", "body": {"type": "box", "layout": "vertical", "contents": []} }"""
            header = """{"type": "text", "text": "Data COVID-19 Hari Ini", "weight": "bold", "wrap": true, "align": "center", "color": "#0a0a0a", "margin": "md"}, {"type": "separator"},{"type": "box", "layout": "horizontal", "contents": [{"type": "text", "text": "Negara", "weight": "bold", "margin": "xs", "color": "#0a0a0a", "size": "xs", "flex": 6, "gravity": "center", "align": "center"}, {"type": "separator"}, {"type": "text", "text": "Jumlah Positif", "weight": "bold", "margin": "xs", "color": "#0a0a0a", "size": "xs", "flex": 5, "gravity": "center", "wrap": true, "align": "center"}, {"type": "separator"}, {"type" : "text", "text" : "Jumlah Meninggal", "weight" : "bold", "margin" : "xs", "color" : "#0a0a0a", "size" : "xs", "flex" : 5, "gravity" : "center", "wrap": true, "align" : "center"}] }, {"type": "separator"},"""
            box_item = """{"type": "box", "layout": "vertical", "margin": "none", "contents": []}"""
            item = """{"type": "box", "layout": "horizontal", "contents": [{"type": "text", "text": "region", "wrap": false, "color": "#0a0a0a", "margin": "xs", "size": "xs", "flex": 6 }, {"type": "separator"}, {"type": "text", "text": "positive", "align": "end", "wrap": false, "color": "#0a0a0a", "margin": "xs", "size": "xs", "flex": 5 }, {"type": "separator"}, {"type": "text", "text": "???", "align": "end", "wrap": false, "color": "#0a0a0a", "margin": "xs", "size": "xs", "flex": 5 }]}"""
            items = ""
            loop = len(zipped)
            for i in zipped:
                if i[0] == 0:
                    loop-=1
            
            loop = 25 if loop > 25 else loop
            for i in range(loop):
                items += item
                if i < loop-1:
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

            total_cases = sum(today_cases)
            total_deaths = sum(today_deaths)
            # Convert dictionary to json
            total_all = "Total Positif: " + group(total_cases) + "\nTotal Meninggal: " + group(total_deaths)
            bubble_string = json.dumps(dictionary)
            message = [FlexSendMessage(alt_text="Flex Message", contents=json.loads(bubble_string)), TextSendMessage(text=total_all)]
        except Exception as e:
            print(e)
            message = TextSendMessage(text="Data tidak dapat dimuat, coba lagi nanti\nError Message: "+e)
        line_bot_api.reply_message(event.reply_token, message)
    
    elif msg_from_user[0].lower() == '/istilah':
        url = 'https://raw.githubusercontent.com/xstreamx/LINE-Bot-COVID-19/master/img/infographic.jpg'
        line_bot_api.reply_message(event.reply_token, ImageSendMessage(url, url))
        
    else:
        message = TextSendMessage(text="Kata kunci yang anda masukkan salah! Ketik /help untuk melihat bantuan")
        line_bot_api.reply_message(event.reply_token, message)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
