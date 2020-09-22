#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
from std_msgs.msg import String

from rospy_message_converter import message_converter


def callback(msg):
	print(msg)


rospy.init_node('test_robot', anonymous=True)

sub = rospy.Subscriber('/test', String , callback)

rospy.spin()

