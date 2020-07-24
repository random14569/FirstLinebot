# -*- coding: utf-8 -*-

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import requests
import json
import random
import os
import psycopg2

app = Flask(__name__)

line_bot_api = LineBotApi('o46h+QEWQwDDrbd/Yc/qO+ZlfRQfAXBvXjogtyXPU9CtwHdmMv3YHOlG2Wna+l0/V3O8fYSMhuxQJBLLLz+EjXB8erMC6rieGlmH0SNRnZgJZS7ki2zn5M82Gy9/mPcy5glfAFY2ngmzA8pFvwb4/gdB04t89/1O/w1cDnyilFU=') #Channel access token (long-lived)
handler = WebhookHandler('3d586fbfcf410417126a0cf8ded39388') #channel secret
#google map api
google_map_api = 'google_map_api'

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    print("Request body: " + body, "Signature: " + signature)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(PostbackEvent)
def handle_postback(event):
    postBack=event.postback.data
    if postBack.find("餐廳") != -1:
        key_list = load_keyword()
        key = find_key(postBack, key_list)
	    #東區、西區非唯一行政區，要加縣市名
        if postBack.find("東區") != -1:
            key = 0
            address = "嘉義市東區"
        elif postBack.find("西區") != -1:
            key = 1
            address = "嘉義市西區"
        else:
            if key > -1 and key < 20:
                 address = postBack
        
	    #將address(文字)轉成座標值，使用geocode api
        addurl = 'https://maps.googleapis.com/maps/api/geocode/json?key={}&address={}&sensor=flase'.format(google_map_api,address)
        addressReq = requests.get(addurl)
        addressDoc = addressReq.json()
		
	    #取出座標
        lat = addressDoc['results'][0]['geometry']['location']['lat']
        lng = addressDoc['results'][0]['geometry']['location']['lng']

	    #搜尋附近的餐廳(20個)，使用place api
        foodStoreSearch = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?key={}&location={},{}&rankby=distance&type=restaurant&language=zh-TW".format(google_map_api,lat,lng)
        foodReq = requests.get(foodStoreSearch)
        nearby_restaurants_dict = foodReq.json()
        top20_restaurants = nearby_restaurants_dict["results"]
     
        bravo = restaurant_list(top20_restaurants, key)	
	    #隨機從bravo中選三個餐廳顯示(圖片/評分/地址)
        restaurant_random = random.sample(bravo,3)
        restaurant1 = restaurant_data(bravo,top20_restaurants,restaurant_random,0)
        restaurant2 = restaurant_data(bravo,top20_restaurants,restaurant_random,1)        
        restaurant3 = restaurant_data(bravo,top20_restaurants,restaurant_random,2)
		
	    #以輪播模板顯示
        Carousel_template = TemplateSendMessage(
        alt_text='附近餐廳',
        template=CarouselTemplate(
        columns=[
            CarouselColumn(
                thumbnail_image_url=restaurant1[1],
                title=restaurant1[0],
                text=restaurant1[2],
                actions=[
                    URITemplateAction(
                        label='查看地圖',
                        uri=restaurant1[3]
                    )
                ]
            ),
            CarouselColumn(
                thumbnail_image_url=restaurant2[1],
                title=restaurant2[0],
                text=restaurant2[2],
                actions=[
                    URITemplateAction(
                        label='查看地圖',
                        uri=restaurant2[3]
                    )
                ]
            ),
            CarouselColumn(
                thumbnail_image_url=restaurant3[1],
                title=restaurant3[0],
                text=restaurant3[2],
                actions=[
                    URITemplateAction(
                        label='查看地圖',
                        uri=restaurant3[3]
                    )
                ]
            )
        ]
        )
        )
        line_bot_api.reply_message(event.reply_token,Carousel_template)
		
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = postBack))

