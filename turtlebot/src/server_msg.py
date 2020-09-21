#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
from std_msgs.msg import Int32MultiArray
import time
from geometry_msgs.msg import Twist
from tf.transformations import euler_from_quaternion, quaternion_from_euler
from nav_msgs.msg import Odometry
import math

LINEAR = 0.1

roll = pitch = yaw = 0.0
current_degree = 0
position_x = 0
position_y = 0
kp=1

course ="r/12"

def move(linear, angular):
	twist = Twist()
	twist.linear.x = linear
	twist.angular.z = angular

	ack_publisher.publish(twist)

def callback(msg):

	global roll, pitch, yaw, position_x, position_y
	orientation_q = msg.pose.pose.orientation
	position_x = msg.pose.pose.position.x
	position_y = msg.pose.pose.position.y
	orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
	(roll, pitch, yaw) = euler_from_quaternion (orientation_list)
	print(position_x)

def callback2(msg):

	global course
	txt = "r/12/l/13"
	course = txt.split("/")
	print(course)

	




def move_go(dis):
	global position_x, position_y
	for i in range(dis):
		current_position_x = position_x
		current_position_y = position_y
		if(current_degree == 0):
			while not rospy.is_shutdown():
				move(0.02, 0)
				if(int(position_x * 100) == int((current_position_x + 0.1) * 100)):
					move_stop()
					break
		elif(current_degree == -90):
			while not rospy.is_shutdown():
				move(0.02, 0)
				if(int(position_y * 100) == int((current_position_y - 0.1) * 100)):
					move_stop()
					break
		elif(current_degree == 90):
			while not rospy.is_shutdown():
				move(0.02, 0)
				if(int(position_y * 100) == int((current_position_y + 0.1) * 100)):
					move_stop()
					break
		elif(current_degree == 180):
			while not rospy.is_shutdown():
				move(0.02, 0)
				if(int(position_x * 100) == int((current_position_x - 0.1) * 100)):
					move_stop()
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
		print("taeget={} current:{}", current_degree, yaw)
		print(command.angular.z)
		r.sleep()
		if (int(command.angular.z * 100) == 0):
			break
	move_go(dis)

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
	move_go(dis)

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
	move_go(dis)


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
	move_go(dis)


def move_stop(): #정지
	move(0,0)


rospy.init_node('rotate_robot')

sub = rospy.Subscriber ('/odom', Odometry, callback)
server_sub = rospy.Subscriber ('/odom', Odometry, callback2)

ack_publisher = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
pub = rospy.Publisher('cmd_vel', Twist, queue_size=1)
r = rospy.Rate(50)
command =Twist()
time.sleep(2)

dis = 1
turn = 1

while(1):
    dis = dis + 1




