#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
from std_msgs.msg import Int32MultiArray
from sensor_msgs.msg import LaserScan
import math

class Lds:
    def __init__(self):
        rospy.init_node('turtle_lds')
        self.sub_lds = rospy.Subscriber('scan', LaserScan, self.callback_lidar)  # Lidar로 부터 위치 정보를 받는 Subscriber
        self.right = 0
        self.left = 0
        self.front = 0


    # Lider값 가공
    def callback_lidar(self, scan):
        self.right = scan.ranges[330] #오른쪽 30도 방향
        self.left = scan.ranges[30] #왼쪽 30도 방향
        self.front = scan.ranges[0]  # 터틀봇 정면의 Lidar 값

    def get_right(self):
        return self.right

    def get_left(self):
        return self.left

    def get_front(self):
        return self.front