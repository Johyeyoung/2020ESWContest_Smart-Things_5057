#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
from tf.transformations import euler_from_quaternion, quaternion_from_euler
from nav_msgs.msg import Odometry


class Odom:
    def __init__(self):
        rospy.Subscriber('/odom', Odometry, self.callback_odom)  # 터틀봇의 위치정보 Subscriber
        self.roll, self.pitch, self.yaw = -1, -1, -1
        self.position_x = ''
        self.position_y = ''

    def callback_odom(self, msg):
        orientation_q = msg.pose.pose.orientation
        self.position_x = msg.pose.pose.position.x  # 자신의 X 좌표를 받음
        self.position_y = msg.pose.pose.position.y  # 자신의 Y 좌표를 받음
        orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]  # 위치 정보 list
        self.roll, self.pitch, self.yaw = euler_from_quaternion(orientation_list)

    def get_roll(self):
        return self.roll

    def get_pitch(self):
        return self.pitch

    def get_yaw(self):
        return self.yaw

    def get_position_x(self):
        return self.position_x

    def get_position_y(self):
        return self.position_y