def restaurant_list(top20_restaurants, key):
    res_num = (len(top20_restaurants))
		
    bravo=[]
	#將20筆資料中評分超過3.9的存成bravo[]
    for i in range(res_num):
        try:
			#因google map資料有缺失，去除沒有評分的資料(colab執行top20_restaurants = nearby_restaurants_dict["results"][i]['rating']，報錯則為資料缺失)
            if key == 0 or key == 2 or key == 3 or key == 8 or key == 9 or key == 15 or key == 17 or key == 19:
                if top20_restaurants[i]['rating'] > 3.9:
                    print('rate: ',top20_restaurants[i]["rating"])
                    bravo.append(i)
            elif key == 1:
                if i != 11 and i != 12:
                    if top20_restaurants[i]['rating'] > 3.9:
                        print('rate: ',top20_restaurants[i]["rating"])
                        bravo.append(i)	
            elif key == 4:
                if i != 3:
                    if top20_restaurants[i]['rating'] > 3.9:
                        print('rate: ',top20_restaurants[i]["rating"])
                        bravo.append(i)
            elif key == 5:
                if i != 4 and i != 5:
                    if top20_restaurants[i]['rating'] > 3.9:
                        print('rate: ',top20_restaurants[i]["rating"])
                        bravo.append(i)
            elif key == 6:
                if i != 11 and i != 19:
                    if top20_restaurants[i]['rating'] > 3.9:
                        print('rate: ',top20_restaurants[i]["rating"])
                        bravo.append(i)
            elif key == 7:
                if i != 9 and i != 14:
                    if top20_restaurants[i]['rating'] > 3.9:
                        print('rate: ',top20_restaurants[i]["rating"])
                        bravo.append(i)
            elif key == 10:
                if i != 16 and i != 17:
                    if top20_restaurants[i]['rating'] > 3.9:
                        print('rate: ',top20_restaurants[i]["rating"])
                        bravo.append(i)
            elif key == 11:
                if i != 0:
                    if top20_restaurants[i]['rating'] > 3.9:
                        print('rate: ',top20_restaurants[i]["rating"])
                        bravo.append(i)
            elif key == 12:
                if i != 2 and i != 16 and i !=17:
                    if top20_restaurants[i]['rating'] > 3.9:
                        print('rate: ',top20_restaurants[i]["rating"])
                        bravo.append(i)
            elif key == 13:
                if i == 1 or i > 2 and i < 10:
                    if top20_restaurants[i]['rating'] > 3.9:
                        print('rate: ',top20_restaurants[i]["rating"])
                        bravo.append(i)
            elif key == 14:
                if i != 0 and i != 5:
                    if top20_restaurants[i]['rating'] > 3.9:
                        print('rate: ',top20_restaurants[i]["rating"])
                        bravo.append(i)
            elif key == 16:
                if i != 7 and i != 17 and i !=18:
                    if top20_restaurants[i]['rating'] > 3.9:
                        print('rate: ',top20_restaurants[i]["rating"])
                        bravo.append(i)
            elif key == 18:
                if i != 18:
                    if top20_restaurants[i]['rating'] > 3.9:
                        print('rate: ',top20_restaurants[i]["rating"])
                        bravo.append(i)
        except:
            keyError
    if len(bravo) < 0:
        content = "沒東西可吃"
	
    return bravo	

def restaurant_data(bravo,top20_restaurants,restaurant_random,index):
    restaurant = top20_restaurants[restaurant_random[index]]
    if restaurant.get("photos") is None:
        thumbnail_image_url = None	
    else:
        photo_reference = restaurant["photos"][0]["photo_reference"]
        photo_width = restaurant["photos"][0]["width"]
        thumbnail_image_url = "https://maps.googleapis.com/maps/api/place/photo?key={}&photoreference={}&maxwidth={}".format(google_map_api,photo_reference,photo_width)
    rating = "無" if restaurant.get("rating") is None else restaurant["rating"]
    address = "沒有資料" if restaurant.get("vicinity") is None else restaurant["vicinity"]
    details = "Google Map評分：{}\n地址：{}".format(rating,address)
		
	#以座標連接google map app
    map_url = "https://www.google.com/maps/search/?api=1&query={lat},{long}&query_place_id={place_id}".format(lat=restaurant["geometry"]["location"]["lat"],long=restaurant["geometry"]["location"]["lng"],place_id=restaurant["place_id"])
	
    return restaurant["name"], thumbnail_image_url, details, map_url	
    
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("Handle: reply_token: " + event.reply_token + ", message: " + event.message.text)
    context = event.message.text
    if context.find("里長") != -1:
        key_list = load_keyword()
        key = find_key(context, key_list)
        reply, rank = check_keyword(key, key_list)
        if key > -1 and key < 20:
            if context.find("東區") != -1:
                school_address = "嘉義市東區學校"
                hospital_address = "嘉義市東區醫院"
            elif context.find("西區") != -1:
                school_address = "嘉義市西區學校"
                hospital_address = "嘉義市西區醫院"
            else:
                school_address = key_list[key]+'學校'
                hospital_address = key_list[key]+'醫院'
			#以按鈕模板顯示
            buttons_template = TemplateSendMessage(
            alt_text='選單',
            template=ButtonsTemplate(
                    thumbnail_image_url=None,
					title=key_list[key],
                    text=rank,
                    actions=[
                        PostbackTemplateAction(
                            label='紅綠燈',
                            data = reply
                        ),
                        PostbackTemplateAction(
                            label='附近餐廳',
                            data = key_list[key]+'餐廳'
                        ),
                        URITemplateAction(
                            label='教育機構',
							test = key,
                            uri="https://www.google.com/maps/search/?api=1&query={}".format(school_address)					
                        ),
						URITemplateAction(
                            label='周遭醫院',
                            uri="https://www.google.com/maps/search/?api=1&query={}".format(hospital_address)					
                        ),
		            ]
		        )
	        )  
            line_bot_api.reply_message(event.reply_token,buttons_template)			
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = reply))

