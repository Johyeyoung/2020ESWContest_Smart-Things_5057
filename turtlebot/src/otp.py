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


# # otp mqtt client s
# def mqtt_client(pos):
#     # MQTT client 생성, 이름
#     mqtt2 = mqtt.Client("OTP")
#     mqtt2.connect("192.168.0.15", 1883)  # 로컬호스트에 있는 MQTT서버에 접속
#     mqtt2.publish("otp_result", pos)  # topic 과 넘겨줄 값

#
# class MQTT_publisher:
#     def __init__(self):
#
#         pos = 0
#         cnt = 0
#         print("start")
#         while pos != "1":
#             # turn on otp & get data
#             pos = str(otp_check())
#             print("sending")
#             mqtt_client(pos)
#
#             cnt += 1
#             if cnt == 5:
#                 break


# class MQTT_publisher:
#     def __init__(self):
#         self.mqtt_client = mqtt.Client("OTP")
#
#     def otp_value_publish(pos):
#         # MQTT client 생성, 이름
#         self.mqtt_client.connect("192.168.0.15", 1883)  # 로컬호스트에 있는 MQTT서버에 접속
#         self.mqtt_client.publish("otp_result", pos)  # topic 과 넘겨줄 값
#
#     def time_over_value_publish(self):
#         pos = "3"  # lost
#         self.otp_value_publish(pos)
#
#     def success_or_fail_publish(self):
#         pos = 0
#         cnt = 0
#         print("start")
#         while pos != "1":
#             # turn on otp & get data
#             pos = str(otp_check())
#             print("sending")
#             self.otp_value_publish(pos)
#
#             cnt += 1
#             if cnt == 5:
#                 break




