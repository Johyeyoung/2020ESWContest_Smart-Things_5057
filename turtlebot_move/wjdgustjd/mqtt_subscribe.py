#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy

from std_msgs.msg import Int32MultiArray
import time
from geometry_msgs.msg import Twist
from tf.transformations import euler_from_quaternion, quaternion_from_euler
from nav_msgs.msg import Odometry
import math
from std_msgs.msg import String
import test_otp
import time_over



class Turtlebot_move:
    def __init__(self):

        self.recive_order = ""  # 서버로부터의 경로
        self.otp_flag = "lost"

        rospy.init_node('turtle_server')
        self.sub_otp = rospy.Subscriber('/otp_start', String, self.callback_otp)  # OTP Subscriber
        self.sub_server = rospy.Subscriber('/test', String, self.callback_server)  # 서버로부터 경로를 받는 Subscriber
        self.r = rospy.Rate(50)
        self.command = Twist()
        rospy.sleep(2)

        rospy.spin()

    # 서버로부터 터틀봇의 움직임을 받음
    def callback_server(self, msg):
        self.recive_order = msg.data  # 서버 msg의 data

    # recive otp string
    def callback_otp(self, msg):
        self.otp_flag = msg.data  # OTP요청

    def get_order(self):
        return self.recive_order

    def get_otp_flag(self):
        return self.otp_flag

    def otp_start(self):
        if (self.otp_flag == "start"):  # 서버로부터 start를 받았을 경우 otp실행
            self.move(0, 0)
            test_otp.MQTT_Subscriber()
            self.otp_flag = ""  # OTP_flag 초기화

    def otp_lost(self):
        if (self.otp_flag == "lost"):  # 서버로부터 start를 받았을 경우 otp실행
            self.move(0, 0)
            test_otp.LOST_Subscriber()
            self.otp_flag = ""  # OTP_flag 초기화


