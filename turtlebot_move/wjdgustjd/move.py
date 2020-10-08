#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy

from std_msgs.msg import Int32MultiArray
import time
from geometry_msgs.msg import Twist
from tf.transformations import euler_from_quaternion, quaternion_from_euler
from nav_msgs.msg import Odometry
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

        # self.sub = rospy.Subscriber('/odom', Odometry, self.callback)  # 터틀봇의 위치정보 Subscriber
        self.pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)  # 모터 회전 관련 publisher
        self.r = rospy.Rate(50)
        self.command = Twist()
        rospy.sleep(2)

        while not rospy.is_shutdown():
            self.recive_order = "" #서버로부터 명령 초기화
            while self.recive_order == "":  #서버로부터 경로를 받을떄까지 기다림
                print("waiting reived_order")

            self.recive_order="G1/L1/G1" #경로를 임의로 설정
            self.order = self.recive_order.split("/") # "/" 기준으로 명령을 분리
            self.start(self.order) #터틀봇 이동 시작

        currnet_time = time.time()
        #경로 이동후 OTP확인
        while True:        #경로이동 완료후 현재 위치에서 10초동안 목표 확인을 기다림
            if (time.time() - currnet_time > 60):  #목표물을 발견하지 못했을 경우 서버에 알림
                self.mqtt_sub.otp_lost()
                break

            elif(self.mqtt_sub.get_otp_flag() == "start"): #목표물을 발견했을 경우 OTP인증 요구
                self.mqtt_sub.otp_start()
                break

        self.reverse_order = self.order_reversed(self.order)#경로를 역순으로 정렬
        self.start(self.reverse_order) #역순으로 정렬된 경로로 이동

        rospy.spin()





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
            while int(self.position_x * 100) >= int((current_position_x + (0.1 * dis)) * 100):
                if (self.mqtt_sub.get_otp_flag() == "start"):  # 목표물을 발견했을 경우 OTP인증 요구
                    self.mqtt_sub.otp_start()
                    break
                self.move(0.01, 0)


        elif (self.current_degree == -90): # 오른쪽으로 이동앞
            while int(self.position_y * 100) <= int((current_position_y - (0.1 * dis)) * 100):
                if (self.mqtt_sub.get_otp_flag() == "start"):  # 목표물을 발견했을 경우 OTP인증 요구
                    self.mqtt_sub.otp_start()
                    break
                self.move(0.01, 0)


        elif (self.current_degree == 90): # 왼쪽으로 이동
            while int(self.position_y * 100) >= int((current_position_y + (0.1 * dis)) * 100):
                if (self.mqtt_sub.get_otp_flag() == "start"):  # 목표물을 발견했을 경우 OTP인증 요구
                    self.mqtt_sub.otp_start()
                    break
                self.move(0.01, 0)

        elif (self.current_degree == 180): #뒷쪽으로 이동
            while int(self.position_x * 100) <= int((current_position_x - (0.1 * dis)) * 100):
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

        # self.lds_move(dis)

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
            self.command.angular.z = self.kp * (target_rad - self.yaw)  # 현재 각도에 따라 회전 속도를 조절
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


Turtlebot_move()

if __name__ == '__main__':
    move = Turtlebot_move()
    while rospy.is_shutdown():
        move