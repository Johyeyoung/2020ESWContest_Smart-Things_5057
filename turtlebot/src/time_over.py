# -*- coding: utf-8 -*-
import Jetson.GPIO as GPIO
import paho.mqtt.client as mqtt
import time
import json


# otp mqtt client
def mqtt_client(pos):
    # MQTT client 생성, 이름
    mqtt2 = mqtt.Client("OTP")
    mqtt2.connect("192.168.0.15", 1883)  # 로컬호스트에 있는 MQTT서버에 접속
    mqtt2.publish("otp_result", pos)  # topic 과 넘겨줄 값


class LOST_Subscriber:
    def __init__(self):
        pos = "3"  # lost
        mqtt_client(pos)








