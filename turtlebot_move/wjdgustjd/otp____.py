# -*- coding: utf-8 -*-
import Jetson.GPIO as GPIO
import paho.mqtt.client as mqtt
import time
import json


def otp_check():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(33, GPIO.IN)
    GPIO.setup(35, GPIO.IN)
    GPIO.setup(37, GPIO.OUT)
    count = 0
    result = 0
    GPIO.output(37, GPIO.HIGH)
    print(1)
    time.sleep(0.1)
    GPIO.output(37, GPIO.LOW)
    print("in")
    while (1):
        if GPIO.input(33) == 1:
            result = "1"
            time.sleep(0.5)
            print(0)

            break
        elif GPIO.input(35) == 1:
            result = "0"
            time.sleep(0.5)
            print(1)

            break

    return result


# otp mqtt client s
def mqtt_client(pos):
    # MQTT client 생성, 이름
    mqtt2 = mqtt.Client("OTP")
    mqtt2.connect("192.168.0.66", 1883)  # 로컬호스트에 있는 MQTT서버에 접속
    print(123)
    mqtt2.publish("otp_result", pos)  # topic 과 넘겨줄 값
    print(456)


class MQTT_Subscriber:
    def __init__(self):

        pos = 0
        cnt = 0
        print("start")
        while pos != "1":
            # turn on otp & get data
            pos = str(otp_check())
            print("sending")
            mqtt_client(pos)

            cnt += 1
            if cnt == 5:
                break

time.sleep(5)
MQTT_Subscriber()






