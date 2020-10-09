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

    time.sleep(0.1)
    GPIO.output(37, GPIO.LOW)

    while (1):
        if GPIO.input(33) == 1:
            result = "1"
            time.sleep(0.5)


            break
        elif GPIO.input(35) == 1:
            result = "0"
            time.sleep(0.5)


            break

    return result
