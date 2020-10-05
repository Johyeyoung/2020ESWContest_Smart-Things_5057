#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
import self as self
from std_msgs.msg import Int32MultiArray
import time
from geometry_msgs.msg import Twist
from tf.transformations import euler_from_quaternion, quaternion_from_euler
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
import math
import json
from std_msgs.msg import String
import test_otp


class Turtlebot_move:
    def __init__(self):

        self.LINEAR = 0.1
        self.roll = self.pitch = self.yaw = 0.0
        self.current_degree = 0 #터틀봇의 현재 방향
        self.position_x = 0 #터틀봇의 x좌표
        self.position_y = 0 #터틀봇의 y좌표
        self.kp = 0.5  #터틀봇의 회전 속도
        self.recive_order = "" #서버로부터의 경로
        self.avg = []  #Lidar의 평균거리 list
        self.front = 0 #터틀봇과 앞의 물체와의 거리
        self.otp_flag = "lost"


        rospy.init_node('rotate_robot')
        self.sub_otp = rospy.Subscriber('/otp_start', String, self.callback_otp) #OTP Subscriber
        self.sub_server = rospy.Subscriber('/test', String, self.callback_server) # 서버로부터 경로를 받는 Subscriber
        self.sub = rospy.Subscriber('/odom', Odometry, self.callback) #터틀봇의 위치정보 Subscriber
        self.sub_lds = rospy.Subscriber('scan', LaserScan, self.callback_lidar) #Lidar로 부터 위치 정보를 받는 Subscriber
        self.ack_publisher = rospy.Publisher('/cmd_vel', Twist, queue_size=1) #모터 회전 관련 publisher
        self.r = rospy.Rate(50)
        self.command = Twist()
        rospy.sleep(2)

        while not rospy.is_shutdown():
            self.recive_order = "" #서버로부터 명령 초기화
            while self.recive_order == "":  #서버로부터 경로를 받을떄까지 기다림
                print("waiting reivd_order")

            self.recive_order="G32/L52/G20" #경로를 임의로 설정
            self.order = self.recive_order.split("/") # "/" 기준으로 명령을 분리
            self.start(self.order) #터틀봇 이동 시작
            rospy.spin()

        
    # Lider값 가공
    def callback_lidar(self,scan):
        self.front = scan.ranges[0] #터틀봇 정면의 Lidar 값


    # 서버로부터 터틀봇의 움직임을 받음
    def callback_server(self, msg):
        self.recive_order = msg.data #서버 msg의 data


    #recive otp string
    def callback_otp(self, msg):
        self.otp_flag = msg.data #서 OTP요청


    # 터틀봇의 움직임을 받음
    def callback(self, msg):
        orientation_q = msg.pose.pose.orientation
        self.position_x = msg.pose.pose.position.x  #자신의 X 좌표를 받음
        self.position_y = msg.pose.pose.position.y  #자신의 Y 좌표를 받음
        orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w] #위치 정보 list
        (self.roll, self.pitch, self.yaw) = euler_from_quaternion(orientation_list)

    # 앞으로 움직임(lds 센서를 보면서 좌우의 물체가 일정 가리와 가까워지면 그 반대 방향으로 이동)
    def move(self, linear, angular):
        twist = Twist()
        twist.linear.x = linear
        twist.angular.z = angular
        self.ack_publisher.publish(twist) #터틀봇 움직임 요청

    # 터틀봇 기본 동작

    def lds_move(self, dis): # Lidar를 이용하여 앞으로 이동
        dis = dis / 100
        current_front = self.front  #현재의 front값 저장
        time.sleep(0.1)
        while (not rospy.is_shutdown()):

            if(self.otp_flag == "start"): #서버로부터 start를 받았을 경우 otp실행
                self.move(0,0)
                test_otp.MQTT_Subscriber()
                self.otp_flag = "" #OTP_flag 초기화
                break
            time.sleep(0.01)
            self.move(0.05, 0)

            if (self.front - current_front < -1 * 1.5 * dis): #Lidat 값이 너무 크게 잡힐경우 무시
                continue

            if (self.front - current_front <= -1 * dis):  #Lidar 값이 dis만큼 차이 날떄까지 move
                time.sleep(0.1)
                self.move(0, 0)

                break

    def move_front(self, dis):  # 정면으로  회전
        self.current_degree = 0
        target_rad = self.current_degree * math.pi / 180 #target 방향 설정
        self.move_turn(self, target_rad) #터틀봇 회전

        self.lds_move(dis)

    def move_back(self, dis):  # 180 방향으로 회
        self.current_degree = 180
        target_rad = self.current_degree * math.pi / 180 #target 방향 설정
        self.move_turn(self, target_rad) #터틀봇 회전

        self.lds_move(dis)

    def move_left(self, dis):  # 90도 방향으로 회전
        self.current_degree = 90
        target_rad = self.current_degree * math.pi / 180  # #target 방향 설정
        self.move_turn(self, target_rad) #터틀봇 회전

        self.lds_move(dis)

    def move_right(self, dis):  # -90도 방향으로 회전
        self.current_degree = -90
        target_rad = self.current_degree * math.pi / 180 #target 방향 설정
        self.move_turn(self, target_rad)

        self.lds_move(dis)

    def move_turn(self, target_rad): #target 각도를 전달받아 회전
        while not rospy.is_shutdown():
            self.command.angular.z = self.kp * (target_rad - self.yaw) #현재 각도에 따라 회전 속도를 조절
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
            if order[i][0] == 'R': #오른쪽으로 회전
                self.move_right(float(order[i][1:]))  #방향과 이동거리를 인자로 넘김
            elif order[i][0] == 'L': #왼쪽으로 회전
                self.move_left(float(order[i][1:]))
            elif order[i][0] == 'G': #앞으로 이동
                self.move_front(float(order[i][1:]))
            elif order[i][0] == 'B': #뒤로 이동
                self.move_back(float(order[i][1:]))

        self.move(0,0)
        currnet_time = time.time()

        while(True): #경로이동 완료후 현재 위치에서 10초동안 목표 확인을 기다림
            if (time.time() - currnet_time > 10):  #목표물을 발견하지 못했을 경우 서버에 알림
                self.otp_flag == "lost"
                test_otp.LOST_Subscriber()
                break

            elif(self.otp_flag == "start"): #목표물을 발견했을 경우 OTP인증 요구
                test_otp.MQTT_Subscriber()

