#!/usr/bin/python
import socket
import cv2
import numpy
import json


class DRONE_Client:
    def __init__(self, TCP_IP, TCP_PORT):
        # 소켓 생성 및 서버에 연결
        self.sock = socket.socket()
        self.sock.connect((TCP_IP, TCP_PORT))
        print('connecting')



    # 맵이 전체적으로 들어왔는지 확인하기
    def fullMapChecker(self, img):

        # 1st: 데모판 영역따기 - findcontour 처리해서 가장 큰 사각형 잡기  -> 기울어짐 제거 작업
        imgray = cv2.GaussianBlur(img, (5, 5), 0)
        imgray = cv2.cvtColor(imgray, cv2.COLOR_BGR2GRAY)
        canny = cv2.Canny(imgray, 100, 200)
        contours, hierarchy = cv2.findContours(canny, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        sorted_list = sorted(contours, key=lambda cc: len(cc))

        # 2nd: 기울어진 최대사각형 "sorted_list[-1]"의 면적을 토대로 적절한 맵이 들어왔나 확인 - 서버로 보낼지 판단
        maxHull = cv2.convexHull(sorted_list[-1])
        area = cv2.contourArea(maxHull)

        # image debugging
        cv2.drawContours(img, [maxHull], 0, (0, 1, 9), 2)
        cv2.imshow("map", img)
        print(area)
        cv2.waitKey(0)

        # 면적이 일정 비율 이상이면 True
        return True if area > 50000 else False



    def sendToServer(self, img, lct):

        # 1st: MQTT로 객체 위치 보내주기
        import paho.mqtt.client as mqtt
        obj_x, obj_y = lct[0], lct[1]  # 객체의 위치
        spot = "x{}y{}".format(obj_x, obj_y)
        mqtt = mqtt.Client("objectFinder")  # MQTT client 생성, 이름
        mqtt.connect('192.168.0.15', 1883)  # 로컬호스트에 있는 MQTT서버에 접속
        mqtt.publish("target_location", json.dumps({"data": spot}))  # topic 과 넘겨줄 값



        # 2st: 소켓통신 - 추출한 이미지를 String 형태로 변환(인코딩)
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        result, imgencode = cv2.imencode('.jpg', img, encode_param)
        data = numpy.array(imgencode)
        stringData = data.tostring()

        # 2st: 소켓통신 - String 형태로 변환한 이미지를 socket을 통해서 전송
        self.sock.send(str(len(stringData)).encode().ljust(16))
        self.sock.send(stringData)
        # self.sock.close()   # ...........혹시 이 부분에서 종료해서 끊어졌나..


    def sockClose(self):
        self.sock.close()