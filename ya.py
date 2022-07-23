from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import world_con_fig
import os
import telegram
import requests as req
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
import time
import cv2
import numpy as np
import Adafruit_DHT as Sensor
# from datetime import datetime
from datetime import datetime
from ctypes import resize
from telepot.loop import MessageLoop # 봇 구동


bot = telegram.Bot(world_con_fig.Tado_API_TOKEN)



font      = cv2.FONT_HERSHEY_SIMPLEX
org       = (100,30)
fontScale = 1
fontColor = (255,255,255)
lineType  = 2
file_name = " "
Outpin = 17


def hoho():    
    Humi, Temp  = Sensor.read_retry(Sensor.DHT11, Outpin)
    print ("Humidity = {0:0.1f}% Temp = {1:0.1f}*C".format(Humi, Temp))


    sense = "Humidity = {0:0.1f}% Temp = {1:0.1f}*C".format(Humi, Temp)
    cap = cv2.VideoCapture(0) 
    dt_now = datetime.now()
    ret, frame = cap.read() # 사진 촬영

    if ret == True:
        frame = cv2.flip(frame, 1) # 좌우 대칭
        msg = datetime.now().strftime("%Y%m%d %H:%M:%S.%f")
        cv2.putText(frame, str(msg), org, font, fontScale, (0, 0, 0), 1)
        cv2.putText(frame, str(sense), (50, 70), font, fontScale, (255,0,255), 1)
        file_name = '{}.jpg'.format(dt_now.strftime('%Y%m%d%H%M%S'))
        cv2.imwrite('/home/pi/bj_projects/static/img/' + file_name, frame) # 사진 저장
        print("file_name:", file_name)
        bot.send_photo(chat_id = world_con_fig.Tado_BOT_CHAT_ID, photo=open("/home/pi/bj_projects/static/img/" + file_name, "rb"))

        cap.release()
  



updater = Updater(world_con_fig.Tado_API_TOKEN, use_context=True)

def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def get_command(update, context) :
    print("get")
    show_list = []
    show_list.append(InlineKeyboardButton("cctv 테스트", callback_data="cctv 테스트")) # add on button
    show_list.append(InlineKeyboardButton("현재 cctv 상태 확인", callback_data="현재 cctv 상태 확인")) # add on button
    show_list.append(InlineKeyboardButton ("감시 시작", callback_data="감시 시작"))
    show_list.append(InlineKeyboardButton("감시 종료", callback_data="감시 종료"))
    show_list.append(InlineKeyboardButton("취소", callback_data="취소")) # add off button
    show_markup = InlineKeyboardMarkup(build_menu(show_list, len(show_list) - 1)) # make markup

    update.message.reply_text("원하는 값을 선택하세요", reply_markup=show_markup)

def callback_get(update, context):

    print("callback")
    context.bot.edit_message_text(text="{}이(가) 선택되었습니다".format(update.callback_query.data),
                                  chat_id=update.callback_query.message.chat_id,
                                  message_id=update.callback_query.message.message_id)
    if update.callback_query.data == 'cctv 테스트':
        hoho()
    if update.callback_query.data == '취소':
        pass

    if update.callback_query.data == '감시 시작':
        myfile = open('/home/pi/bj_projects/hwakin.txt','w')
        myfile.write('on')
        myfile.close()
    

    if update.callback_query.data == '감시 종료':
        myfile = open('/home/pi/bj_projects/hwakin.txt','w')
        myfile.write('off')    
        myfile.close()
        
    if update.callback_query.data == '현재 cctv 상태 확인':
        with open('/home/pi/bj_projects/hwakin.txt', 'r') as myfile:
            go = myfile.read()
            myfile.close()
        if go == 'on':
            bot.send_message(chat_id = world_con_fig.Tado_BOT_CHAT_ID, text = '자동감시모드 활성중')
        elif go == 'off':
            bot.send_message(chat_id = world_con_fig.Tado_BOT_CHAT_ID, text = '자동감시모드 비활성중')
            



get_handler = CommandHandler('on', get_command)
updater.dispatcher.add_handler(get_handler)
updater.dispatcher.add_handler(CallbackQueryHandler(callback_get))

updater.start_polling(timeout=1, drop_pending_updates=True)
updater.idle()