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
from rospy_message_converter import message_converter
import test_otp



LINEAR = 0.1

roll = pitch = yaw = 0.0
current_degree = 0
position_x = 0
position_y = 0
kp=  0.3
recive_order = ""
avg = []
front = 0




class Turtlebot_move:
    def __init__(self):
	rospy.init_node('rotate_robot')
	sub_server = rospy.Subscriber('/test', String , callback_server)
	ack_publisher = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
	sub = rospy.Subscriber ('/odom', Odometry, callback)

	pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)
	r = rospy.Rate(50)
	command =Twist()
	rospy.sleep(2)


	recive_order = "G75/R44"
	order =recive_order.split("/")


	otp_client = tset_otp.MQTT_Subscriber("otp_start")


	start(order)


	rospy.spin()
	
#Lider값 가공
def callback_lider(scan):
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

    #average
    Front_avg = avge(Front)
    Left1_avg = avge(Left1)
    Left2_avg = avge(Left2)
    Left3_avg = avge(Left3)
    Left4_avg = avge(Left4)
    Right1_avg = avge(Right1)
    Right2_avg = avge(Right2)
    Right3_avg = avge(Right3)
    Right4_avg = avge(Right4)
    back_avg = avge(back)

    avg = [Front_avg, Left1_avg, Left2_avg, Left3_avg, Left4_avg, Right1_avg, Right2_avg, Right3_avg, Right4_avg, back_avg]

    global front
    front = scan.ranges[0]


    return avg;

#lider값 평균 구하기
def avge(arr):
    l = []
    for i in arr:
        if i == float("inf"):
            continue
        elif i == 0:
            continue
        else:
            l.append(i)
    #print(l)
    return sum(l)/(len(l)+0.01)





#서버로부터 터틀봇의 움직임을 받음
def callback_server(msg):

	global recive_order
	recive_order = msg


#터틀봇의 움직임을 받음
def callback(msg):

	global roll, pitch, yaw, position_x, position_y
	orientation_q = msg.pose.pose.orientation
	position_x = msg.pose.pose.position.x
	position_y = msg.pose.pose.position.y
	orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
	(roll, pitch, yaw) = euler_from_quaternion (orientation_list)

#앞으로 움직임(lds 센서를 보면서 좌우의 물체가 일정 가리와 가까워지면 그 반대 방향으로 이동)
def move(linear, angular):
	global avg
	twist = Twist()
	twist.linear.x = linear
	twist.angular.z = angular
	ack_publisher.publish(twist)


#터틀봇 기본 동작

def lds_move(dis):
    
    print("okay_2")

    global front
    dis = dis/100
    print(dis)
    print(type(dis))
    current_front = front

    while(not rospy.is_shutdown()):
        time.sleep(0.01)
        move(0.05, 0)	
        print(front - current_front)

	if(front - current_front < -1 * 1.5 * dis):
		continue

        if(front - current_front <= -1*dis):
	    print(front - current_front)
            time.sleep(0.1)
	    move(0,0)	
            print("done")
            break





def move_front(dis): #정면으로  회전
	global current_degree

	current_degree = 0

	while not rospy.is_shutdown():
		# quat = quaternion_from_euler (roll, pitch,yaw)
		# print quat
		target_rad = 0 * math.pi / 180
		command.angular.z = kp * (target_rad - yaw)
		pub.publish(command)
		print("-------")
		print("taeget={} current:{}", current_degree, yaw)
		print(command.angular.z)
		print("------")
		r.sleep()
		if (int(command.angular.z * 100) == 0):
			break
	print(dis)
	print(type(dis))
	lds_move(dis)

def move_back(dis): #180 방향으로 회전

	global current_degree
	current_degree = 180

	while not rospy.is_shutdown():
		# quat = quaternion_from_euler (roll, pitch,yaw)
		# print quat
		target_rad = 180 * math.pi / 180
		command.angular.z = kp * (target_rad - yaw)
		pub.publish(command)
		print("taeget={} current:{}", current_degree, yaw)
		print(command.angular.z)
		r.sleep()
		if (int(command.angular.z * 100) == 0):
			break
	lds_move(dis)

def move_left(dis): #90도 방향으로 회전
	global current_degree
	current_degree =  90
	while not rospy.is_shutdown():
		# quat = quaternion_from_euler (roll, pitch,yaw)
		# print quat
		target_rad = 90 * math.pi / 180
		command.angular.z = kp * (target_rad - yaw)
		pub.publish(command)
		print("taeget={} current:{}", current_degree, yaw)
		print(command.angular.z)
		r.sleep()
		if (int(command.angular.z * 100) == 0):
			break
	lds_move(dis)


def move_right(dis): # -90도 방향으로 회전

	global current_degree
	current_degree =  -90

	while not rospy.is_shutdown():
		# quat = quaternion_from_euler (roll, pitch,yaw)
		# print quat
		target_rad = -90 * math.pi / 180
		command.angular.z = kp * (target_rad - yaw)
		pub.publish(command)
		print("taeget={} current:{}", current_degree , yaw)
		print(command.angular.z)
		r.sleep()
		if (int(command.angular.z * 100) == 0):
			break
	lds_move(dis)

def move_stop(): #정지
	move(0,0)

#json으로부터 입력받은 터틀봇의 움직임을 실행
def start(order):
	print(order)
	min_move = 0  
	#터틀봇 움직임의 최소 단위
	for i in range(len(order)):
		if order[i][0] == 'R':
			move_right(float(order[i][1:]))
		elif order[i][0] == 'L':
			move_left(float(order[i][1:]))
		elif order[i][0] == 'G':
			print("okay_1")
			print(int(order[i][1:]))
			move_front(float(order[i][1:]))
		elif order[i][0] == 'B':

			move_back(float(order[i][1:]))



