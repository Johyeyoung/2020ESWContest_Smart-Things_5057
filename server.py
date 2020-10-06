import socket
import threading
import cv2
import numpy
from MakeMap import *  # 맵 만들기
from Find_path import *  # 경로 만들기
from MongoDB import *
import paho.mqtt.client as mqtt
import warnings
import Find_person
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
print("#####################################")
print("######### SERVER is waiting #########")
print("#####################################")

conn, addr = s.accept()
postLocation = [0, 0]
map_flag = True # 전체 구역과 관련해 미리 맵을 만든다
map = None



while True:
    # .......... 2. Client 접속 성공 & data 받기
    length = recvall(conn, 16)
    stringData = recvall(conn, int(length))
    location = stringData.split(b'\n\b\n\b')[-1].decode()  # x{}:y{}
    location = [int(i) for i in location.split(":")]
    print("터틀봇의 위치: ", postLocation)
    print("침입자의 위치: ", location)
    data = numpy.fromstring(stringData, dtype='uint8')
    #s.close()
    decimg = cv2.imdecode(data, 1)
    print("_________ SERVER get Data _________")

    # .......... 2-1. debugging 이미지 확인하기
    #cv2.imshow('SERVER', decimg)
    #cv2.waitKey(0)


    # 맵을 먼저 만든다
    if map_flag:
        makeMap = Realize(decimg)
        makeMap.contour()
        makeMap.delete_destroy()
        map = makeMap.draw_result_map()
        map_flag = False


    # .......... 3. 이미지(origin.jpg)를 mongoDB에 저장
    cv2.imwrite('./container/origin.jpg', decimg)
    img = open('./container/origin.jpg', 'rb')
    mongo.storeImg_map(img, 'map_origin.jpg')
    print("____________Drone image saved!!____________")


    # .......... 4. 길찾기 시작
    print("____________경로 탐색 모드가 실행됩니다._____________")

    if location[0]//10 != postLocation[0]//10 and location[1]//10 != postLocation[1]//10:
        find_path = Find_path(decimg, location, map)
        find_path.path_algorithm(postLocation)
        postLocation = location
        img, pos = find_path.real_path()
        mqtt.publish("pathList", json.dumps({"data": pos}))  # topic 과 넘겨줄 값


        # .......... 4-1. 경로 맵(map_result.jpg)을 mongoDB에 저장하기
        cv2.imwrite('./container/map_result.jpg', img)
        img = open('./container/map_result.jpg', 'rb')
        mongo.storeImg_map(img, 'map_result.jpg')
        print("____________map_result image saved!!____________")

    else:
        print("이미 경로를 탐색했습니다")
        break

    # .......... 6. Read Turtlebot wabCam and find person
    print("____________객체 추적 모드가 실행됩니다._____________")
    result = Find_person.check_person()
    if result == True:
        conn.send('DRONE_close'.encode('utf-8'))
        print('DRone_close')
        break
    else:
        # 다시 추적을 위해 드론소켓으로 작동하라는 명령을 내린다
        conn.send('DRONE_again'.encode('utf-8'))
        print('DRone_again')