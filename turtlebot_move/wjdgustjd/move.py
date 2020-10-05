#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
from std_msgs.msg import Int32MultiArray
from geometry_msgs.msg import Twist
from tf.transformations import euler_from_quaternion, quaternion_from_euler
from nav_msgs.msg import Odometry
import math
import json



class move:
    def __init__(self):
        self.roll = self.pitch = self.yaw = 0.0
        self.current_degree = 0  # 터틀봇의 현재 방향
        self.position_x = 0  # 터틀봇의 x좌표
        self.position_y = 0  # 터틀봇의 y좌표
        self.kp = 0.5  # 터틀봇의 회전 속도
        self.order = self.recive_order.split("/")  # "/" 기준으로 명령을 분리
        self.start(self.order)  # 터틀봇 이동 시작
        rospy.spin()


    # 터틀봇의 움직임을 받음
    def callback(self, msg):
        orientation_q = msg.pose.pose.orientation
        self.position_x = msg.pose.pose.position.x  # 자신의 X 좌표를 받음
        self.position_y = msg.pose.pose.position.y  # 자신의 Y 좌표를 받음
        orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]  # 위치 정보 list
        (self.roll, self.pitch, self.yaw) = euler_from_quaternion(orientation_list)