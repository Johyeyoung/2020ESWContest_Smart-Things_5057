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
kp=0.5

def move(linear, angular):
	twist = Twist()
	twist.linear.x = linear
	twist.angular.z = angular
	ack_publisher.publish(twist)

def callback(msg):
    global roll, pitch, yaw
    orientation_q = msg.pose.pose.orientation
    orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
    (roll, pitch, yaw) = euler_from_quaternion (orientation_list)



def turn_left(): #왼쪽으로 90도 만큼 회전
	global current_degree
	current_degree = current_degree + 90
	while not rospy.is_shutdown():
		# quat = quaternion_from_euler (roll, pitch,yaw)
		# print quat
		target_rad = current_degree * math.pi / 180
		command.angular.z = kp * (target_rad - yaw)
		pub.publish(command)
		print("taeget={} current:{}", current_degree, yaw)
		print(command.angular.z)
		r.sleep()
		if (int(command.angular.z * 100) == 0):
			move_stop()
			break


def turn_right(): #오른쪽으로 90도 만큼 회전
	global current_degree
	current_degree = current_degree - 90
	while not rospy.is_shutdown():
		# quat = quaternion_from_euler (roll, pitch,yaw)
		# print quat
		target_rad = current_degree * math.pi / 180
		command.angular.z = kp * (target_rad - yaw)
		pub.publish(command)
		print("taeget={} current:{}", current_degree , yaw)
		print(command.angular.z)
		r.sleep()
		if (int(command.angular.z * 100) == 0):
			move_stop()
			break

def move_stop():
	move(0,0)


rospy.init_node('rotate_robot')

sub = rospy.Subscriber ('/odom', Odometry, callback)
ack_publisher = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
pub = rospy.Publisher('cmd_vel', Twist, queue_size=1)
r = rospy.Rate(10)
command =Twist()
time.sleep(2)

turn_right()
turn_right()
turn_left()
turn_right()
