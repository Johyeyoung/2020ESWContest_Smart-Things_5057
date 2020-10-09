# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import time
import json
from otp import otp_check

# otp_check 이 result 를 반환
# pos = str(otp_check())
class MQTT_publisher:
    def __init__(self):
        self.mqtt_client = mqtt.Client("OTP")

    def otp_value_publish(self, pos):
        # MQTT client 생성, 이름
        self.mqtt_client.connect("192.168.0.15", 1883)  # 로컬호스트에 있는 MQTT서버에 접속
        self.mqtt_client.publish("otp_result", pos)  # topic 과 넘겨줄 값

    def time_over_value_publish(self):
        pos = "3"  # lost
        self.otp_value_publish(pos)

    def success_or_fail_publish(self):
        pos = 0
        cnt = 0
        print("start")
        while pos != "1":
            # turn on otp & get data
            pos = str(otp_check())
            print("sending")
            self.otp_value_publish(pos)

            cnt += 1
            if cnt == 5:
                break
