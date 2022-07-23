#이미지 처리, 텔레그램 입력에 필요한 라이브러리 불러오기
import cv2
import numpy as np
from datetime import datetime
from psutil import STATUS_LOCKED
import telegram
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import world_con_fig 
import requests as req
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
import time
import cv2
import numpy as np
import Adafruit_DHT as Sensor
from datetime import datetime
from ctypes import resize
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import config as cof


bot = telegram.Bot(world_con_fig.API_TOKEN)


font      = cv2.FONT_ITALIC
org       = (100,30)
fontScale = 1
fontColor = (255,255,255)
lineType  = 2
file_name = " "
Outpin = 17



print('ss')
# 카메라 캡션 장치 준비
a, b, c = None, None, None
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)      # 프레임 폭을 480으로 설정 
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 320)     # 프레임 높이를 320으로 설정

# b 프레임 읽기
print('cap')
thresh = 25    # 달라진 픽셀 값 기준치 설정
max_diff = 5   # 달라진 픽셀 갯수 기준치 설정

while cap.isOpened() or ret:
    print('while')
    with open('/home/pi/bj_projects/hwakin.txt', 'r') as myfile:
        go = myfile.read()
        myfile.close()
    
    if go == 'on':
        
        ret, a = cap.read()     # a 프레임 읽기
        ret, b = cap.read()     # b 프레임 읽기
        ret, c = cap.read()     # c 프레임 읽기
        draw = c.copy()         # 출력 영상에 사용할 복제본
        if not ret:
            break
        
        # 3개의 영상을 그레이 스케일로 변경
        a_gray = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY)
        b_gray = cv2.cvtColor(b, cv2.COLOR_BGR2GRAY)
        c_gray = cv2.cvtColor(c, cv2.COLOR_BGR2GRAY)
        # a-b, b-c 절대 값 차 구하기 
        diff1 = cv2.absdiff(a_gray, b_gray)
        diff2 = cv2.absdiff(b_gray, c_gray)
        # 스레시홀드로 기준치 이내의 차이는 무시
        ret, diff1_t = cv2.threshold(diff1, thresh, 255, cv2.THRESH_BINARY)
        ret, diff2_t = cv2.threshold(diff2, thresh, 255, cv2.THRESH_BINARY)
        # 두 차이에 대해서 AND 연산, 두 영상의 차이가 모두 발견된 경우
        diff = cv2.bitwise_and(diff1_t, diff2_t)
        # 열림 연산으로 노이즈 제거 ---①
        k = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))
        diff = cv2.morphologyEx(diff, cv2.MORPH_OPEN, k)
        # 차이가 발생한 픽셀이 갯수 판단 후 사각형 그리기
        diff_cnt = cv2.countNonZero(diff)
        
        #온도와 습도 구하기         
        try:
            Humi, Temp  = Sensor.read_retry(Sensor.DHT11, Outpin)
            sense = "{0:0.1f}%  {1:0.1f}*C".format(Humi, Temp)
        #센서가 꺼졌을시 에러 발생을 방지
        except(TypeError):
    
            sense = 'error!'
        
        if diff_cnt > max_diff:

            nzero = np.nonzero(diff)  # 0이 아닌 픽셀의 좌표 얻기(y[...], x[...])
            cv2.rectangle(draw, (min(nzero[1]), min(nzero[0])), \
                                (max(nzero[1]), max(nzero[0])), (0,255,0), 2)
            cv2.putText(draw, "detected", (10,30), \
                                cv2.FONT_HERSHEY_DUPLEX, 0.5, (0,0,255))

            stacked = np.hstack((draw, cv2.cvtColor(diff, cv2.COLOR_GRAY2BGR)))




            #출력용 이미지 준비
            dt_now = datetime.now()
            msg = datetime.now().strftime("%Y%m%d %H:%M")
            cv2.rectangle(draw, (480,310),(640, 360),(255,255,255),-1)
            cv2.putText(draw, str(msg), (500,350), font, 0.5, (0, 0, 0), 1)
            cv2.putText(draw, str(sense), (500, 330), font, 0.5, (0,0,255), 1)

            file_name = '{}.jpg'.format(dt_now.strftime('%Y%m%d%H%M%S'))
            cv2.imwrite('/home/pi/bj_projects/static/img/' + file_name, draw) # 사진 저장
            print("file_name:", file_name)
            bot.send_photo(chat_id = world_con_fig.BOT_CHAT_ID, photo=open("/home/pi/bj_projects/static/img/" + file_name, "rb"))

        
        # 다음 비교를 위해 영상 순서 정리
        a = b
        b = c
        time.sleep(0.5)
        cap.release()
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)      # 프레임 폭을 480으로 설정 
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 320)     # 프레임 높이를 320으로 설정

    #설정 변수가 꺼져있을시 무시
    elif go == 'off':
        
        pass

    #설정 변수이외의 입력이 들어왔을시 에러표시
    else:
        print('!!Error!!')
        break
