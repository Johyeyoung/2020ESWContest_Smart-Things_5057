#!/usr/bin/python
# -*- encoding: utf-8 -*-
import socket
import threading
import cv2
import numpy
from MakeMap import *  # 맵 만들기
from Find_path import *  # 경로 만들기
from MongoDB import *
import paho.mqtt.client as mqtt
import warnings
from Find_person import *
import json
import sys
import time

warnings.simplefilter("ignore", DeprecationWarning)
#socket 수신 버퍼를 읽어서 반환하는 함수
def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

# .......... 0-2. mongoDB 객체 생성
mongo = MongoDB()

# .......... 0-1. 서버의 IP와 port 번호
# .......... 4-2. TurtleBot 에게 MQTT 로 경로 정보 넘기기
mqtt = mqtt.Client("loadFinder")  # MQTT client 생성, 이름 ""
mqtt.connect("localhost", 1883)  # 로컬호스트에 있는 MQTT서버에 접속

# .......... 1. TCP 소켓 열고 수신 대기
TCP_IP = '192.168.0.15'
TCP_PORT = int(sys.argv[1])
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(True)
print("###############################################################################")
print("############################# SERVER is waiting ###############################")
print("###############################################################################")

conn, addr = s.accept()
postLocation = [0, 0]
map_flag = True # 전체 구역과 관련해 미리 맵을 만든다
map = None



while True:
    # .......... 2. DRONE Client 접속 성공 & data 받기
    length = recvall(conn, 16)
    stringData = recvall(conn, int(length))
    # ....... 발견된 객체의 위치 x{}:y{} 도출
    location = stringData.split(b'\n\b\n\b')[-1].decode()
    location = [int(i) for i in location.split(":")]
    #........ 이미지 데이터
    data = numpy.fromstring(stringData, dtype='uint8')
    decimg = cv2.imdecode(data, 1)

    print("____________________________  SERVER GET DATA  ________________________________\n\n")

    # .......... 2-1. debugging 이미지 확인하기
    #cv2.imshow('SERVER', decimg)
    #cv2.waitKey(0)


    # 맵을 먼저 만든다
    if map_flag:
        time.sleep(2)
        makeMap = Make_Map(decimg)
        makeMap.get_Max_contour()
        makeMap.delete_destroy()
        map = makeMap.draw_result_map()
        map_flag = False


    # .......... 3. 이미지(origin.jpg)를 mongoDB에 저장
    mongo.storeImg_map(decimg, 'map_origin.jpg')
    print("\n\n\n                            DRONE image saved!!")

    # .......... 4. 길찾기 시작

    print("________________________  경로 탐색 모드가 실행됩니다.  ________________________")
    print("                                     ▼\n\n")
    #print("                                     ▼")
    #print("                                     ▼\n\n")
    time.sleep(2)
    if location[0]//10 != postLocation[0]//10 and location[1]//10 != postLocation[1]//10:
        find_path = Find_path(decimg, location, map)
        find_path.path_algorithm(postLocation)
        postLocation = location  # 과거의 목적지는 터틀봇의  다음 시작점이 되기에 기록
        img, path_data = find_path.drawing_path()  # 경로가 그려진 맵과 경로 데이터 반환
        mqtt.publish("pathList", json.dumps({"data": path_data}))  # topic 과 넘겨줄 값


        # .......... 4-1. 경로 맵(map_result.jpg)을 mongoDB에 저장하기
        mongo.storeImg_map(img, 'map_result.jpg')
        print("\n\n                            map_result image saved!! ")


    else:
        print("\n\n\n___________________________________________________________________________")
        print("           이미 탐색한 경로입니다. 감시를 종료합니다.           ")
        print("___________________________________________________________________________")

        break

    # .......... 6. Read Turtlebot wabCam and find person
    time.sleep(2)
    print("_________________________  터틀봇이 주행을 시작합니다. _________________________")
    print("                                       ▼\n\n")

    find_person = Find_person()
    result = find_person.check_person()
    if result == True:
        conn.send('DRONE_close'.encode('utf-8'))
        print("\n\n\n_________________________________________________________________________")
        print('                 DRONE 감시 모드를 종료합니다.')
        print("_________________________________________________________________________\n")

        break
    else:
        # 다시 추적을 위해 드론소켓으로 작동하라는 명령을 내린다
        conn.send('DRONE_again'.encode('utf-8'))
        print("\n\n\n__________________________________________________________________________")
        print('                   DRONE 이미지를 요청합니다.')
        print("______________________________________________________________________________\n")
