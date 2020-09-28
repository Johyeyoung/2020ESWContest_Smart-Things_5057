import cv2
import numpy as np
import json
from mongoengine import connect, Document, fields
import paho.mqtt.client as mqtt
from MongoDB import *
mongo = MongoDB()

LABELS_FILE='obj.names'
CONFIG_FILE='yolov4-tiny-custom.cfg'
WEIGHTS_FILE='yolov4-tiny-custom_3000.weights'
min_confidence = 0.3
h, w=None, None

net = cv2.dnn.readNetFromDarknet(CONFIG_FILE, WEIGHTS_FILE)
layer_names = net.getLayerNames()
output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
LABELS = open(LABELS_FILE).read().strip().split("\n")
np.random.seed(4)
COLORS = np.random.randint(0, 255, size=(len(LABELS), 3), dtype="uint8")



# 들어온 화면에서 yolo로 사람인지 확인하기
def isPerson(img):

    # Loading image
    height, width, channels = img.shape

    # Detecting objects
    blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)  # outs는 감지 결과이다. 탐지된 개체에 대한 모든 정보와 위치를 제공한다.

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
            if confidence > min_confidence:
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

    idxs = cv2.dnn.NMSBoxes(boxes, confidences, min_confidence,
                            min_confidence)

    # ensure at least one detection exists
    if len(idxs) > 0:
        # loop over the indexes we are keeping
        for i in idxs.flatten():
            # extract the bounding box coordinates
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])
            color = [int(c) for c in COLORS[class_ids[i]]]

            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            text = "{}: {:.4f}".format(LABELS[class_ids[i]], confidences[i])
            cv2.putText(img, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, color, 2)

    # show the output image
    cv2.imshow("output", cv2.resize(img, (800, 600)))
    #writer.write(cv2.resize(img, (800, 600)))
    cv2.waitKey(1) & 0xFF
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
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        # 디버깅용
        # frame = cv2.imread("./container/66.jpg")
        cv2.imshow("origin", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        isPerson(frame)
        # 1..... yolo로 사람이 발견되면 otp 인증을 한다.
        if person_ditection == isPerson(frame):

            # .... TurtleBot 에게 경로 정보 넘기기
            import paho.mqtt.client as mqtt
            mqtt = mqtt.Client("OTP")  # MQTT client 생성, 이름 ""
            mqtt.connect("localhost", 1883)  # 로컬호스트에 있는 MQTT서버에 접속
            mqtt.publish("otp_start", json.dumps({"data": "start"}))  # topic 과 넘겨줄 값

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
    mqtt_Subscriber = MQTT_Subscriber()
    # 사람을 찾는 main 함수
