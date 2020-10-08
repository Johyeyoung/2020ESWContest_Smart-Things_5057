# -*- coding: utf-8 -*-
import Jetson.GPIO as GPIO
import paho.mqtt.client as mqtt
import time
import json
from otp import mqtt_client


class LOST_publisher:
    def __init__(self):
        pos = "3"  # lost
        mqtt_client(pos)








