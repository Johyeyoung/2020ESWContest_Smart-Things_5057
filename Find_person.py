import cv2
import numpy as np
import json
from mongoengine import connect, Document, fields
import paho.mqtt.client as mqtt
from MongoDB import *

mongo = MongoDB()


def on_connect(client, userdata, flags, rc):
    print("connected with result code" + str(rc))
    client.subscribe("mqtt/myiot/#")

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    return msg

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)
client.loop_forever()



def check_person():
    print('find_person mode')

    # 사람을 확인했는지 확인하는 변수
    person_ditection = False

    # 터틀봇 영상 가져오기
    cap = cv2.VideoCapture('http://192.168.0.32:8080/stream?topic=/usb_cam/image_raw')
    while True:
       ret, frame = cap.read()
       cv2.imshow("origin", frame)
       if cv2.waitKey(1) & 0xFF == ord('q'):
           break
       limit = 0
       # 사람이 발견되면 otp 인증을 한다.
       person = isPerson(frame)

       if person_ditection == person:
            # OTP 인증받기
            result = 0





            while result != 1:


                # mongoDB로 저장하기
                img = open('./container/map_result.jpg', 'rb')
                mongo.storeImg(img, 'map.jpg')  # 넘길 이미지와 이름


                # OPT의 결과가 1이면 성공/ 0이면 실패
                limit += 1
                if limit == 3:
                    result = 2
                   break

            # mongoDB로 옮기기
            img = open('./container/map_result.jpg', 'rb')
            mongo.storeImg(, 'map.jpg')  # 넘길 이미지와 이름



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

check_person()