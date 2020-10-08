import cv2
import numpy as np
import json
from mongoengine import connect, Document, fields
import paho.mqtt.client as mqtt
from MongoDB import *


class Yolo_checker:
    def __init__(self):
        LABELS_FILE = './yolo/obj.names'
        CONFIG_FILE = './yolo/yolov4-tiny-custom.cfg'
        WEIGHTS_FILE = './yolo/yolo_turtle.weights'
        self.min_confidence = 0.3
        h, w = None, None

        self.net = cv2.dnn.readNetFromDarknet(CONFIG_FILE, WEIGHTS_FILE)
        layer_names = self.net.getLayerNames()
        self.output_layers = [layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
        self.LABELS = open(LABELS_FILE).read().strip().split("\n")
        np.random.seed(4)
        self.COLORS = np.random.randint(0, 255, size=(len(self.LABELS), 3), dtype="uint8")


    # 들어온 화면에서 yolo로 사람인지 확인하기
    def isPerson(self, img):
        # Loading image
        height, width, channels = img.shape
        # Detecting objects
        blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        self.net.setInput(blob)
        outs = self.net.forward(self.output_layers)  # outs는 감지 결과이다. 탐지된 개체에 대한 모든 정보와 위치를 제공한다.

        # Showing informations on the screen
        class_ids = []
        confidences = []
        boxes = []
        (h, w) = img.shape[:2]
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > self.min_confidence:
                    # Object detected
                    # center_x = int(detection[0] * width)
                    # center_y = int(detection[1] * height)
                    box = detection[0:4] * np.array([w, h, w, h])
                    (center_x, center_y, width, height) = box.astype("int")

                    # Rectangle coordinates
                    x = int(center_x - (width / 2))
                    y = int(center_y - (height / 2))
                    boxes.append([x, y, int(width), int(height)])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        idxs = cv2.dnn.NMSBoxes(boxes, confidences, self.min_confidence,
                                self.min_confidence)

        # ensure at least one detection exists
        if len(idxs) > 0:
            # loop over the indexes we are keeping
            for i in idxs.flatten():
                # extract the bounding box coordinates
                (x, y) = (boxes[i][0], boxes[i][1])
                (w, h) = (boxes[i][2], boxes[i][3])
                color = [int(c) for c in self.COLORS[class_ids[i]]]

                cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
                text = "{}: {:.4f}".format(self.LABELS[class_ids[i]], confidences[i])
                cv2.putText(img, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, color, 2)

        # show the output image
        #cv2.imshow("output", cv2.resize(img, (800, 600)))
        #writer.write(cv2.resize(img, (800, 600)))
        #cv2.waitKey(1) & 0xFF
        return True if len(idxs) != 0 else False



class MQTT_OTP_Subscriber:
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
        print("터틀봇의 답변을 기다리고 있습니다 ▼")
        client.subscribe(self.topic)

    # 메세지 대기 모드
    def on_message(self, client, userdata, msg):
        input_data = msg.payload.decode()
        answer_lst = {"1": "Success", "0": "Fail", "3": "Time_Over"}
        self.result_msg = answer_lst[input_data]
        if input_data == "0":
            self.limit += 1
            if self.limit == 5:
                self.result_msg = "Real Fail"
        print("Result ▶ ", self.result_msg)
        self.mongo.storeStr_otp(self.result_msg)  # MongoDB에 OTP 결과 저장


class Find_person:
    def __init__(self):
        # 필요한 객체 생성
        self.otp_client = MQTT_OTP_Subscriber("otp_result")
        self.yolo_checker = Yolo_checker()
        self.mongo = MongoDB()

        # 사람을 확인했는지 확인하는 변수
        self.flag = 0
        # 터틀봇 영상 가져오기
        self.cap = cv2.VideoCapture('http://192.168.0.32:8080/stream?topic=/usb_cam/image_raw')


    def check_person(self):
        try:
            while True:
                ret, frame = self.cap.read()

                # 1..... yolo로 사람이 발견되면 otp 인증을 한다.
                if self.yolo_checker.isPerson(frame) and self.flag == 0:
                    self.flag = 1
                    print("                    Find person  --------->  OTP ON                    ")
                    print("___________________ 사람을 발견했습니다. OTP 인증 시도 ___________________")
                    # 1-0 .... TurtleBot 에게 otp 시작 알림
                    import paho.mqtt.client as mqtt
                    mqtt = mqtt.Client("OTP")  # MQTT client 생성, 이름 ""
                    mqtt.connect("localhost", 1883)  # 로컬호스트에 있는 MQTT서버에 접속
                    mqtt.publish("otp_start", json.dumps({"data": "start"}))  # topic 과 넘겨줄 값


                # 2..... OTP 인증 Mode start!! --- (MQTT) 답변 받기 및 메세지 분석
                otp_result = self.otp_client.result_msg
                if otp_result == "Success":
                    print("▶ OTP 인증 성공 ")
                    return True
                elif otp_result == "Time_Over":
                    print("▶ OTP 시간 초과 ")
                    self.mongo.storeImg_otp(frame, 'intruder.jpg')  # 넘길 이미지와 이름
                    return False  # 다시 드론으로부터 이미지 받아서 추적
                if self.otp_client.limit == 5:
                    # 2-1.... 인증시도 5회 만료시, 현장 사진 mongoDB 저장
                    print("▶ OTP 관리자 확인 요망 ")
                    self.mongo.storeImg_otp(frame, 'intruder.jpg')  # 넘길 이미지와 이름
                    return False  # 다시 드론으로부터 이미지 받아서 추적

                # .......... 디버깅용
                # cv2.imshow("origin", frame)
                # if cv2.waitKey(1) & 0xFF == ord('q'):
                #    break
        except:
            pass


if __name__ =='__main__':
    # 사람을 찾는 main 함수
    find_person = Find_person()
    find_person.check_person()
