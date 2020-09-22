import cv2
import numpy as np
import json
from mongoengine import connect, Document, fields
import paho.mqtt.client as mqtt
from MongoDB import *

mongo = MongoDB()


# 들어온 화면에서 yolo로 사람인지 확인하기
def isPerson(img):
    min_confidence = 0.5
    net = cv2.dnn.readNet("yolov4-tiny-custom_10000.weights", "yolov4-tiny-custom.cfg")
    classes = []
    with open("./obj.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]

    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    colors = np.random.uniform(0, 255, size=(len(classes), 3))

    # Loading image
    height, width, channels = img.shape
    cv2.imshow("Original Image", img)

    # Detecting objects
    blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)  # outs는 감지 결과이다. 탐지된 개체에 대한 모든 정보와 위치를 제공한다.

    # Showing informations on the screen
    class_ids = []
    confidences = []
    boxes = []

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > min_confidence:
                # Object detected
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                # Rectangle coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, min_confidence, 0.4)
    font = cv2.FONT_HERSHEY_PLAIN
    print(boxes)
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            print(i, label)
            color = colors[i]
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            cv2.putText(img, label, (x, y + 30), font, 2, (0, 255, 0), 1)

    return True if len(boxes) != 0 else len(boxes) == 0



class MQTT_Subscriber:
    def __init__(self, topic):
        self.limit = 0  # 최대 인증 시도 5회까지 check
        self.result_msg = None  # otp 인증 결과
        self.topic = topic

        # mongoDB 객체 생성해서 OTP 결과값 저장
        self.mongo = MongoDB()

        client = mqtt.Client()
        client.connect("localhost", 1883, 60)
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.loop_start()


    # self.topic 구독하기
    def on_connect(self, client, userdata, flags, rc):
        print("connected with result code" + str(rc))
        client.subscribe(self.topic)

    # 메세지 대기 모드
    def on_message(self, client, userdata, msg):
        input_data = msg.payload.decode()
        self.result_msg = "Success" if input_data == "1" else "Fail"
        if input_data == "0":
            self.limit += 1
            if self.limit == 5:
                self.result_msg = "Real Fail"
        print(self.result_msg)
        self.mongo.storeStr_otp(self.result_msg)  # MongoDB에 OTP 결과 저장



def check_person():
    print('find_person mode')

    # 사람을 확인했는지 확인하는 변수
    person_ditection = False

    # 터틀봇 영상 가져오기
    cap = cv2.VideoCapture('http://192.168.0.32:8080/stream?topic=/usb_cam/image_raw')
    while True:
        ret, frame = cap.read()
        # 디버깅용
        # frame = cv2.imread("./container/66.jpg")
        cv2.imshow("origin", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # 1..... yolo로 사람이 발견되면 otp 인증을 한다.
        if person_ditection == isPerson(frame):

            # 2..... OTP 인증 Mode start!!
            otp_client = MQTT_Subscriber("otp")
            while True:
                # 2-0..... OTP(MQTT) 메세지 분석
                otp_result = otp_client.result_msg
                if otp_result == "Success":
                    print("인증 성공!")
                    break

                if otp_client.limit == 5:
                    # 2-1.... 인증시도 5회 만료시, 현장 사진 mongoDB 저장
                    print("관리자 확인 요망!")
                    cv2.imwrite('./otpChecker/intruder.jpg', frame)
                    img = open('./otpChecker/intruder.jpg', 'rb')
                    mongo.storeImg_otp(img, 'intruder.jpg')  # 넘길 이미지와 이름
                    break



if __name__ =='__main__':
    # 사람을 찾는 main 함수
    check_person()
