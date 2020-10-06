#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy

import time
from geometry_msgs.msg import Twist
import math
import Lidar
import mqtt_subscribe
from odometry import Odom


class Turtlebot_move:
    def __init__(self):

        self.current_degree = 0  # 터틀봇의 현재 방향
        self.kp = 0.5  # 터틀봇의 회전 속도
        self.mqtt_sub = mqtt_subscribe()
        self.Lidar = Lidar()
        rospy.init_node('turtle_move')
        self.odom = Odom()
        self.pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)  # 모터 회전 관련 publisher
        self.r = rospy.Rate(50)
        self.command = Twist()


    #움직임이 완료된 경로를 받아 재자리로 돌아가기 위한 경로를 생성
    def order_reversed(order):
        order = list(reversed(order))  # 경로역순으로 정렬하고 방향을 재조정후 return'
        print(order)
        order_change = {"G": "B", "B": "G", "L": "R", "R": "L"}
        for i in range(len(order)):
            order[i] = order[i].replace(order[i][0], order_change[order[i][0]])
        # order = order + "/G10"  # 원래 앞으로 바라보도록 기본 경로 추가
        print(order)
        return order

    # 앞으로 움직임(lds 센서를 보면서 좌우의 물체가 일정 가리와 가까워지면 그 반대 방향으로 이동)
    def move(self, linear, angular):
        time.sleep(0.2)
        twist = Twist()
        if (self.lidar.get_right() < 0.2):     #오른쪽에 장애물이 있을 경우 회피
            twist.angular.z = 0.1

        elif (self.lidar.get_left() < 0.2):    #왼쪽에 장애물이 있을 경우 회피
            twist.angular.z = -0.1

        else:
            twist.angular.z = angular #양쪽에 장애물이 없을경우

        twist.linear.x = linear

        self.pub.publish(twist)  # 터틀봇 움직임 요청

    # 터틀봇 기본 동작

    def move_go(self, dis):
        current_position_x = self.odom.get_position_x() #현재 x좌표 기록
        current_position_y = self.odom.get_position_y()#현재 y좌표 기록

        if (self.current_degree == 0): # 앞으로 이동
            while int(Odom.get_position_x() * 100) >= int((current_position_x + (0.1 * dis)) * 100):
                if (self.mqtt_sub.get_otp_flag() == "start"):  # 목표물을 발견했을 경우 OTP인증 요구
                    self.mqtt_sub.otp_start()
                    break
                self.move(0.01, 0)


        elif (self.current_degree == -90): # 오른쪽으로 이동앞
            while int(Odom.position_y() * 100) <= int((current_position_y - (0.1 * dis)) * 100):
                if (self.mqtt_sub.get_otp_flag() == "start"):  # 목표물을 발견했을 경우 OTP인증 요구
                    self.mqtt_sub.otp_start()
                    break
                self.move(0.01, 0)


        elif (self.current_degree == 90): # 왼쪽으로 이동
            while int(Odom.position_y() * 100) >= int((current_position_y + (0.1 * dis)) * 100):
                if (self.mqtt_sub.get_otp_flag() == "start"):  # 목표물을 발견했을 경우 OTP인증 요구
                    self.mqtt_sub.otp_start()
                    break
                self.move(0.01, 0)

        elif (self.current_degree == 180): #뒷쪽으로 이동
            while int(Odom.get_position_x()  * 100) <= int((current_position_x - (0.1 * dis)) * 100):
                if (self.mqtt_sub.get_otp_flag() == "start"):  # 목표물을 발견했을 경우 OTP인증 요구
                    self.mqtt_sub.otp_start()
                    break
                self.move(0.01, 0)


    def move_front(self, dis):  # 정면으로  회전
        self.current_degree = 0
        target_rad = self.current_degree * math.pi / 180  # target 방향 설정
        self.move_turn(target_rad)  # 터틀봇 회전
        self.move_go(dis)

    def move_back(self, dis):  # 180 방향으로 회전
        self.current_degree = 180
        target_rad = self.current_degree * math.pi / 180  # target 방향 설정
        self.move_turn(target_rad)  # 터틀봇 회전
        self.move_go(dis)


    def move_left(self, dis):  # 90도 방향으로 회전
        self.current_degree = 90
        target_rad = self.current_degree * math.pi / 180  # #target 방향 설정
        self.move_turn(target_rad)  # 터틀봇 회전
        self.move_go(dis)

    def move_right(self, dis):  # -90도 방향으로 회전
        self.current_degree = -90
        target_rad = self.current_degree * math.pi / 180  # target 방향 설정
        self.move_turn(target_rad)
        self.move_go(dis)

    def move_turn(self, target_rad):
        while not rospy.is_shutdown():
            self.command.angular.z = self.kp * (target_rad - Odom.get_yaw())  # 현재 각도에 따라 회전 속도를 조절
            self.pub.publish(self.command)
            self.r.sleeOp()
            if (int(self.command.angular.z * 100) == 0):
                break

    def move_stop(self):  # 정지
        self.move(0, 0)

    # json으로부터 입력받은 터틀봇의 움직임을 실행
    def start(self, order):
        print(order)
        min_move = 0
        # 터틀봇 움직임의 최소 단위
        for i in range(len(order)):
            if order[i][0] == 'R':  # 오른쪽으로 회전
                self.move_right(int(order[i][1:]))
            elif order[i][0] == 'L':  # 왼쪽으로 회전
                self.move_left(int(order[i][1:]))
            elif order[i][0] == 'G':  # 앞으로 이동
                self.move_front(int(order[i][1:]))
            elif order[i][0] == 'B':  # 뒤로 이동
                self.move_back(int(order[i][1:]))

        self.move(0, 0)
