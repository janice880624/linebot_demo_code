import os
import json, requests
from datetime import datetime

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

app = Flask(__name__)
# LINE BOT info
line_bot_api = LineBotApi(os.environ.get("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("CHANNEL_SECRET"))

@app.route("/", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    print(body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

cities = ['基隆市','嘉義市','臺北市','嘉義縣','新北市','臺南市','桃園縣','高雄市','新竹市','屏東縣','新竹縣','臺東縣','苗栗縣','花蓮縣','臺中市','宜蘭縣','彰化縣','澎湖縣','南投縣','金門縣','雲林縣','連江縣']

def get2(city):
    token = 'CWB-779E078C-5DF0-43F6-B526-FADAD3641C02'
    url = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=' + token + '&format=JSON&locationName=' + str(city)
    Data = requests.get(url)
    Data = (json.loads(Data.text))['records']['location'][0]['weatherElement']
    res = [[] , [] , []]
    for j in range(3):
        for i in Data:
            res[j].append(i['time'][j])
    return res

# Message event
@handler.add(MessageEvent)
def handle_message(event):
    message_type = event.message.type
    user_id = event.source.user_id
    reply_token = event.reply_token
    message = event.message.text
    if(message[:2] == '天氣'):
        city = message[3:]
        city = city.replace('台','臺')
        if(not (city in cities)):
            line_bot_api.reply_message(reply_token, TextSendMessage(text="查詢格式為: 天氣 縣市"))
        else:
            res = get2('臺北市')

            token = 'api_token'
            url = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=' + token + '&format=JSON&locationName=' + str(city)
            Data = requests.get(url)
            Data = (json.loads(Data.text))['records']['location'][0]['weatherElement']
            res = [[] , [] , []]
            for j in range(3):
                for i in Data:
                    res[j].append(i['time'][j])

            reply_text1 = "{} ~ {}\n天氣狀況 {}\n溫度 {} ~ {} °C\n降雨機率 {}".format(res[1][0]['startTime'][5:-3], res[1][0]['endTime'][5:-3], res[0][0]['parameter']['parameterName'], res[0][2]['parameter']['parameterName'], res[0][4]['parameter']['parameterName'], res[0][1]['parameter']['parameterName'])
            
            line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_text1))
    else:
        line_bot_api.reply_message(reply_token, TextSendMessage(text='你傳錯訊息囉'))
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port)
