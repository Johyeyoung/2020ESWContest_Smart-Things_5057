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
import Lidar
import mqtt_subscribe


class Turtlebot_move:
    def __init__(self):

        self.roll = self.pitch = self.yaw = 0.0
        self.current_degree = 0  # 터틀봇의 현재 방향
        self.position_x = 0  # 터틀봇의 x좌표
        self.position_y = 0  # 터틀봇의 y좌표
        self.kp = 0.5  # 터틀봇의 회전 속도
        self.mqtt_sub = mqtt_subscribe()
        self.Lidar = Lidar()

        rospy.init_node('turtle_move')
        self.sub = rospy.Subscriber('/odom', Odometry, self.callback)  # 터틀봇의 위치정보 Subscriber
        self.pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)  # 모터 회전 관련 publisher
        self.r = rospy.Rate(50)
        self.command = Twist()
        rospy.sleep(2)

        self.recive_order = "G1/L1/G1"  # 경로를 임의로 설정
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

    # 앞으로 움직임(lds 센서를 보면서 좌우의 물체가 일정 가리와 가까워지면 그 반대 방향으로 이동)
    def move(self, linear, angular):
        time.sleep(0.2)
        twist = Twist()
        if (self.lidar.get_right() < 0.2):     #오른쪽에 장애물이 있을 경우 회피
            twist.angular.z = 0.1

        elif (self.lidar.left() < 0.2):    #왼쪽에 장애물이 있을 경우 회피
            twist.angular.z = -0.1

        else:
            twist.angular.z = angular #양쪽에 장애물이 없을경우

        twist.linear.x = linear

        self.pub.publish(twist)  # 터틀봇 움직임 요청

    # 터틀봇 기본 동작

    def move_go(self, dis):
        for i in range(int(dis)):
            current_position_x = self.position_x
            current_position_y = self.position_y
            if (self.current_degree == 0):
                while not rospy.is_shutdown():
                    self.move(0.01, 0)
                    if (int(self.position_x * 100) >= int((current_position_x + 0.1) * 100)):
                        self.move_stop()

                        break
            elif (self.current_degree == -90):
                while not rospy.is_shutdown():
                    self.move(0.01, 0)
                    if (int(self.position_y * 100) <= int((current_position_y - 0.1) * 100)):
                        self.move_stop()
                        break
            elif (self.current_degree == 90):
                while not rospy.is_shutdown():
                    self.move(0.01, 0)
                    if (int(self.position_y * 100) >= int((current_position_y + 0.1) * 100)):
                        self.move_stop()
                        break
            elif (self.current_degree == 180):
                while not rospy.is_shutdown():
                    self.move(0.01, 0)
                    if (int(self.position_x * 100) <= int((current_position_x - 0.1) * 100)):
                        self.move_stop()
                        break
                        self.move(0, 0)


    def move_front(self, dis):  # 정면으로  회전
        self.current_degree = 0
        target_rad = self.current_degree * math.pi / 180  # target 방향 설정
        self.move_turn(target_rad)  # 터틀봇 회전
        self.move_go(dis)

    def move_back(self, dis):  # 180 방향으로 회전ㄴ
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
            self.r.sleep()
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
                self.move_right(float(order[i][1:]))
            elif order[i][0] == 'L':  # 왼쪽으로 회전
                self.move_left(float(order[i][1:]))
            elif order[i][0] == 'G':  # 앞으로 이동
                self.move_front(float(order[i][1:]))
            elif order[i][0] == 'B':  # 뒤로 이동
                self.move_back(float(order[i][1:]))

        self.move(0, 0)


Turtlebot_move()

