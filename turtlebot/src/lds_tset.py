#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
from std_msgs.msg import Int32MultiArray, String
import time
from geometry_msgs.msg import Twist
from tf.transformations import euler_from_quaternion, quaternion_from_euler
from nav_msgs.msg import Odometry
import math
from sensor_msgs.msg import LaserScan
import math
import json


global pose
global past
global past_num
global dot
global cnt
cnt = 0
dot = [0, 0]
past = [[0, 0]]
pose = [0, 0]
rospy.init_node('scan_values')
avg = []
front = 0

#Lider값 가공
def callback_lider(scan):

    global avg

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

    right = scan.ranges[270]
    left = scan.ranges[90]
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
    print(front)


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



def move(linear, angular):
	twist = Twist()
	twist.linear.x = linear
	twist.angular.z = angular

	ack_publisher.publish(twist)


def lds_move_test():
    global front
    current_front = front
    time.sleep(0.1)
    while(not rospy.is_shutdown()):
        move(0.1, 0)
        print(front - current_front)

        if(front - current_front <= -0.3 ):
            move(0,0)
            print("done")
            break



rospy.init_node('scan_values')
sub = rospy.Subscriber('scan', LaserScan, callback_lider)
ack_publisher = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
pub = rospy.Publisher('cmd_vel', Twist, queue_size=1)

time.sleep(0.5)
lds_move_test()


rospy.spin()