##建立keyword list，0-19是鄉鎮市，20-22是嘉義市、嘉義縣、嘉義，23-27分別是人口、教育、交通、治安、醫療
def load_keyword():
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode = 'require')
    cursor = conn.cursor()
    
    select_result = f"""select c."town_name" FROM "TownDescription" AS c;"""
    cursor.execute(select_result)
    raw = cursor.fetchmany(-1)
    
    keyword_list = []
    for i in raw:
        keyword_list.append(str(i[0]))
    keyword_list.append("嘉義市")
    keyword_list.append("嘉義縣")
    keyword_list.append("嘉義")
    
    keyword_list.append("人口")
    keyword_list.append("教育")
    keyword_list.append("交通")
    keyword_list.append("治安")
    keyword_list.append("醫療")
        
    cursor.close()
    conn.close()
    return keyword_list

def find_key(message, key_list):
    key = -1
    for i in range(len(key_list)):
        loc = message.find(key_list[i])
        if loc != -1:
            key = i
            break
    return key

def check_keyword(message, key_list):
    info = select_info(message, key_list)
    rank = info[-1]
    reply = prepare_message(info)
    return reply, rank
    
def select_info(keypoint, key_list):
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode = 'require')
    cursor = conn.cursor()
    reply = []
    
    if keypoint == -1:
        reply = ["你說什麼?阿伯我重聽!再說一次~"]
    elif keypoint < 20:
        reply = key_list[23:28]
        select_result = f"""select * FROM "TownDescription" WHERE "town_name" LIKE '"""+ str(key_list[keypoint])+ """';"""
        cursor.execute(select_result)
        raw = cursor.fetchmany(-1)
        select_result = f"""select * FROM "TownLightRank" WHERE "town_name" LIKE '"""+ str(key_list[keypoint])+ """';"""
        cursor.execute(select_result)
        raw_sec = cursor.fetchmany(-1)
        
        reply = prepare_reply(raw, raw_sec, key_list[23:28])

    elif keypoint == 20:
        reply = key_list[0:2]
    elif keypoint == 21:
        reply = key_list[2:20]
    elif keypoint == 22:
        reply = key_list[0:20]

    cursor.close()
    conn.close()
    
    return reply

def prepare_message(context_list):
    string = ""
    for i in range(len(context_list)):
        string = string + str(context_list[i])
        if i!= (len(context_list)-1):
            string = string + "\n"
    return string

def prepare_reply(description, light, keyword):
    message = []
    message.append(description[0][0])
    for i in range(len(keyword)):
        tmp = keyword[i] + "紅綠燈:" + light[0][i+1] + "燈," + description[0][i+1]
        message.append(str(tmp))
    tmp = "整個嘉義地區適合居住排名："+str(light[0][6])
    message.append(str(tmp))
    return message
    
@app.route("/") #"/"首頁根目錄的意思
def home():
    return "test"

@app.route("/test")
def test():
    return "test2"


if __name__ == "__main__":
    app.run()