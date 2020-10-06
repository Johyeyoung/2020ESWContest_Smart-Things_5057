#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy

import time
import math
from std_msgs.msg import String
import test_otp
import time_over



class MQTT_serve:
    def __init__(self):
        self.recive_order = ""  # 서버로부터의 경로
        self.otp_flag = "lost"

        rospy.Subscriber('/otp_start', String, self.callback_otp)  # OTP Subscriber
        rospy.Subscriber('/test', String, self.callback_server)  # 서버로부터 경로를 받는 Subscriber


    # 서버로부터 터틀봇의 움직임을 받음
    def callback_server(self, msg):
        self.recive_order = msg.data  # 서버 msg의 data

    # recive otp string
    def callback_otp(self, msg):
        self.otp_flag = msg.data  # OTP요청

    def get_order(self): #경로 전달
        return self.recive_order

    def get_otp_flag(self): #otp_flag 전달
        return self.otp_flag

    def otp_start(self): # OTP인증 시작
        est_otp.MQTT_Subscriber()
        self.otp_flag = ""  # OTP_flag 초기화

    def otp_lost(self): #객체 재확인 필요 요청
        test_otp.LOST_Subscriber()
        self.otp_flag = ""  # OTP_flag 초기화


