#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
from std_msgs.msg import Int32MultiArray, String
import time
from geometry_msgs.msg import Twist
from tf.transformations import euler_from_quaternion, quaternion_from_euler
from nav_msgs.msg import Odometry
import math



def callback(msg):
	
	print(msg)
	print(msg.data)




rospy.init_node('rotate_robot')

sub = rospy.Subscriber ('/test', String, callback)
ack_publisher = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
pub = rospy.Publisher('cmd_vel', Twist, queue_size=1)
r = rospy.Rate(50)
command =Twist()
time.sleep(2)
rospy.spin()
dis = 1
turn = 1


#[ERROR] [1600248083.752708]: Message type std_msgs/String does not have a field load


