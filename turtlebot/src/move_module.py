#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
from std_msgs.msg import Int32MultiArray
import time
from geometry_msgs.msg import Twist
from tf.transformations import euler_from_quaternion, quaternion_from_euler
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
import math
import json
from std_msgs.msg import String


class Turtlebot_move:
    def __init__(self):

        self.LINEAR = 0.1

        self.roll = self.pitch = self.yaw = 0.0
        self.current_degree = 0
        self.position_x = 0
        self.position_y = 0
        self.kp = 0.5
        self.recive_order = ""
	self.recive_otp_str =""
        self.avg = []
        self.front = 0
	self.otp_flag = ""


        rospy.init_node('rotate_robot')
	self.sub_otp = rospy.Subscriber('/otp_start', String, self.callback_otp)
        self.sub_server = rospy.Subscriber('/test', String, self.callback_server)

        self.ack_publisher = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
        self.sub = rospy.Subscriber('/odom', Odometry, self.callback)
        self.sub_lds = rospy.Subscriber('scan', LaserScan, self.callback_lidar)
	
        self.pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)
        self.r = rospy.Rate(50)
        self.command = Twist()
        rospy.sleep(2)
	self.recive_order="R57/G35"
        self.order = self.recive_order.split("/")
        self.start(self.order)
	rospy.spin()

        
    # Lider값 가공
    def callback_lidar(self,scan):
	
        Front = scan.ranges[0:14] + scan.ranges[345:359]
        Left1 = scan.ranges[15:34]
        Left2 = scan.ranges[35:54]
        Left3 = scan.ranges[55:74]
        Left4 = scan.ranges[75:94]
        Right1 = scan.ranges[325:344]
        Right2 = scan.ranges[305:324]
        Right3 = scan.ranges[285:304]
        Right4 = scan.ranges[265:284]
        back = scan.ranges[95:264]

        # average
        Front_avg = self.avge(Front)
        Left1_avg = self.avge(Left1)
        Left2_avg = self.avge(Left2)
        Left3_avg = self.avge(Left3)
        Left4_avg = self.avge(Left4)
        Right1_avg = self.avge(Right1)
        Right2_avg = self.avge(Right2)
        Right3_avg = self.avge(Right3)
        Right4_avg = self.avge(Right4)
        back_avg = self.avge(back)

        self.avg = [Front_avg, Left1_avg, Left2_avg, Left3_avg, Left4_avg, Right1_avg, Right2_avg, Right3_avg,
               Right4_avg,
               back_avg]

        self.front = scan.ranges[0]

    # lidar값 평균 구하기
    def avge(self, arr):
        l = []
        for i in arr:
            if i == float("inf"):
                continue
            elif i == 0:
                continue
            else:
                l.append(i)
        # print(l)
        return sum(l) / (len(l) + 0.01)

    # 서버로부터 터틀봇의 움직임을 받음
    def callback_server(self, msg):
	print("receive data from topic 'test'")
        self.recive_order = msg.data

    

    #recive otp string
    def callback_otp(self, msg):
	self.otp_flag = msg.data


    # 터틀봇의 움직임을 받음
    def callback(self, msg):
        orientation_q = msg.pose.pose.orientation
        self.position_x = msg.pose.pose.position.x
        self.position_y = msg.pose.pose.position.y
        orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
        (self.roll, self.pitch, self.yaw) = euler_from_quaternion(orientation_list)

    # 앞으로 움직임(lds 센서를 보면서 좌우의 물체가 일정 가리와 가까워지면 그 반대 방향으로 이동)
    def move(self, linear, angular):
        twist = Twist()
        twist.linear.x = linear
        twist.angular.z = angular
        self.ack_publisher.publish(twist)

    # 터틀봇 기본 동작

    def lds_move(self, dis):
        print("okay_2")

        dis = dis / 100
        current_front = self.front
        time.sleep(0.1)
        while (not rospy.is_shutdown()):

	    if(self.otp_flag == "start"):
		self.move(0,0)
		test_otp.MQTT_Subscriber()
		self.otp_flag = ""
		print("find")
		break
		
            time.sleep(0.01)
            self.move(0.1, 0)
 

            if (self.front - current_front < -1 * 1.5 * dis):
                continue

            if (self.front - current_front <= -1 * dis):
                print(self.front - current_front)
                time.sleep(0.1)
                self.move(0, 0)
                print("done")
                break

    def move_front(self, dis):  # 정면으로  회전
        self.current_degree = 0

        while not rospy.is_shutdown():
            # quat = quaternion_from_euler (roll, pitch,yaw)
            # print quat
            target_rad = 0 * math.pi / 180
            self.command.angular.z = self.kp * (target_rad - self.yaw)
            self.pub.publish(self.command)
            print("-------")
            print("taeget={} current:{}", self.current_degree, self.yaw)
            print(self.command.angular.z)
            print("------")
            self.r.sleep()
            if (int(self.command.angular.z * 100) == 0):
                break
        print(dis)
        print(type(dis))
        self.lds_move(dis)

    def move_back(self, dis):  # 180 방향으로 회
        self.current_degree = 180

        while not rospy.is_shutdown():
            # quat = quaternion_from_euler (roll, pitch,yaw)
            # print quat
            target_rad = 180 * math.pi / 180
            self.command.angular.z = self.kp * (target_rad - self.yaw)
            self.pub.publish(self.command)
            print("taeget={} current:{}", self.current_degree, self.yaw)
            print(self.command.angular.z)
            self.r.sleep()
            if (int(self.command.angular.z * 100) == 0):
                break
        self.lds_move(dis)

    def move_left(self, dis):  # 90도 방향으로 회전
        self.current_degree = 90
        while not rospy.is_shutdown():
            # quat = quaternion_from_euler (roll, pitch,yaw)
            # print quat
            target_rad = 90 * math.pi / 180
            self.command.angular.z = self.kp * (target_rad - self.yaw)
            self.pub.publish(self.command)
            print("taeget={} current:{}", self.current_degree, self.yaw)
            print(self.command.angular.z)
            self.r.sleep()
            if (int(self.command.angular.z * 100) == 0):
                break
        self.lds_move(dis)

    def move_right(self, dis):  # -90도 방향으로 회전
        self.current_degree = -90

        while not rospy.is_shutdown():
            # quat = quaternion_from_euler (roll, pitch,yaw)
            # print quat
            target_rad = -90 * math.pi / 180
            self.command.angular.z = self.kp * (target_rad - self.yaw)
            self.pub.publish(self.command)
            print("taeget={} current:{}", self.current_degree, self.yaw)
            print(self.command.angular.z)
            self.r.sleep()
            if (int(self.command.angular.z * 100) == 0):
                break
        self.lds_move(dis)

    def move_stop(self):  # 정지
        self.move(0, 0)

    # json으로부터 입력받은 터틀봇의 움직임을 실행
    def start(self, order):
        print(order)
        min_move = 0
        # 터틀봇 움직임의 최소 단위
        for i in range(len(order)):
            if order[i][0] == 'R': #오른쪽으로 회전
                self.move_right(float(order[i][1:]))
            elif order[i][0] == 'L': #왼쪽으로 회전
                self.move_left(float(order[i][1:]))
            elif order[i][0] == 'G': #앞으로 이동
                print("okay_1")
                print(int(order[i][1:]))
                self.move_front(float(order[i][1:]))
            elif order[i][0] == 'B': #뒤로 이동
                self.move_back(float(order[i][1:]))
	    else:
		break
	while(1):
	    print("waiting")
	    if(self.otp_flag == "start"):
		self.move(0,0)
		test_otp.MQTT_Subscriber()
		self.otp_flag = ""
		print("find")
		break




test = Turtlebot_move()
