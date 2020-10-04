import socket
import cv2
import numpy
from Find_path import *
from MongoDB import *
import paho.mqtt.client as mqtt
import warnings
import Find_person
import json

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



# .......... 0-1. IP와 port 번호
TCP_IP = '192.168.35.121'
TCP_PORT = 5009
# .......... 0-2. mongoDB 객체 생성
mongo = MongoDB()

while True:

    # .......... 1. TCP 소켓 열고 수신 대기
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((TCP_IP, TCP_PORT))
    s.listen(True)
    print("_________ SERVER is waiting _________")



    # .......... 2. Client 접속 성공 & data 받기
    conn, addr = s.accept()
    length = recvall(conn, 16)
    stringData = recvall(conn, int(length))
    location = stringData.split(b'\n\b\n\b')[-1].decode()  # x{}:y{}
    location = list(map(int, location.split(":")))
    print("침입자의 위치: ", location)
    data = numpy.fromstring(stringData, dtype='uint8')
    s.close()
    decimg = cv2.imdecode(data, 1)
    print("_________ SERVER get Data _________")

    # .......... 2-1. debugging 이미지 확인하기
    #cv2.imshow('SERVER', decimg)
    #cv2.waitKey(0)



    # .......... 3. 이미지(origin.jpg)를 mongoDB에 저장
    cv2.imwrite('./container/origin.jpg', decimg)
    img = open('./container/origin.jpg', 'rb')
    mongo.storeImg_map(img, 'map_origin.jpg')
    print("____________Drone image saved!!____________")




    # .......... 4. 길찾기 시작
    print("____________경로 탐색 모드가 실행됩니다._____________")
    find_path = Find_path(decimg, location)
    find_path.path_algorithm()
    img, pos = find_path.real_path()

    # .......... 4-1. 경로 맵(map_result.jpg)을 mongoDB에 저장하기
    cv2.imwrite('./container/map_result.jpg', img)
    img = open('./container/map_result.jpg', 'rb')
    mongo.storeImg_map(img, '')
    print("____________map_result image saved!!____________")


    # .......... 4-2. TurtleBot 에게 MQTT 로 경로 정보 넘기기
    mqtt = mqtt.Client("loadFinder")  # MQTT client 생성, 이름 ""
    mqtt.connect("localhost", 1883)  # 로컬호스트에 있는 MQTT서버에 접속
    mqtt.publish("pathList", json.dumps({"data": pos}))  # topic 과 넘겨줄 값



    # .......... 6. Read Turtlebot wabCam and find person
    print("____________객체 추적 모드가 실행됩니다._____________")
    result = Find_person.check_person()
    result = False
    if result == True:
        break